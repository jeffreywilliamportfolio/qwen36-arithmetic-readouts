# Methods and reproduction

The experiment reads Jacobian-lens vocabulary projections at the final prompt token for 55 published order-of-operations items and 50 generated held-out items. Every item is also captured with its trailing space removed. The raw prompts use no chat template and no added BOS token. `data/prompts.jsonl` records every submitted token ID sequence.

## Readout and scoring

The local reader hooks the output residual of each of 64 decoder blocks. For a fitted source layer it computes `lm_head(final_norm(h @ J.T))`; the lens target and any later block are read without transport. The hosted lens has fitted matrices for blocks 0–62 and targets block 63. The five-prompt lens has matrices for blocks 0–61 and targets block 62. Layer numbers are zero-based. A prompt's final token and a transformer's penultimate block are separate coordinates.

The frozen scorer accepts digit strings, English number forms, and Chinese numerals, matched by `decoded_token.strip().lower()`. Its definitions are extracted verbatim into `data/synonyms.py`. A hit takes the minimum accepted rank over evaluated layers 0–62, excluding the model's final output layer 63. For the five-prompt lens this includes a direct read of target block 62; the report also gives the count restricted to its fitted sources 0–61. Only the first eight list entries per layer are used for API comparisons. Rank 99 represents an uncaptured rank beyond that horizon. Local exact rank is `1 + count(logit > candidate_logit)` over the full output vocabulary; ties can therefore differ from list positions.

The baseline checks digits absent from the prompt, target, and intermediate. The paired sign test compares an item's intermediate rank to the median of its uninvolved-digit ranks, omits ties, and uses the two-sided exact binomial tail. Wrong-precedence decoys come from the held-out item records or the documented three-operand parser in `scripts/read_local.py`.

The held-out generator used seed 20260904, ten templates, integer operands 1–12, distinct positive intermediate/target/decoy values, and 25 single-digit plus 25 two-digit intermediates. Each two-digit item must have a reachable one-token spelling. The complete selection rules are saved in `data/items_new50.json`. No claim of generalization beyond this selection is required for the measurement comparison.

## Correctness and continuation gate

Primary correctness uses the first number in the local greedy continuation, up to six new tokens. The strict gate uses ten sampled continuations at temperature 0.8, top-p 0.95, and a 32-token limit, with a separate CUDA generator seeded 0–9 for each row. An item passes when at least eight samples begin numerically with the target and none of the ten samples or the greedy continuation contains the intermediate before the target.

The offline scorer independently reparses signed integers, decimals, and the English number forms used by the recorded parser. On the released data, it agrees with all 105 stored correctness flags and all 105 strict-gate flags. This check does not make the finite continuation gate an exhaustive test of every possible verbalization or language.

The initial API chat-template correctness arm and 74 partial API sampling records are preserved as auxiliary evidence. They are not used instead of the complete local trailing-space gate. The separate `v2_box_full` directory contains 105 space and five no-space sampled captures; the primary `v2_box` directory contains all 210 variants with greedy continuations.

## Offline reproduction

```bash
python3 scripts/fetch_evidence.py
python3 analysis/score.py --check --out recomputed
```

The scorer uses only Python 3.10+ and the standard library. It verifies the raw-file inventory, reads the API and local observations, recomputes the per-item flags and metrics, and compares them with `results/summary.json` and `results/per_item.jsonl`. It makes no network calls. The downloader pins a Hugging Face commit and validates checksums.

## Fresh API captures

```bash
python3 scripts/run_api.py --dry-run
export NEURONPEDIA_API_KEY='your-key'
python3 scripts/run_api.py --out fresh-api/raw_A
```

The API replay uses the exact recorded token IDs, topN 8, zero generated tokens, greedy temperature, and the raw-token endpoint. A live hosted service may change. Exact reproduction of the published measurements uses the saved responses rather than an assumption that future calls will be identical. API credentials are read from the environment.

## Fresh local captures and lens fitting

The recorded environment used PyTorch 2.11.0+cu128, transformers 5.14.1, CUDA 12.8, and an NVIDIA RTX PRO 6000 Blackwell Workstation Edition. `requirements-gpu.txt` records the Python dependencies and pins the Jacobian-lens source commit. Use a compatible Linux CUDA environment and sufficient memory for the approximately 54 GB bf16 model plus activations and Jacobian matrices.

```bash
python3 -m pip install -r requirements-gpu.txt
python3 scripts/fetch_evidence.py --lens
python3 scripts/fit_pile_lens.py --dry-run
```

Download a local `Qwen/Qwen3.6-27B` snapshot. Separately download the hosted checkpoint from `neuronpedia/jacobian-lens`, path `qwen3.6-27b/jlens/Salesforce-wikitext/Qwen3.6-27B_jacobian_lens_n1000.pt`. Its recorded SHA-256 is `1718c8c52dd8a9dad03738d4d625937c1fbba10be325b872ed446c7290fc11e1`; check that hash before a comparison. The model configuration hash and weight-index hash are in `provenance/local_manifest.json`. The original capture did not record resolved weight revision or shard hashes, so those hashes alone do not establish the precise model-weight bytes.

```bash
python3 scripts/read_local.py \
  --model /path/to/model-snapshot \
  --lens-hosted /path/to/hosted_n1000.pt \
  --lens-pile5 lenses/qwen36_pile5.pt \
  --out fresh-local

python3 scripts/fit_pile_lens.py \
  --model /path/to/model-snapshot \
  --out fresh-fit --n-prompts 5 --dim-batch 4
```

`read_local.py` applies both lenses to the same captured residuals, writes top-8 lists at every prompt position, top-64 lists and exact ranks for specified candidates at the final position, and greedy/sampled continuations. It preserves the recorded continuation parser for capture parity; `analysis/score.py` provides the separate decimal-aware audit. Use `--dry-run` with a tokenizer to inspect prompt and synonym IDs without loading the model. The reader defaults to both position variants and sampled continuations; `--skip-sampling` matches the initial greedy-only local pass.

The fitter reads the bundled five calibration sequences directly, preserving all 128 IDs and avoiding a mutable corpus download. They are document indices 0, 1, 2, 4, and 5 in the recorded Pile subset, selected in row order from documents with at least 132 tokens. The upstream estimator skips the first four source positions and excludes the final position through its valid-position mask, targets block 62, and averages per-prompt Jacobians uniformly. The recorded run used the plain PyTorch autograd path, bf16 model weights, fp32 accumulation, and stored fp16 matrices. A new fit can use its own output directory and per-prompt resume checkpoint.

Only five calibration prompts and a finalized five-prompt lens are included. This package contains no 25-prompt result. Fitting time recorded by the finalization-only manifest is not the original training time; that distinction is explained in `PROVENANCE.md`.
