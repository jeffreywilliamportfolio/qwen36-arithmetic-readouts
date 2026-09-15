#!/usr/bin/env python3
"""Download pinned evidence, verify SHA-256, and extract the raw reads.

Uses only the Python standard library. --lens also downloads the 3.25 GB
five-prompt checkpoint; ordinary offline rescoring needs only the raw archive.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def fetch(repo, revision, entry):
    path = ROOT / entry['path']
    if path.is_file() and sha(path) == entry['sha256']:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    url = f'https://huggingface.co/datasets/{repo}/resolve/{revision}/{entry["path"]}'
    temp = path.with_suffix(path.suffix + '.part')
    print('Downloading', entry['path'], flush=True)
    with urllib.request.urlopen(url, timeout=120) as response, temp.open('wb') as f:
        shutil.copyfileobj(response, f, length=8 << 20)
    if sha(temp) != entry['sha256']:
        temp.unlink()
        raise SystemExit('Download checksum mismatch: ' + entry['path'])
    temp.replace(path)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'evidence')
    parser.add_argument('--lens', action='store_true')
    args = parser.parse_args()
    release = json.loads((ROOT / 'provenance/release.json').read_text())
    if not release['hf_revision'] or len(release['hf_revision']) != 40:
        raise SystemExit('A pinned 40-character dataset revision is required')
    artifacts = json.loads((ROOT / 'provenance/artifacts.json').read_text())
    archive = fetch(release['hf_repo'], release['hf_revision'], artifacts['raw_reads'])
    expected = {r['path']: r for r in json.loads((ROOT / 'provenance/evidence_files.json').read_text())}
    args.out.mkdir(parents=True, exist_ok=True)
    seen = set()
    with tarfile.open(archive, 'r:gz') as t:
        for member in t:
            name = PurePosixPath(member.name)
            if (not member.isfile() or name.is_absolute() or '..' in name.parts
                    or member.name not in expected or member.name in seen):
                raise SystemExit('Unexpected archive member')
            dest = args.out.joinpath(*name.parts)
            if not dest.resolve().is_relative_to(args.out.resolve()):
                raise SystemExit('Archive output escapes the evidence directory')
            dest.parent.mkdir(parents=True, exist_ok=True)
            with t.extractfile(member) as source, dest.open('wb') as f:
                shutil.copyfileobj(source, f)
            if sha(dest) != expected[member.name]['sha256']:
                raise SystemExit('Extracted file checksum mismatch: ' + member.name)
            seen.add(member.name)
    if seen != set(expected):
        raise SystemExit('Archive is missing expected observations')
    print('Verified and extracted', len(seen), 'evidence files to', args.out)
    if args.lens:
        if release.get('checkpoint_available') is False:
            raise SystemExit('Raw evidence is ready. The lens checkpoint upload is still in progress; update this checkout before using --lens.')
        fetch(release['hf_repo'], release['hf_revision'], artifacts['pile5_lens'])
        print('Verified the five-prompt checkpoint')


if __name__ == '__main__':
    main()
