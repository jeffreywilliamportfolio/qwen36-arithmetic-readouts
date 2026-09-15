---
language:
  - en
  - zh
license: apache-2.0
task_categories:
  - other
pretty_name: Arithmetic Intermediate Readout Sensitivity on Qwen3.6-27B
size_categories:
  - n<1K
tags:
  - interpretability
  - arithmetic
  - jacobian-lens
  - reproducibility
  - qwen
configs:
  - config_name: item_results
    default: true
    data_files:
      - split: test
        path: results/per_item.jsonl
  - config_name: prompt_tokens
    data_files:
      - split: test
        path: data/prompts.jsonl
---

# Arithmetic Intermediate Readout Sensitivity on Qwen3.6-27B

**Arithmetic intermediate detection with a Jacobian lens depends sharply on the prompt token being read and the numeral forms accepted by the scorer.** Across 105 order-of-operations items, the recorded hosted-lens responses contain the intermediate at rank 1 on **48 items at the trailing space**, versus **4 at the preceding token**. On the 25 held-out items with two-digit intermediates, rank-1 detection falls from **13 to 3** when Chinese numerals are removed from the synonym set. A separately fitted five-prompt lens also shows both sensitivities.

[GitHub: code and report](https://github.com/jeffreywilliamportfolio/qwen36-arithmetic-readouts) · [Hugging Face: evidence and checkpoint](https://huggingface.co/datasets/ec75hash/qwen36-arithmetic-readouts) · [Full results](RESULTS.md) · [Methods](METHODS.md) · [Provenance](PROVENANCE.md)

Release **v1.0.2**: [GitHub release](https://github.com/jeffreywilliamportfolio/qwen36-arithmetic-readouts/releases/tag/v1.0.2) · [HF release snapshot](https://huggingface.co/datasets/ec75hash/qwen36-arithmetic-readouts/tree/v1.0.2) · [Reproduction CI](https://github.com/jeffreywilliamportfolio/qwen36-arithmetic-readouts/actions/workflows/reproduce.yml)

The package contains the original 55 evaluation items, 50 held-out items, 210 exact prompt-token sequences, 105 scored item rows, **1,349 raw evidence files**, a CPU scorer, capture and fitting scripts, historical preregistration records, checksums, and the **five-prompt** lens checkpoint. The raw archive and checkpoint are hosted on Hugging Face; the ordinary GitHub clone stays small.

| Set and readout | Rank 1 | Rank ≤ 3 |
| --- | ---: | ---: |
| Original 55 items, hosted API lens | 24/55 (43.6%) | 41/55 (74.5%) |
| Held-out 50, hosted API lens | 24/50 (48.0%) | 36/50 (72.0%) |
| All 105, hosted API lens | 48/105 (45.7%) | 77/105 (73.3%) |
| All 105, local hosted lens, exact ranks | 48/105 (45.7%) | 77/105 (73.3%) |
| All 105, local five-prompt lens, exact ranks | 45/105 (42.9%) | 60/105 (57.1%) |

A hit means that an accepted **single-token spelling** of the intermediate reaches the specified rank at **at least one evaluated layer, 0–62**, at the final prompt token. For the five-prompt lens, layer 62 is a direct read of its target block; [RESULTS.md](RESULTS.md) also reports the fitted-source-only count. This is a vocabulary readout measurement. It does not establish which language the model computes in or that the intermediate is causally necessary.

The preregistered replication result is mixed: the correctly answered original items reach 16/47 (34.0%) at rank 1, below the registered 35% threshold. The strict sampled-continuation filter admits only 24/105 items, below the required 30, so that column cannot test the planned H1/H2 conclusions. Those outcomes are reported alongside the measurement sensitivities in [RESULTS.md](RESULTS.md).

## Reproduce the published numbers

Python 3.10+ is sufficient. This path uses the standard library and downloads an approximately 86 MB compressed archive; it requires no model, GPU, account, or API key.

```bash
git clone https://github.com/jeffreywilliamportfolio/qwen36-arithmetic-readouts.git
cd qwen36-arithmetic-readouts
python3 scripts/fetch_evidence.py
python3 analysis/score.py --check --out recomputed
```

The downloader pins the dataset revision in `provenance/release.json`, checks the archive SHA-256, and verifies every extracted file. The scorer independently aggregates those observations and compares every published item row and aggregate with the release tables.

To verify the preregistration freeze, run `shasum -a 256 -c FREEZE.verify.sha256` (macOS) or `sha256sum -c FREEZE.verify.sha256` (Linux) from the repository root: twelve `OK` lines confirm the published plan, addenda, runners, scorer, and item files are byte-identical to the locally recorded September 4 hash list. See [`preregistration/README.md`](preregistration/README.md). CI re-runs both checks on every push.

To also download the fitted lens, add `--lens` to the fetch command. It downloads approximately 3.25 GB. New model captures and fitting are described in [METHODS.md](METHODS.md); their numerical implementation follows the recorded pipeline, while their publication wrappers were checked with dry runs. No new GPU experiment was performed for this release.

## Dataset layout and interpretation

The `item_results` viewer contains one row per item. `group="paper"` identifies the original 55; `group="new"` identifies the held-out 50. `rank`, `no_space_rank`, and `no_cjk_rank` use the hosted API's top-8 lists, with **99 meaning absent from the captured top 8**, not a measured exact rank. `hosted_n1000_rank` and `pile5_rank` use local exact ranks. `correct_*` and `admissible_*` distinguish recorded flags from an independent continuation reparse. The `prompt_tokens` viewer contains the two prompt variants and their exact input IDs.

| Path | Contents |
| --- | --- |
| `data/` | Evaluation items, frozen synonym definitions, exact prompt IDs |
| `results/` | All item rows and machine-readable aggregates |
| `analysis/score.py` | Independent offline aggregation and checks |
| `scripts/` | Pinned downloader, API replay, local reader, five-prompt fitter |
| `calibration/prompts.json` | The five exact 128-token calibration sequences |
| `preregistration/` | Byte-identical frozen v2 records and their hash lists |
| `provenance/` | Capture manifests, per-file evidence hashes, release pins, and historical audit records |
| `artifacts/raw_reads.tar.gz` | Complete saved v2 observations, on Hugging Face |
| `lenses/qwen36_pile5.pt` | Five-prompt Jacobian lens, on Hugging Face |

The held-out set was generated before its v2 captures, with seed 20260904, and deliberately requires at least one single-token route for each two-digit intermediate. Its performance should be interpreted for that reachable-item population. The release includes partial auxiliary API sampling records (74/105 items); the primary local sampling gate covers all 105 trailing-space prompts.

The original evaluation items and Jacobian-lens implementation come from [anthropics/jacobian-lens at the recorded revision](https://github.com/anthropics/jacobian-lens/tree/581d398613e5602a5af361e1c34d3a92ea82ba8e). The hosted checkpoint is distributed through [neuronpedia/jacobian-lens](https://huggingface.co/neuronpedia/jacobian-lens). This release is Apache-2.0 within the scope described in [NOTICE](NOTICE); calibration source material and external model dependencies retain their own rights.

Author: Jeffrey W. Shorthill. Captures: September 4–5, 2026. Offline audit and publication: September 14, 2026.
