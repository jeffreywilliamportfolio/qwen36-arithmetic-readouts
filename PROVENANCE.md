# Provenance and release history

The observations were captured September 4–5, 2026 and independently rescored for publication. The source experiment had an exploratory first pass before the v2 preregistration. The initial v2 plan and subsequent addenda record when hypotheses, filters, controls, and the five-prompt compute cap were introduced. These stages should not be summarized as every decision having preceded every capture.

**The twelve frozen files, all 1,349 raw observation files, and the five-prompt lens checkpoint are published byte-identical to the preserved source records.** The publication scorer, portable wrappers, documentation, and derived result tables were assembled for publication. Archive directory aliases are described below; they do not alter the observation files' bytes.

## Frozen records

`provenance/frozen_sources.json` records the twelve frozen file hashes and their publication paths, plus the historical hash-list file. As of v1.0.1 all 12 files are published **byte-identical** to the frozen originals, together with the verbatim historical hash list (`preregistration/record/FREEZE.sha256`) and a strict-format derivation (`FREEZE.verify.sha256` at the repository root) that `shasum -a 256 -c` / `sha256sum -c` accepts; CI re-runs that verification on every push. Matching these hashes verifies the published files against the locally recorded freeze. It is not independent evidence of the claimed freeze time. The publication scorer and portable capture wrappers were assembled after the observations and are not presented as frozen v2 code.

Historical interpretation rules in the preregistration files are preserved as a record of the plan. In particular, the plan's assumption that a five-prompt lens must be weaker than a 25-prompt lens is not established by these data. Current claims and denominators are given in `RESULTS.md`.

## Original observation files

The release includes every saved v2 API/local JSON observation in the selected evidence directories: **1,349 files**. `provenance/evidence_files.json` records each file's SHA-256 and byte size. The archive contains the original saved file bytes, including historical metadata and path strings. The downloader verifies the archive checksum and every extracted file.

| Evidence directory | Files | Role |
| --- | ---: | --- |
| `v2_api/raw_A` | 210 | Main hosted API lens reads, both prompt variants |
| `v2_api/raw_B` | 105 | Auxiliary chat-template correctness captures |
| `v2_api/raw_C` | 74 | Partial auxiliary unseeded API sampling gate |
| `v2_box/hosted_n1000` | 210 | Local hosted lens reads |
| `v2_box/pile5` | 210 | Local five-prompt lens reads |
| `v2_box/continuations` | 210 | Greedy-only initial local continuations |
| `v2_box_full/hosted_n1000` | 110 | Hosted reads accompanying sampled captures |
| `v2_box_full/pile5` | 110 | Five-prompt reads accompanying sampled captures |
| `v2_box_full/continuations` | 110 | Complete 105-item trailing-space gate plus five no-space cases |

The archive uses `pile5` as the directory alias for the five-prompt lens. The original capture directory and checkpoint prefix used a historical label ending in `25`; the actual five-prompt fit is documented in `preregistration/record/PREREG_orderops_v2_ADDENDUM5.md`. File contents retain the original labels and paths.

The original 55-item JSON is byte-identical to the upstream evaluation file at `anthropics/jacobian-lens` commit `581d398613e5602a5af361e1c34d3a92ea82ba8e`. The held-out item file and its selection rules are also preserved. The five calibration sequences and text fingerprints appear in `calibration/prompts.json`.

## Checkpoint and environment

The five-prompt lens is the original checkpoint, SHA-256 `fd9af5fdb7322c9559e7a4702a845c7db0d92f780e53fdf415df899e065e0022`, matching the frozen v2 capture manifest. `provenance/checkpoint.json` preserves the per-entry payload hashes and the earlier ZIP-prefix transformation record. All 68 uncompressed entry payloads were verified unchanged when the original checkpoint was restored in v1.0.1.

The checkpoint contains 62 fp16 matrices of shape 5120 × 5120, fitted from five prompts, with source blocks 0–61 and target block 62. It uses the upstream tensor-dictionary format and can be loaded with `torch.load(..., weights_only=True)`. There is no saved resumable fitting accumulator in this release.

Capture manifests record the model configuration SHA-256, weight-index SHA-256, lens hashes, software versions, GPU, tokenization policy, and exact-rank convention. The resolved model revision and model shard hashes were not captured. The bootstrap's expected revision is therefore recorded as an expectation, not proof of the exact weights used. Host file paths retained in historical manifests describe the original environment; portable commands are in `METHODS.md`.

The fitted-lens manifest was written during checkpoint finalization: its 25-second elapsed value and zero-second per-prompt entries describe that finalization invocation. They are not measurements of fitting cost. No new compute-time or rental-price estimate is asserted by this release.

## Reproduction and audit records

The [GitHub reproduction workflow](https://github.com/jeffreywilliamportfolio/qwen36-arithmetic-readouts/actions/workflows/reproduce.yml) verifies the twelve frozen hashes, downloads and verifies the pinned observations, and independently recomputes all 105 item rows and every published aggregate. API request construction and bundled calibration loading are checked with dry runs. The checkpoint was checked through its archive payloads and a safe PyTorch tensor-dictionary load in the earlier audit. The release does not claim a fresh API or GPU replication of the experiment.

`provenance/validation.json` retains the original publication audit and later version-specific updates. Its original top-level fields describe v1.0.0; the subsequent update blocks describe later releases. The v1.0.1 artifact, evidence-file, and release manifests are preserved under `provenance/history/v1.0.1/`, including the original/released hash pairs for the formerly normalized observation files. These historical manifests are not the current downloader inputs.

The current downloader uses the HF artifact commit pinned in `provenance/release.json`. The v1.0.2 tags identify the aligned documentation and metadata on [GitHub](https://github.com/jeffreywilliamportfolio/qwen36-arithmetic-readouts/releases/tag/v1.0.2) and [Hugging Face](https://huggingface.co/datasets/ec75hash/qwen36-arithmetic-readouts/tree/v1.0.2). The dataset carries the large artifacts; GitHub carries the report, code, item tables, checksums, and audit records.

## Release history

- **v1.0.0** (2026-09-14): initial publication. Six of the twelve frozen files were published as normalized renderings, with separate original and published hashes. Observation files retained their numerical payloads with lens-identity/path metadata normalization. The lens checkpoint used a renamed ZIP entry prefix with unchanged uncompressed payloads.
- **v1.0.1** (2026-09-14): all twelve frozen files and the original checkpoint were restored byte-identical. The historical `FREEZE.sha256`, strict-format `FREEZE.verify.sha256`, and CI freeze verification were added. The raw observations remained normalized. GitHub's v1.0.0/v1.0.1 history and the historical audit records remain available.
- **HF artifact refresh** (2026-09-14): [artifact commit `ddf3417`](https://huggingface.co/datasets/ec75hash/qwen36-arithmetic-readouts/tree/ddf3417b9058af55ab2f02c3629d55c2becc06cf) restored the original bytes of all 1,349 observation files. HF's visible history restarted from a new initial commit; the former artifact pin `23081127dc542b2dbec3d76ae586f9e53b990dea` returned HTTP 404 during the alignment check. This temporarily broke the previous GitHub downloader. The refresh's archive checksum is `d1588433a1e5e08b5fd344abdc8d89822b845b35deebe894ef49e8c2ab1a47e6`.
- **v1.0.2** (2026-09-14): GitHub and HF use the same current artifact pin, checksums, observation inventory, documentation, and citation version. The chronology distinguishes the initial plan from subsequent addenda, and the byte-identity claim names the original artifacts explicitly. Earlier audit records are retained. Measurement values and scoring code are unchanged; only the result summary's file-size inventory changes with the restored observation bytes.
