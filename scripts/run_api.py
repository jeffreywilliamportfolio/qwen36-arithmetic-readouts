#!/usr/bin/env python3
"""Replay the 210 recorded raw-token requests. Set NEURONPEDIA_API_KEY to capture.

No tokenizer download is needed: data/prompts.jsonl contains the original input IDs.
Dry run validates requests without contacting the service. The service may evolve;
offline scoring of saved responses is the exact reproduction path.
"""
import argparse
import json
import os
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = 'https://www.neuronpedia.org/api/lens/prompt'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'evidence/v2_api/raw_A')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    prompts = [json.loads(line) for line in (ROOT / 'data/prompts.jsonl').read_text().splitlines()]
    if args.limit is not None:
        if args.limit < 1:
            parser.error('limit must be positive')
        prompts = prompts[:args.limit]
    key = os.environ.get('NEURONPEDIA_API_KEY')
    if not args.dry_run and not key:
        parser.error('NEURONPEDIA_API_KEY is required for a live capture')
    if not args.dry_run:
        args.out.mkdir(parents=True, exist_ok=True)
    for prompt in prompts:
        body = dict(modelId='qwen3.6-27b', inputTokenIds=prompt['input_ids'],
                    type=['JACOBIAN_LENS'], topN=8, temperature=0, numCompletionTokens=0,
                    filterNonWordTokens=False, stream=False, enableThinking=False, prependBos=True)
        if args.dry_run:
            continue
        name = f"{prompt['set']}_{prompt['name']}_{prompt['variant']}.json"
        path = args.out / name
        if path.exists():
            continue
        request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(),
            headers={'Content-Type': 'application/json', 'x-api-key': key}, method='POST')
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
        if not result.get('tokens'):
            raise RuntimeError('Response contains no tokens; capture stopped')
        result['_item'] = prompt
        path.write_text(json.dumps(result, ensure_ascii=False) + '\n')
        print('Captured', name, flush=True)
        time.sleep(0.8)
    print('Validated' if args.dry_run else 'Completed', len(prompts), 'requests')


if __name__ == '__main__':
    main()
