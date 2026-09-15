# Results

**Two measurement choices strongly change arithmetic intermediate detection: prompt-token position and accepted numeral forms.** The effect appears in both API and local hosted-lens reads, and both sensitivities recur with a separately fitted five-prompt lens. All numbers below are recomputed from the released observations by `analysis/score.py`; the complete item-level record is `results/per_item.jsonl`.

## Intermediate detection

| Hosted API readout | Rank 1 | Rank ≤ 3 |
| --- | ---: | ---: |
| Original paper items | 24/55 (43.6%) | 41/55 (74.5%) |
| Held-out items | 24/50 (48.0%) | 36/50 (72.0%) |
| Pooled | 48/105 (45.7%) | 77/105 (73.3%) |

The original-item uninvolved-digit baseline is 22/298 (7.38%) at rank 1; pooled it is 35/548 (6.39%). These are counts over item–digit comparisons. The paired sign test compares each item's intermediate rank against the median rank of its uninvolved digits. For the original 55, there are 42 wins, 12 losses, and one tie; the two-sided exact sign-test p-value is **0.0000520945**. The intermediate has multiple accepted spellings, while the baseline checks digit spellings only, so this is not a candidate-set-matched null.

The held-out values are similar to the original values. They describe a set designed to contain reachable single-token intermediate forms; they do not estimate performance on arbitrary arithmetic expressions.

## Position and numeral-form sensitivity

| Comparison | Rank-1 detections |
| --- | ---: |
| All items, final trailing-space token | 48/105 |
| All items, previous token within the same prompt | 4/105 |
| All items, final token after deleting the trailing space | 4/105 |
| Held-out two-digit intermediates, digits + English + Chinese | 13/25 |
| Same two-digit items, digits + English | 3/25 |
| Held-out single-digit intermediates, either synonym set | 11/25 |

For all 105 items, the previous-token ranks within the full prompt match the corresponding ranks after deleting its trailing space. The earlier token is an equals marker: 97 prompts use `=` and eight use the word `equals`. This supports a strong position sensitivity, rather than a claim that the value is detectable at only one position in every context.

The tokenizer encodes `23` as separate digit IDs `[17, 18]`, while `二十三` is one token, ID `131734`. Accepted Chinese numeral tokens therefore provide a route for two-digit values that digit-only scoring cannot credit. Across both sets, 20 of the 22 two-digit rank-1 hits include a Chinese numeral at rank 1: 17 have Chinese alone among the spelling families, three have both Chinese and English, and two have English alone. These are readout spellings; they do not identify the language of an internal computation.

The strict admissible two-digit subset is small: removing Chinese numerals changes rank-1 hits from 4/12 to 2/12. That is exactly half, not below the original half-rate criterion. The larger 13-to-3 sensitivity is the held-out **unfiltered** result.

## Lens comparison and instrument agreement

| Local lens, all 105 items | Rank 1 | Rank ≤ 3 |
| --- | ---: | ---: |
| Hosted 1000-prompt lens | 48 | 77 |
| Five-prompt Pile lens | 45 | 60 |

Using exact local ranks, the five-prompt lens reaches **93.75% of the hosted lens's rank-1 count** and **77.92% of its rank-3 count**. The rank-1 item overlap is 35, so these percentages are ratios of counts, not percentages of the same hits retained. With the five-prompt lens, removing the trailing space changes rank-1 hits from 45 to 4; excluding Chinese numerals changes the held-out two-digit count from 13 to 3.

The hosted lens transports blocks 0–62 to block 63. The five-prompt lens transports blocks 0–61 to block 62; block 62 is read directly. Restricting the five-prompt analysis to its fitted Jacobian source layers alone gives 43/105 rank-1 hits. Thus the comparison changes both calibration data and target block. The results show that the reported sensitivities survive this alternate lens. They do not establish monotonic improvement with more fitting prompts, rule out all lens-quality explanations, or constitute a 25-prompt experiment.

The API and local hosted top-8 readouts agree on rank-1 hit status for 104/105 items. The local top-8 list has 47 rank-1 hits, whereas its exact-rank calculation has 48: exact ranks count only strictly greater logits, while list positions break ties. The five-prompt counts are 44 by list position and 45 by exact rank. The release records both conventions instead of treating them as interchangeable.

## Registered outcomes and output controls

On the correctly answered original items, rank 1 is **16/47 (34.0%)**, one item below the preregistered 35% bar; rank ≤ 3 is **33/47 (70.2%)**. Under the original H1 rule, that is “does not replicate as scored.” The strict gate requires at least eight of ten sampled continuations to assert the target and no sampled or greedy continuation to emit the intermediate before the target. It admits **24/105 items**: 12 original and 12 held out. Because the plan required 30, H1/H2 are **not testable as designed** in the designated strict column. Within those 24, the observed counts are 8 at rank 1 and 15 at rank ≤ 3; they remain descriptive.

Of the 48 pooled rank-1 hits, **24** also place the intermediate in the model's final-layer top-8 next tokens. Of the 77 rank-3 hits, **30** are absent from that final-layer top 8. This is an output-distribution control, not evidence that an ordinary logit lens at every earlier layer would miss the intermediate, or that it could never appear in a continuation.

A wrong-precedence decoy can be defined for 67 items. The intermediate beats it on 49, loses on eight, and ties on ten: **49/57 (86.0%) among non-ties**, or 49/67 (73.1%) of all decoy-bearing items. The denominator matters.

The supported contribution is a reproducible account of measurement sensitivity on this model, with a mixed outcome under the stricter registered replication criteria. These data do not identify the cause of an unobserved external pipeline's result.
