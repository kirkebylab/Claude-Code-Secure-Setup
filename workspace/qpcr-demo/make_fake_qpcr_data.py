"""Make a FAKE qPCR dataset for the data analysis demo.

Nothing in the output was measured. Every number is simulated, so the file is
safe to share, upload, and analyze in front of an audience.

The pretend experiment: human stem-cell-derived neurons, stimulated for 1 hour
with vehicle (ctrl), KCl, BDNF, or forskolin. Three activity-dependent genes
(FOS, ARC, NPAS4) plus the reference gene GAPDH, measured in technical
triplicate.

The data are clean: no duplicates, no missing values, no mixed units.

Run it with:  python3 make_fake_qpcr_data.py
"""

import csv
import random
from pathlib import Path

SEED = 2026  # same seed = same file every time
OUT = Path(__file__).parent / "fake_qpcr_data.csv"

GROUPS = ["ctrl", "KCl", "BDNF", "forskolin"]
SAMPLES_PER_GROUP = 6
TECH_REPS = 3
GENES = ["GAPDH", "FOS", "ARC", "NPAS4"]

# Typical Ct for each gene in unstimulated (ctrl) cells
BASELINE_CT = {"GAPDH": 18.2, "FOS": 27.6, "ARC": 28.4, "NPAS4": 31.0}

# The built-in "true" answer: change versus ctrl in log2 units (1 = doubling).
# More expression means a LOWER Ct, so these are subtracted from the Ct.
TRUE_LOG2FC = {
    "ctrl": {"FOS": 0.0, "ARC": 0.0, "NPAS4": 0.0},
    "KCl": {"FOS": 4.5, "ARC": 3.5, "NPAS4": 5.0},
    "BDNF": {"FOS": 3.0, "ARC": 2.5, "NPAS4": 0.0},
    "forskolin": {"FOS": 3.5, "ARC": 0.6, "NPAS4": 0.0},
}

# How noisy the data are, in Ct units
SAMPLE_INPUT_SD = 0.40  # sample-to-sample loading differences (hits every gene)
GENE_BIO_SD = {"GAPDH": 0.10, "FOS": 0.40, "ARC": 0.40, "NPAS4": 0.40}
TECH_SD = 0.08  # well-to-well pipetting noise


def main():
    rng = random.Random(SEED)
    rows = []
    sample_number = 0

    for group in GROUPS:
        for _ in range(SAMPLES_PER_GROUP):
            sample_number += 1
            sample = f"S{sample_number:02d}"

            input_shift = rng.gauss(0, SAMPLE_INPUT_SD)
            for gene in GENES:
                true_ct = (
                    BASELINE_CT[gene]
                    - TRUE_LOG2FC[group].get(gene, 0.0)
                    + input_shift
                    + rng.gauss(0, GENE_BIO_SD[gene])
                )
                for rep in range(1, TECH_REPS + 1):
                    ct = round(true_ct + rng.gauss(0, TECH_SD), 2)
                    rows.append([sample, group, gene, rep, f"{ct:.2f}"])

    with open(OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "group", "gene", "replicate", "Ct"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT.name}")


if __name__ == "__main__":
    main()
