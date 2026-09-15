#!/usr/bin/env python3
"""Fit a Jacobian lens from the exact bundled calibration token IDs.

The recorded checkpoint used five 128-token prompts, skip_first=4, target block
62 of 64, standard estimator, uniform weighting, bf16 model weights, and
dim_batch=4. This runner uses the recorded upstream library revision; see METHODS.md.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='Qwen/Qwen3.6-27B')
    parser.add_argument('--calibration', type=Path, default=ROOT / 'calibration/prompts.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'fit-output')
    parser.add_argument('--n-prompts', type=int, default=5)
    parser.add_argument('--dim-batch', type=int, default=4)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    all_prompts = json.loads(args.calibration.read_text())['prompts']
    if not 1 <= args.n_prompts <= len(all_prompts):
        parser.error('n-prompts must be between 1 and the number of supplied calibration prompts')
    prompts = all_prompts[:args.n_prompts]
    for prompt in prompts:
        ids = prompt['input_ids']
        if len(ids) != 128 or not all(isinstance(i, int) and 0 <= i < 248320 for i in ids):
            parser.error('each calibration prompt must contain exactly 128 valid integer token IDs')
    spec = dict(calibration_sha256=sha(args.calibration), n_prompts=len(prompts),
                doc_indices=[p['doc_index'] for p in prompts], max_seq_len=128,
                skip_first=4, target_layer=62, dim_batch=args.dim_batch,
                model=args.model, dtype='bfloat16', estimator='standard', weighting='uniform')
    print(json.dumps(spec, indent=2), flush=True)
    if args.dry_run:
        return
    for module in ('fla', 'flash_linear_attention', 'causal_conv1d'):
        if importlib.util.find_spec(module) is not None:
            raise SystemExit(f'Recorded fitting uses plain autograd; use an environment without {module}')

    import torch
    import jlens
    from jlens.hf import HFLensModel
    from transformers import AutoTokenizer
    from read_local import load_text_model, verify_capture

    args.out.mkdir(parents=True, exist_ok=True)
    spec_path = args.out / 'fit_spec.json'
    if spec_path.exists() and json.loads(spec_path.read_text()) != spec:
        raise SystemExit('Existing fit spec differs; choose a fresh output directory')
    spec_path.write_text(json.dumps(spec, indent=2) + '\n')
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.bos_token_id is not None:
        raise SystemExit('This protocol expects the recorded tokenizer with no BOS token')
    model = load_text_model(args.model, torch.bfloat16)
    token_map = {f'calibration:{p["doc_index"]}': p['input_ids'] for p in prompts}

    class PreTokenized(HFLensModel):
        def encode(self, text, *, max_length=512):
            return torch.tensor([token_map[text][:max_length]], dtype=torch.long, device=self.input_device)

    lm = PreTokenized(model, tokenizer, compile=False)
    if lm.n_layers != 64 or lm.d_model != 5120:
        raise SystemExit('Expected 64 decoder blocks and hidden width 5120')
    capture = verify_capture(lm, tokenizer)
    start = time.monotonic()
    lens = jlens.fit(lm, list(token_map), target_layer=-2, dim_batch=args.dim_batch,
                     max_seq_len=128, skip_first=4,
                     checkpoint_path=str(args.out / 'fit_ckpt.pt'), checkpoint_every=1, resume=True)
    output = args.out / f'qwen36_pile{len(prompts)}.pt'
    lens.save(str(output))
    spec.update(n_prompts_fitted=lens.n_prompts, source_layers=lens.source_layers,
                capture_check=capture, invocation_seconds=time.monotonic() - start,
                torch=torch.__version__, cuda=torch.version.cuda,
                gpu=torch.cuda.get_device_name(0), lens_sha256=sha(output), lens_bytes=output.stat().st_size)
    (args.out / 'provenance.json').write_text(json.dumps(spec, indent=2) + '\n')
    print('Saved', output, flush=True)


if __name__ == '__main__':
    main()
