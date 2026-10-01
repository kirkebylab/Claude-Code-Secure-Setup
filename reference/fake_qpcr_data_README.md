# fake_qpcr_data.csv

**This is fake data.** Every number was simulated by a script. Nothing here was
measured, and no real cells, donors, or patients are involved. It is safe to
share, upload, and analyze.

## The pretend experiment

Human stem-cell-derived neurons were stimulated for 1 hour with one of four
treatments, then RNA was collected and three activity-dependent genes were
measured by qPCR.

| Group       | Treatment                                    | Samples |
| :---------- | :------------------------------------------- | :-----: |
| `ctrl`      | Vehicle only                                 |    6    |
| `KCl`       | Potassium chloride (depolarizes the neurons) |    6    |
| `BDNF`      | Brain-derived neurotrophic factor            |    6    |
| `forskolin` | Forskolin (raises cAMP)                      |    6    |

Each sample is a separate culture well. Each sample was measured for four
genes, and each gene was run in three technical replicate wells on the plate.

## Columns

| Column      | Meaning                                                     |
| :---------- | :---------------------------------------------------------- |
| `sample`    | Sample ID (`S01` to `S24`), one per culture well            |
| `group`     | Treatment group: `ctrl`, `KCl`, `BDNF`, or `forskolin`      |
| `gene`      | `FOS`, `ARC`, `NPAS4` (targets) or `GAPDH` (reference gene) |
| `replicate` | Technical replicate number: 1, 2, or 3                      |
| `Ct`        | Cycle threshold. Lower Ct means more of that transcript     |

One row is one qPCR well: 24 samples x 4 genes x 3 replicates = 288 rows.

## Questions to try

- Describe the dataset: what are the variables, groups, and group sizes?
- Which genes change with each treatment, compared with `ctrl`?
- Which statistical test fits, and what does it assume?
- Use the ΔΔCt method with `GAPDH` as the reference gene to get fold changes.
- Plot the result with individual samples shown as points.
