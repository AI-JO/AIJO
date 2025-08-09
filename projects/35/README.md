# Project 35 — ED Patient Flow Modeling

## Quick start

1) Change into the project

```bash
cd /Users/amin/AIJO/projects/35
```

2) Use the project-local Conda environment

- Activate (preferred):

```bash
conda activate /Users/amin/AIJO/projects/35/.env
```

- If it does not exist yet, create it and then activate:

```bash
conda create -y --prefix /Users/amin/AIJO/projects/35/.env -c conda-forge \
  python=3.11 numpy=1.26 pandas=2.1 scikit-learn=1.3 scipy=1.10 \
  matplotlib=3.8 seaborn=0.13 pyarrow=14 bottleneck=1.3.7 numexpr=2.8.8
conda activate /Users/amin/AIJO/projects/35/.env
```

3) (Optional) Generate fresh synthetic data

```bash
./.env/bin/python generateData.py
```

4) Prepare MIMIC-like CSVs expected by the model

```bash
./.env/bin/python prepare_mimic_like_data.py
```

This writes the following files under `data/`:
- `edstays.csv`
- `triage.csv`
- `vitalsign.csv`
- `diagnosis.csv`

5) Run the model

```bash
./.env/bin/python model.py
```

Artifacts produced:
- `processed_mimic_ed_data.csv` in the project root
- Plots for arrivals by hour and LOS by disposition are displayed

## Expected results (example)

From a recent run on the included synthetic data:

```text
Patient Urgency Level Distribution:
urgency
high      0.598655
medium    0.215247
low       0.186099
Name: proportion, dtype: float64
```

```text
Accuracy: 0.78
              precision    recall  f1-score   support

           0       0.79      0.86      0.82       147
           1       0.74      0.65      0.69        94

    accuracy                           0.78       241
   macro avg       0.77      0.75      0.76       241
weighted avg       0.77      0.78      0.77       241
```

## Notes
- The environment is pinned to NumPy 1.26 to avoid NumPy 2.x ABI issues with compiled deps.
- `prepare_mimic_like_data.py` converts the synthetic CSVs into the MIMIC-like tables used by `model.py`.
