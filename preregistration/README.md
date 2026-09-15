# Preregistration records

The twelve files covered by the locally recorded **September 4, 2026 (MDT)** hash list comprise the initial v2 preregistration, subsequent addenda, capture runners, scorer, and evaluation items. They are published **byte-identical** at the paths listed below. The addenda describe decisions made at the stages recorded in each document; this collection does not establish that every decision or file preceded every v2 capture. `record/FREEZE.sha256` is the historical hash list, also published verbatim.

The twelve files are the v2 plan (`PREREG_orderops_v2.md`), five addenda, three API runners, the frozen scorer (`score_orderops.py`), and the two evaluation item files (published at `data/order_ops.json` and `data/items_new50.json`).

## Verify

From the repository root:

```bash
shasum -a 256 -c FREEZE.verify.sha256    # macOS
sha256sum -c FREEZE.verify.sha256        # Linux
```

Twelve `OK` lines confirm that every published file matches its recorded freeze hash. `FREEZE.verify.sha256` is a strict-format derivation of `record/FREEZE.sha256`: it maps the historical entries to their repository paths, because the historical file lists bare filenames and carries a trailing inline note that standard `-c` parsing treats as part of the last filename. The two lists contain the same twelve hashes; `provenance/frozen_sources.json` records both.

The same CI workflow that rescores the published results re-runs this verification on every push.

## Reading these files

They are historical documents and are not edited, so they reflect their moment of writing:

- They refer to the target recipe from the July 6, 2026 [LessWrong review of the upstream paper](https://www.lesswrong.com/posts/zFJ3ZdQwrTWE9jT5S/a-review-of-anthropic-s-global-workspace-paper), whose reported arithmetic non-replication motivated this measurement.
- `PREREG_orderops_v2_ADDENDUM5.md` documents, before any box result was read, the compute-cap change from a 25-prompt to a 5-prompt lens fit and the asymmetric interpretation rule for it. The plan's assumption that a 5-prompt lens is strictly weaker than a 25-prompt lens is an assumption, not something these data establish.
- One runner reads an API key from a private local environment file by path; the file itself was never part of the record and no credential appears here.
- The addenda record when hypotheses, filters, and controls were introduced; the sequence matters and is preserved. Current conclusions and denominators live in [`RESULTS.md`](../RESULTS.md).

The freeze was recorded locally and its hashes are self-attested as of the freeze date; matching them verifies the published files against that record, and `PROVENANCE.md` states what this does and does not establish.
