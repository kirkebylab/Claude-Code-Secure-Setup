---
description: Guided analysis of the fake qPCR demo data (fold changes, statistics, plot)
disable-model-invocation: true
---
Walk me through analysing the fake qPCR dataset in reference/fake_qpcr_data.csv. Its description is in reference/fake_qpcr_data_README.md. I am not a programmer, so explain each step in plain language before you do it.

## Ground rules

- reference/ is read-only. Put everything you create in workspace/qpcr-demo/.
- Use Python. If pandas, scipy and matplotlib are not installed, create a virtual environment in workspace/qpcr-demo/.venv and install them there. Before installing, tell me which websites that needs (it should be pypi.org and files.pythonhosted.org), so I know what I am approving.
- Write the analysis as one script, workspace/qpcr-demo/analyze_qpcr.py, so it can be run again from scratch.
- Do not open workspace/qpcr-demo/make_fake_qpcr_data.py until the last step.

## Steps

After each step, sum up what you found in two or three plain sentences.

1. Describe the data: the columns, the treatment groups, how many samples are in each group, and how many technical replicates each sample has.
2. Check quality: look for missing values, and check how closely the three technical replicates agree. Flag any sample and gene whose replicates differ by more than 0.5 Ct.
3. Calculate fold changes with the ΔΔCt method: average the technical replicates, subtract GAPDH within each sample (ΔCt), subtract the mean ctrl ΔCt for that gene (ΔΔCt), and convert to fold change as 2^(−ΔΔCt).
4. Test which genes change with each treatment compared with ctrl. Use one value per sample (the biological replicate), not the individual wells. Choose a suitable test, explain why, say what it assumes, and correct for multiple comparisons.
5. Plot log2 fold change for each gene and treatment, with every sample shown as a point and the group mean marked. Save it as workspace/qpcr-demo/fold_change.png.
6. Write a short plain-language summary of the results, with a table of fold changes and p-values, in workspace/qpcr-demo/RESULTS.md.
7. Finally, open workspace/qpcr-demo/make_fake_qpcr_data.py. It holds the "true" answer the data were simulated from (TRUE_LOG2FC). Tell me how close the analysis came.
