"""
HealthSense AI — Data Preprocessing Module
===========================================
Prompt 11: Data Preprocessing & Model Training

Purpose:
    Load the raw BRFSS 2015 Heart Disease Health Indicators dataset,
    clean it, engineer/scale features, and split into train/test sets.

    This module is designed to be both:
      - Imported by train.py (returns ready-to-use arrays)
      - Run directly for a preprocessing summary report

Usage:
    python ml/src/preprocess.py           # standalone report
    from ml.src.preprocess import load_and_preprocess   # imported

Output (when saving=True):
    ml/models/scaler.pkl              — Fitted StandardScaler
    ml/models/feature_names.json      — Ordered list of feature names
    ml/data/processed/X_test.csv      — Held-out test features
    ml/data/processed/y_test.csv      — Held-out test labels

Educational Disclaimer:
    This is an educational AI/ML project. The model trained on this data
    is NOT a medical diagnostic tool. See ml/README.md for full details.
"""

import json
import pathlib
import sys

# ---------------------------------------------------------------------------
# Path resolution — works whether run from project root or ml/ directory
# ---------------------------------------------------------------------------
SCRIPT_DIR  = pathlib.Path(__file__).resolve().parent   # ml/src/
ML_DIR      = SCRIPT_DIR.parent                          # ml/
PROJECT_DIR = ML_DIR.parent                              # project root

DATASET_PATH    = ML_DIR / "data" / "raw" / "heart_disease_health_indicators_BRFSS2015.csv"
MODELS_DIR      = ML_DIR / "models"
PROCESSED_DIR   = ML_DIR / "data" / "processed"
SCALER_PATH     = MODELS_DIR / "scaler.pkl"
FEAT_NAMES_PATH = MODELS_DIR / "feature_names.json"

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------
try:
    import numpy as np
    import pandas as pd
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
except ImportError as e:
    print(f"[ERROR] Missing required package: {e}")
    print("Run:  pip install -r ml/requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TARGET_COL = "HeartDiseaseorAttack"
RANDOM_STATE = 42
TEST_SIZE    = 0.20   # 80 % train / 20 % test, stratified

# Continuous columns that benefit from standardisation.
# These have ranges wider than [0, 1]:
CONTINUOUS_COLS = [
    "BMI",
    "MentHlth",
    "PhysHlth",
    "GenHlth",   # ordinal 1–5, standardise for logistic regression
    "Age",       # ordinal 1–13
    "Education", # ordinal 1–6
    "Income",    # ordinal 1–8
]

# All feature columns (everything except target).
# Order matters — must be reproduced exactly at inference time.
FEATURE_COLS = [
    "HighBP", "HighChol", "CholCheck", "BMI", "Smoker",
    "Stroke", "Diabetes", "PhysActivity", "Fruits", "Veggies",
    "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost", "GenHlth",
    "MentHlth", "PhysHlth", "DiffWalk", "Sex", "Age",
    "Education", "Income",
]
# Note: 21 feature columns total (22 dataset cols minus the 1 target)


# ---------------------------------------------------------------------------
# Core preprocessing function
# ---------------------------------------------------------------------------

def load_and_preprocess(
    dataset_path: pathlib.Path = DATASET_PATH,
    save_artifacts: bool = False,
    verbose: bool = True,
) -> dict:
    """
    Load and preprocess the BRFSS 2015 dataset.

    Parameters
    ----------
    dataset_path : pathlib.Path
        Path to the raw CSV file.
    save_artifacts : bool
        If True, write scaler.pkl, feature_names.json, X_test.csv, y_test.csv
        to the appropriate directories.
    verbose : bool
        If True, print a structured preprocessing report.

    Returns
    -------
    dict with keys:
        X_train, X_test : np.ndarray  — Scaled feature arrays
        y_train, y_test : np.ndarray  — Integer label arrays (0 or 1)
        feature_names   : list[str]   — Ordered feature names (pre-scaling)
        scaler          : StandardScaler — Fitted scaler (for inference)
        n_train, n_test : int          — Number of samples in each split
        positive_rate_train : float   — Positive class rate in training set
    """

    def _log(msg: str) -> None:
        if verbose:
            print(msg)

    # ------------------------------------------------------------------
    # 1. Load dataset
    # ------------------------------------------------------------------
    _log("\n" + "=" * 70)
    _log(" STEP 1 — Loading dataset")
    _log("=" * 70)

    if not dataset_path.exists():
        print(f"[ERROR] Dataset not found: {dataset_path}")
        print("Run:  python ml/src/download_dataset.py")
        sys.exit(1)

    df = pd.read_csv(dataset_path)
    _log(f"  Loaded: {dataset_path.name}")
    _log(f"  Shape : {df.shape[0]:,} rows × {df.shape[1]} columns")

    # Verify expected columns are present
    missing_cols = [c for c in FEATURE_COLS + [TARGET_COL] if c not in df.columns]
    if missing_cols:
        print(f"[ERROR] Dataset missing expected columns: {missing_cols}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Remove duplicate rows
    # ------------------------------------------------------------------
    _log("\n" + "=" * 70)
    _log(" STEP 2 — Removing duplicate rows")
    _log("=" * 70)

    n_before = len(df)
    df = df.drop_duplicates()
    n_after  = len(df)
    n_removed = n_before - n_after
    _log(f"  Before : {n_before:,} rows")
    _log(f"  Removed: {n_removed:,} duplicate rows ({n_removed / n_before * 100:.2f}%)")
    _log(f"  After  : {n_after:,} rows")

    # ------------------------------------------------------------------
    # 3. Missing values check
    # ------------------------------------------------------------------
    _log("\n" + "=" * 70)
    _log(" STEP 3 — Missing values")
    _log("=" * 70)

    missing_total = df[FEATURE_COLS + [TARGET_COL]].isnull().sum().sum()
    if missing_total == 0:
        _log("  ✅ No missing values in relevant columns.")
    else:
        _log(f"  ⚠️  {missing_total} missing values detected — dropping affected rows.")
        df = df.dropna(subset=FEATURE_COLS + [TARGET_COL])
        _log(f"  Remaining rows: {len(df):,}")

    # ------------------------------------------------------------------
    # 4. Define X and y
    # ------------------------------------------------------------------
    _log("\n" + "=" * 70)
    _log(" STEP 4 — Defining features (X) and target (y)")
    _log("=" * 70)

    X_raw = df[FEATURE_COLS].copy()
    y     = df[TARGET_COL].astype(int).values

    _log(f"  Feature matrix X : {X_raw.shape[0]:,} × {X_raw.shape[1]}")
    _log(f"  Target vector  y : {len(y):,} samples")
    _log(f"  Feature columns ({len(FEATURE_COLS)}):")
    for i, col in enumerate(FEATURE_COLS, 1):
        kind = "continuous" if col in CONTINUOUS_COLS else "binary/ordinal"
        _log(f"    {i:>2}. {col:<25} [{kind}]")

    # ------------------------------------------------------------------
    # 5. Train / test split (stratified)
    # ------------------------------------------------------------------
    _log("\n" + "=" * 70)
    _log(" STEP 5 — Stratified train / test split")
    _log("=" * 70)

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    _log(f"  Train size : {len(X_train_raw):,}  ({100 - TEST_SIZE * 100:.0f}%)")
    _log(f"  Test size  : {len(X_test_raw):,}   ({TEST_SIZE * 100:.0f}%)")
    _log(f"  random_state = {RANDOM_STATE}  (reproducible)")
    _log(f"  Positive rate (train): {y_train.mean() * 100:.2f}%")
    _log(f"  Positive rate (test) : {y_test.mean() * 100:.2f}%")

    # ------------------------------------------------------------------
    # 6. Feature scaling (StandardScaler on continuous columns only)
    # ------------------------------------------------------------------
    _log("\n" + "=" * 70)
    _log(" STEP 6 — Feature scaling")
    _log("=" * 70)
    _log("  Strategy: StandardScaler applied only to continuous/ordinal columns.")
    _log("  Binary features are already in [0, 1] — no scaling needed.")
    _log(f"  Scaled columns: {CONTINUOUS_COLS}")

    scaler = StandardScaler()

    # Fit ONLY on training data — prevents data leakage
    X_train_arr = X_train_raw.values.copy().astype(float)
    X_test_arr  = X_test_raw.values.copy().astype(float)

    cont_indices = [FEATURE_COLS.index(c) for c in CONTINUOUS_COLS]

    scaler.fit(X_train_arr[:, cont_indices])
    X_train_arr[:, cont_indices] = scaler.transform(X_train_arr[:, cont_indices])
    X_test_arr[:, cont_indices]  = scaler.transform(X_test_arr[:, cont_indices])

    _log(f"  Scaler fitted on {len(X_train_arr):,} training samples.")
    _log("  ✅ Scaling complete.")

    # ------------------------------------------------------------------
    # 7. Class imbalance summary
    # ------------------------------------------------------------------
    _log("\n" + "=" * 70)
    _log(" STEP 7 — Class imbalance summary")
    _log("=" * 70)

    pos_train = y_train.sum()
    neg_train = (y_train == 0).sum()
    pos_pct   = pos_train / len(y_train) * 100
    _log(f"  Negative class (no heart disease) : {neg_train:>7,} ({100 - pos_pct:.2f}%)")
    _log(f"  Positive class (heart disease)    : {pos_train:>7,} ({pos_pct:.2f}%)")
    _log(f"  Imbalance ratio                   : {neg_train / pos_train:.1f}:1")
    _log("  Handling strategy: class_weight='balanced' in all classifiers.")
    _log("  This automatically up-weights the minority class during training.")

    # ------------------------------------------------------------------
    # 8. Save artifacts (optional)
    # ------------------------------------------------------------------
    if save_artifacts:
        _log("\n" + "=" * 70)
        _log(" STEP 8 — Saving preprocessing artifacts")
        _log("=" * 70)

        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        # Save scaler
        joblib.dump(scaler, SCALER_PATH)
        _log(f"  ✅ Scaler saved   : {SCALER_PATH}")

        # Save feature names (in exact order)
        with open(FEAT_NAMES_PATH, "w") as f:
            json.dump(FEATURE_COLS, f, indent=2)
        _log(f"  ✅ Feature names  : {FEAT_NAMES_PATH}")

        # Save test set (for later evaluation / reporting)
        X_test_df = pd.DataFrame(X_test_arr, columns=FEATURE_COLS)
        y_test_df = pd.Series(y_test, name=TARGET_COL)
        X_test_df.to_csv(PROCESSED_DIR / "X_test.csv", index=False)
        y_test_df.to_csv(PROCESSED_DIR / "y_test.csv", index=False)
        _log(f"  ✅ X_test saved   : {PROCESSED_DIR / 'X_test.csv'}")
        _log(f"  ✅ y_test saved   : {PROCESSED_DIR / 'y_test.csv'}")

    _log("\n✅ Preprocessing complete.\n")

    return {
        "X_train":             X_train_arr,
        "X_test":              X_test_arr,
        "y_train":             y_train,
        "y_test":              y_test,
        "feature_names":       FEATURE_COLS,
        "scaler":              scaler,
        "n_train":             len(X_train_arr),
        "n_test":              len(X_test_arr),
        "positive_rate_train": float(y_train.mean()),
    }


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\nHealthSense AI — Preprocessing Report")
    print("=" * 70)
    result = load_and_preprocess(save_artifacts=True, verbose=True)
    print("\nSummary")
    print("-" * 40)
    print(f"  Training samples  : {result['n_train']:,}")
    print(f"  Test samples      : {result['n_test']:,}")
    print(f"  Feature count     : {len(result['feature_names'])}")
    print(f"  Positive rate     : {result['positive_rate_train'] * 100:.2f}% (training set)")
    print(f"\nArtifacts saved to:")
    print(f"  {SCALER_PATH}")
    print(f"  {FEAT_NAMES_PATH}")
    print(f"  {PROCESSED_DIR / 'X_test.csv'}")
    print(f"  {PROCESSED_DIR / 'y_test.csv'}")
    print("\n🚀 Next step: python ml/src/train.py\n")
