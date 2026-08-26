"""
HealthSense AI — Dataset Inspection Script
==========================================
Purpose:
    Perform a full data-quality audit of the raw BRFSS 2015 Heart Disease
    Health Indicators dataset before any preprocessing or model training.

Educational Disclaimer:
    This dataset is used for an educational AI/ML project only.
    It is NOT a medical diagnostic tool.

Usage:
    python ml/src/inspect_dataset.py

Output:
    Prints a structured report to stdout covering shape, dtypes, missing
    values, duplicates, descriptive statistics, and target distribution.
"""

import os
import sys
import pathlib

# ---------------------------------------------------------------------------
# Path setup — allow running from project root or ml/ directory
# ---------------------------------------------------------------------------
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent        # ml/src/
ML_DIR = SCRIPT_DIR.parent                                   # ml/
PROJECT_DIR = ML_DIR.parent                                  # project root

DATASET_PATH = ML_DIR / "data" / "raw" / "heart_disease_health_indicators_BRFSS2015.csv"

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------
try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print("[ERROR] Missing required package:", e)
    print("Run:  pip install -r ml/requirements.txt")
    sys.exit(1)


def separator(title: str = "", width: int = 70) -> None:
    """Print a visual section separator."""
    if title:
        pad = (width - len(title) - 2) // 2
        print("\n" + "=" * pad + f" {title} " + "=" * (width - pad - len(title) - 2))
    else:
        print("\n" + "=" * width)


def inspect_dataset(path: pathlib.Path) -> None:
    """Run the full dataset inspection pipeline."""

    # ------------------------------------------------------------------
    # 1. Load dataset
    # ------------------------------------------------------------------
    separator("LOADING DATASET")
    if not path.exists():
        print(f"[ERROR] Dataset not found at: {path}")
        print("Please download the dataset first:")
        print("  Source: https://www.kaggle.com/datasets/alexteboul/heart-disease-health-indicators-dataset")
        print(f"  Save to: {path}")
        sys.exit(1)

    print(f"Loading: {path}")
    df = pd.read_csv(path)
    print(f"Dataset loaded successfully.\n")

    # ------------------------------------------------------------------
    # 2. Shape
    # ------------------------------------------------------------------
    separator("SHAPE")
    print(f"  Rows    : {df.shape[0]:,}")
    print(f"  Columns : {df.shape[1]}")

    # ------------------------------------------------------------------
    # 3. Column names
    # ------------------------------------------------------------------
    separator("COLUMN NAMES")
    for i, col in enumerate(df.columns, start=1):
        print(f"  {i:>2}. {col}")

    # ------------------------------------------------------------------
    # 4. Data types
    # ------------------------------------------------------------------
    separator("DATA TYPES")
    dtype_df = df.dtypes.reset_index()
    dtype_df.columns = ["Column", "DType"]
    for _, row in dtype_df.iterrows():
        print(f"  {row['Column']:<30} {row['DType']}")

    # ------------------------------------------------------------------
    # 5. Missing values
    # ------------------------------------------------------------------
    separator("MISSING VALUES")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct})
    missing_df = missing_df[missing_df["Missing Count"] > 0]

    if missing_df.empty:
        print("  ✅ No missing values found.")
    else:
        print(f"  ⚠️  {len(missing_df)} column(s) with missing values:\n")
        print(missing_df.to_string())

    # ------------------------------------------------------------------
    # 6. Duplicate rows
    # ------------------------------------------------------------------
    separator("DUPLICATE ROWS")
    dup_count = df.duplicated().sum()
    if dup_count == 0:
        print("  ✅ No duplicate rows found.")
    else:
        print(f"  ⚠️  {dup_count:,} duplicate rows detected ({dup_count / len(df) * 100:.2f}%).")

    # ------------------------------------------------------------------
    # 7. Descriptive statistics (numerical)
    # ------------------------------------------------------------------
    separator("DESCRIPTIVE STATISTICS (Numerical)")
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print(f"  Numerical columns ({len(num_cols)}): {num_cols}\n")
    pd.set_option("display.float_format", "{:.2f}".format)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 120)
    print(df[num_cols].describe().to_string())

    # ------------------------------------------------------------------
    # 8. Categorical features
    # ------------------------------------------------------------------
    separator("CATEGORICAL FEATURES")
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_cols:
        print("  No object/category dtype columns detected.")
        print("  Note: Ordinal/binary columns are stored as float64 in this dataset.")
    else:
        for col in cat_cols:
            print(f"\n  [{col}] — unique values: {df[col].nunique()}")
            print(df[col].value_counts().head(10).to_string())

    # ------------------------------------------------------------------
    # 9. Target variable distribution
    # ------------------------------------------------------------------
    TARGET_COL = "HeartDiseaseorAttack"
    separator(f"TARGET DISTRIBUTION: {TARGET_COL}")

    if TARGET_COL not in df.columns:
        print(f"  [ERROR] Target column '{TARGET_COL}' not found in dataset!")
    else:
        counts = df[TARGET_COL].value_counts().sort_index()
        pcts   = (counts / len(df) * 100).round(2)
        print(f"  Total records: {len(df):,}\n")
        for val in counts.index:
            label = "No Heart Disease" if val == 0.0 else "Heart Disease / Attack"
            print(f"  Class {int(val)} ({label:<26}): {counts[val]:>8,}  ({pcts[val]:.2f}%)")

        # Class imbalance warning
        minority_pct = pcts.min()
        if minority_pct < 20:
            print(f"\n  ⚠️  Class imbalance detected (minority class = {minority_pct:.2f}%).")
            print("     Consider techniques such as class_weight='balanced' or SMOTE during training.")

    # ------------------------------------------------------------------
    # 10. Feature-to-Assessment mapping report
    # ------------------------------------------------------------------
    separator("FEATURE MAPPING: Dataset → HealthSense AI Assessment")
    mappings = [
        ("age",    "Age (ordinal 1–13)", "✅ Mappable",   "Convert user age (years) → CDC category"),
        ("gender", "Sex (0/1)",          "✅ Mappable",   "Male→1, Female→0, Other→0 (no Other in dataset)"),
        ("BMI",    "BMI (float)",        "✅ Mappable",   "Compute: weight_kg / (height_m ** 2)"),
        ("smoking","Smoker (binary)",    "⚠️  Partial",   "Never→0, Occasionally/Regularly→1"),
        ("alcohol","HvyAlcoholConsump",  "⚠️  Partial",   "Only heavy drinking captured"),
        ("exercise","PhysActivity",     "⚠️  Partial",   "Binary only; frequency not available"),
        ("sleep",  "— NOT in dataset —","❌ Missing",    "BRFSS 2015 does not include sleep hours"),
        ("water",  "— NOT in dataset —","❌ Missing",    "Water intake not in BRFSS survey"),
        ("symptoms","GenHlth, PhysHlth","⚠️  Proxy only","No direct symptom tags (Fever, Cough, etc.)"),
    ]
    header = f"  {'App Field':<15} {'Dataset Column':<22} {'Status':<15} {'Notes'}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for row in mappings:
        print(f"  {row[0]:<15} {row[1]:<22} {row[2]:<15} {row[3]}")

    # ------------------------------------------------------------------
    # 11. Summary
    # ------------------------------------------------------------------
    separator("SUMMARY")
    print(f"  Dataset rows   : {df.shape[0]:,}")
    print(f"  Dataset columns: {df.shape[1]}")
    print(f"  Missing values : {df.isnull().sum().sum()}")
    print(f"  Duplicate rows : {df.duplicated().sum():,}")
    print(f"  Numerical cols : {len(num_cols)}")
    print(f"  Categorical cols: {len(cat_cols)} (dtype object/category)")
    print(f"  Target column  : {TARGET_COL}")
    if TARGET_COL in df.columns:
        pos_rate = (df[TARGET_COL] == 1.0).mean() * 100
        print(f"  Positive rate  : {pos_rate:.2f}% (heart disease / attack)")
    separator()
    print("\n✅ Dataset inspection complete.")
    print("   Next step: Prompt 11 — data preprocessing & model training.\n")


if __name__ == "__main__":
    inspect_dataset(DATASET_PATH)
