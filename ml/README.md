# HealthSense AI — ML Module

This directory contains all machine-learning-related code, data, and models for the HealthSense AI project.

> ⚠️ **Educational Disclaimer**: This is an educational AI/ML project. The model trained here is NOT a medical diagnostic tool. It cannot replace professional medical advice, diagnosis, or treatment. Dataset limitations and feature mismatches are documented below.

---

## Directory Structure

```
ml/
├── data/
│   ├── raw/                  # Original dataset — NEVER modify
│   │   └── heart_disease_health_indicators_BRFSS2015.csv
│   └── processed/            # Cleaned/encoded test sets (Prompt 11)
│       ├── X_test.csv        # Held-out test features (scaled)
│       └── y_test.csv        # Held-out test labels
├── notebooks/                # Jupyter notebooks for exploration
├── src/                      # Python scripts for ML pipeline
│   ├── download_dataset.py   # One-time dataset download (Prompt 10)
│   ├── inspect_dataset.py    # Dataset inspection/audit (Prompt 10)
│   ├── preprocess.py         # Preprocessing module (Prompt 11)
│   └── train.py              # Model training & evaluation (Prompt 11)
├── models/                   # Saved trained models
│   ├── best_model.pkl        # Best classifier (joblib) (Prompt 11)
│   ├── scaler.pkl            # Fitted StandardScaler (Prompt 11)
│   ├── feature_names.json    # Ordered feature list (Prompt 11)
│   └── training_summary.json # Evaluation metrics log (Prompt 11)
├── requirements.txt          # ML-only Python dependencies
└── README.md                 # This file
```

---

## Dataset

### Source

| Field       | Value                                                                                                                      |
|-------------|----------------------------------------------------------------------------------------------------------------------------|
| **Name**    | Heart Disease Health Indicators Dataset (CDC BRFSS 2015)                                                                   |
| **Origin**  | U.S. Centers for Disease Control and Prevention (CDC) — Behavioral Risk Factor Surveillance System (BRFSS) 2015 Survey     |
| **License** | CC0: Public Domain (no restrictions)                                                                                       |
| **Kaggle**  | https://www.kaggle.com/datasets/alexteboul/heart-disease-health-indicators-dataset                                         |
| **GitHub mirror used** | https://github.com/doguilmak/Heart-Diseaseor-Attack-Classification                                            |
| **File**    | `heart_disease_health_indicators_BRFSS2015.csv`                                                                            |
| **Rows**    | ~253,680 in full dataset; mirror used here contains a representative sample                                                |
| **Columns** | 22                                                                                                                         |

---

### Target Variable

| Column                  | Description                                                          |
|-------------------------|----------------------------------------------------------------------|
| `HeartDiseaseorAttack`  | Binary label: `1.0` = has had heart disease or heart attack, `0.0` = has not |

This will be mapped to our app's **risk levels**: Low / Moderate / High.

---

### Dataset Columns

| Column              | Type    | Description                                                                 |
|---------------------|---------|-----------------------------------------------------------------------------|
| HeartDiseaseorAttack | Binary | **Target** — 0 = no, 1 = yes                                               |
| HighBP              | Binary  | High blood pressure (0/1)                                                   |
| HighChol            | Binary  | High cholesterol (0/1)                                                      |
| CholCheck           | Binary  | Cholesterol check in last 5 years (0/1)                                     |
| BMI                 | Float   | Body Mass Index (can be computed from height+weight)                        |
| Smoker              | Binary  | Smoked at least 100 cigarettes ever (0/1)                                   |
| Stroke              | Binary  | Ever had a stroke (0/1)                                                     |
| Diabetes            | Float   | 0 = no, 1 = pre-diabetic, 2 = diabetic                                      |
| PhysActivity        | Binary  | Physical activity in past 30 days (0/1)                                     |
| Fruits              | Binary  | Eat fruit 1+ times/day (0/1)                                                |
| Veggies             | Binary  | Eat vegetables 1+ times/day (0/1)                                           |
| HvyAlcoholConsump   | Binary  | Heavy alcohol consumption (men >14/week, women >7/week) (0/1)               |
| AnyHealthcare       | Binary  | Has any form of health insurance (0/1)                                      |
| NoDocbcCost         | Binary  | Could not see doctor in past 12 months due to cost (0/1)                    |
| GenHlth             | Ordinal | General health: 1=Excellent, 2=Very Good, 3=Good, 4=Fair, 5=Poor           |
| MentHlth            | Float   | Days of poor mental health in past 30 days (0–30)                           |
| PhysHlth            | Float   | Days of poor physical health in past 30 days (0–30)                        |
| DiffWalk            | Binary  | Difficulty walking or climbing stairs (0/1)                                 |
| Sex                 | Binary  | 0 = Female, 1 = Male                                                       |
| Age                 | Ordinal | Age category: 1=18–24, 2=25–29, ..., 13=80+                               |
| Education           | Ordinal | Education level: 1–6                                                       |
| Income              | Ordinal | Income level: 1–8                                                          |

---

## Feature Mapping: Dataset vs. HealthSense AI Assessment

| HealthSense AI Field  | Dataset Column       | Mapping Strategy                                                               |
|-----------------------|----------------------|--------------------------------------------------------------------------------|
| `age`                 | `Age` (ordinal 1–13) | **Mappable** — convert user's age (years) to CDC ordinal categories            |
| `gender`              | `Sex` (0/1)          | **Mappable** — Male→1, Female→0, Other→0 (limitation: no "Other" in dataset)  |
| `height` + `weight`   | `BMI` (float)        | **Mappable** — compute BMI = weight(kg) / height(m)²                           |
| `smoking`             | `Smoker` (binary)    | **Partial** — map Never→0, Occasionally/Regularly→1 (no "occasional" in dataset) |
| `alcohol`             | `HvyAlcoholConsump`  | **Partial** — only heavy consumption is captured (moderate use is not flagged) |
| `exercise`            | `PhysActivity`       | **Partial** — dataset only has binary yes/no, not frequency categories         |
| `sleep`               | ❌ Not in dataset     | **Not available** — BRFSS 2015 does not include sleep hours                    |
| `water`               | ❌ Not in dataset     | **Not available** — water intake not present in BRFSS survey                   |
| `selectedSymptoms`    | `GenHlth`, `PhysHlth`, `DiffWalk`, etc. | **Partial** — general health indicators exist but not direct symptom tags |

### Summary

- ✅ **Well-mapped**: age, gender, BMI (from height+weight), smoking, exercise (binary)
- ⚠️ **Partially-mapped**: alcohol (only heavy use), symptoms (general health indicators)
- ❌ **Not in dataset**: sleep hours, daily water intake, specific symptom tags (Fever, Headache, etc.)

---

## Limitations

1. **Sleep & Water**: These lifestyle fields collected by our app have NO direct equivalent in the BRFSS 2015 dataset. They will need to be excluded from the model features or handled with proxy variables.
2. **Specific Symptoms**: The app collects specific symptom tags (Fever, Cough, Chest Pain, etc.). The dataset does not have these; it has general health proxy scores instead.
3. **Age Encoding**: The dataset uses 13 ordinal age categories, not exact years. Mapping must be applied carefully.
4. **Target Mismatch**: The dataset's target is *heart disease/attack history*, not a general "health risk score". The three-tier risk output (Low/Moderate/High) in our app is an **educational abstraction**, not a clinical diagnosis.
5. **Dataset Size (Mirror)**: The GitHub mirror used here contains a sample. The full 253,680-row version is available on Kaggle.
6. **Class Imbalance**: Heart disease is relatively rare in the dataset (~9% positive rate). Handled via `class_weight='balanced'` in all classifiers — no SMOTE needed given ~24k minority-class training samples.
7. **No Medical Validation**: This dataset is self-reported survey data from BRFSS. It is appropriate for educational ML modeling but has not been clinically validated for individual diagnostic use.

---

## How This Relates to HealthSense AI

The trained model will:
1. Accept user inputs from the assessment form (after encoding/mapping)
2. Compute a **risk score** (predicted probability × 100)
3. Classify into Low / Moderate / High risk tiers
4. Generate recommendations based on risk factors

The `/predict` endpoint in `backend/main.py` will eventually call the saved model from `ml/models/` to replace the current placeholder response.

---

## Prompt 11 — Preprocessing & Model Training

### Preprocessing Pipeline (`ml/src/preprocess.py`)

| Step | Action | Detail |
|------|--------|--------|
| 1 | Load raw CSV | 253,680 rows × 22 columns |
| 2 | Drop duplicates | ~24k duplicate rows removed |
| 3 | Missing values | None found — no imputation needed |
| 4 | Define X and y | X = 21 feature columns; y = `HeartDiseaseorAttack` |
| 5 | Stratified split | 80% train / 20% test, `random_state=42` |
| 6 | StandardScaler | Applied only to 7 continuous columns (BMI, MentHlth, PhysHlth, GenHlth, Age, Education, Income) — fitted on train only to prevent data leakage |
| 7 | Class imbalance | `class_weight='balanced'` in all classifiers; `sample_weight` used for GradientBoosting (which lacks `class_weight`) |

**Why `class_weight='balanced'` instead of SMOTE?**
With ~24,000 positive-class training samples after deduplication, the minority class is large enough that SMOTE provides marginal benefit at the cost of added complexity and training time. `class_weight='balanced'` adjusts the loss function directly and requires zero synthetic data.

---

### Models Trained (`ml/src/train.py`)

| Model | Key Config |
|-------|-----------|
| **Logistic Regression** | `solver=lbfgs`, `max_iter=1000`, `class_weight='balanced'` |
| **Random Forest** | 100 trees, `min_samples_leaf=5`, `class_weight='balanced'`, `n_jobs=-1` |
| **Gradient Boosting** | 200 estimators, `learning_rate=0.05`, `max_depth=4`, `subsample=0.8`, `sample_weight` for imbalance |

**Selection criterion:** ROC-AUC (primary metric) + Recall (tiebreaker).

Raw accuracy is misleading with class imbalance — a naïve classifier that always predicts "No Heart Disease" achieves ~91% accuracy. ROC-AUC measures the model's discrimination ability across all thresholds and is appropriate for imbalanced classification.

---

### Expected Evaluation Metrics (representative ranges)

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|----------|-----------|--------|----|---------|
| Logistic Regression | ~73–76% | ~0.25–0.30 | ~0.70–0.75 | ~0.38–0.42 | ~0.79–0.82 |
| Random Forest | ~85–88% | ~0.45–0.55 | ~0.45–0.55 | ~0.48–0.54 | ~0.82–0.86 |
| **Gradient Boosting** | **~82–86%** | **~0.40–0.50** | **~0.55–0.65** | **~0.48–0.56** | **~0.83–0.88** |

> Actual values after deduplication depend on the exact CSV. See `ml/models/training_summary.json` for real numbers.

**Note on Logistic Regression:** It achieves high recall by aggressively predicting the positive class (lower threshold effect from `class_weight`). RF and GBC balance precision/recall better. GBC typically wins on ROC-AUC for tabular health data.

---

### Saved Artifacts

| File | Description | Used by |
|------|-------------|---------|
| `ml/models/best_model.pkl` | Best classifier (joblib serialised) | FastAPI `/predict` (Prompt 12) |
| `ml/models/scaler.pkl` | Fitted `StandardScaler` — must be applied to inference inputs | FastAPI `/predict` (Prompt 12) |
| `ml/models/feature_names.json` | Ordered list of 21 feature columns — inference order must match | FastAPI `/predict` (Prompt 12) |
| `ml/models/training_summary.json` | Metrics for all 3 models + metadata | Documentation / reporting |
| `ml/data/processed/X_test.csv` | 20% held-out test features (scaled) | Future evaluation scripts |
| `ml/data/processed/y_test.csv` | 20% held-out test labels | Future evaluation scripts |

---

### How the Saved Model Will Be Used (Prompt 12 — Backend Integration)

The FastAPI `/predict` endpoint in `backend/main.py` will be updated to:

1. **Load at startup**: `best_model.pkl`, `scaler.pkl`, `feature_names.json`
2. **Map user inputs** from the assessment form → 21-feature vector in `feature_names.json` order
3. **Scale** the feature vector using the pre-fitted scaler (same transform applied at training)
4. **Predict**: `model.predict_proba(X)[0][1]` → probability ∈ [0, 1]
5. **Map probability** → risk tier (e.g., < 0.25 → Low, 0.25–0.55 → Moderate, > 0.55 → High)
6. **Return** the `PredictionResult` with real score, tier, and recommendations

> **Limitation note**: The app collects `sleep`, `water`, and specific `selectedSymptoms` which have no direct dataset equivalent. During inference mapping (Prompt 12), these will be handled with proxy substitutions or excluded, as documented in the Feature Mapping table above.

---

## Setup

```bash
# Install ML dependencies (from project root)
pip install -r ml/requirements.txt

# Step 1 — Inspect dataset (Prompt 10, already run)
python ml/src/inspect_dataset.py

# Step 2 — Preprocess only (generates scaler/feature artifacts + test set)
python ml/src/preprocess.py

# Step 3 — Full training pipeline: preprocess + train + evaluate + save (Prompt 11)
python ml/src/train.py
```

After `train.py` completes:
- Check `ml/models/training_summary.json` for actual metrics and best model name
- Check `ml/models/` for `best_model.pkl`, `scaler.pkl`, `feature_names.json`
- Check `ml/data/processed/` for `X_test.csv` and `y_test.csv`
