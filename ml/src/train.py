"""
HealthSense AI — Model Training & Evaluation Script
====================================================
Prompt 11: Data Preprocessing & Model Training

Purpose:
    Train and compare multiple baseline classification models on the
    preprocessed BRFSS 2015 Heart Disease dataset. Select the best model
    by ROC-AUC (with Recall as tiebreaker), and save it for use by the
    FastAPI backend.

Models trained:
    1. Logistic Regression       — interpretable linear baseline
    2. Random Forest Classifier  — robust ensemble (handles non-linearity)
    3. Gradient Boosting         — typically strongest on tabular data

Class imbalance strategy:
    class_weight='balanced' — automatically adjusts sample weights so that
    the minority class (heart disease, ~9%) is treated proportionally during
    training. No SMOTE required at this dataset size.

Primary evaluation metric:
    ROC-AUC — measures the model's ability to discriminate between classes
    regardless of the classification threshold. More informative than
    accuracy alone when classes are imbalanced.

Usage:
    python ml/src/train.py

Output:
    ml/models/best_model.pkl      — Saved best model (joblib)
    ml/models/scaler.pkl          — Fitted StandardScaler (from preprocessing)
    ml/models/feature_names.json  — Ordered feature column names
    ml/data/processed/X_test.csv  — Held-out test features (scaled)
    ml/data/processed/y_test.csv  — Held-out test labels

Educational Disclaimer:
    This is an educational AI/ML project. The trained model is NOT a
    medical diagnostic tool. See ml/README.md for full context.
"""

import pathlib
import sys
import time
import json

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR  = pathlib.Path(__file__).resolve().parent   # ml/src/
ML_DIR      = SCRIPT_DIR.parent                          # ml/
PROJECT_DIR = ML_DIR.parent                              # project root

# Add ml/src to path so we can import preprocess
sys.path.insert(0, str(SCRIPT_DIR))

MODELS_DIR   = ML_DIR / "models"
BEST_MODEL_PATH = MODELS_DIR / "best_model.pkl"

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------
try:
    import numpy as np
    import joblib
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score,
        f1_score, roc_auc_score, confusion_matrix,
        classification_report,
    )
except ImportError as e:
    print(f"[ERROR] Missing required package: {e}")
    print("Run:  pip install -r ml/requirements.txt")
    sys.exit(1)

try:
    from preprocess import load_and_preprocess, SCALER_PATH, FEAT_NAMES_PATH
except ImportError:
    print("[ERROR] Could not import preprocess.py. Make sure you run this from the project root:")
    print("  python ml/src/train.py")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def separator(title: str = "", width: int = 72) -> None:
    """Print a visual section separator."""
    if title:
        pad = (width - len(title) - 2) // 2
        print("\n" + "=" * pad + f" {title} " + "=" * (width - pad - len(title) - 2))
    else:
        print("\n" + "=" * width)


def evaluate_model(
    name: str,
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    verbose: bool = True,
) -> dict:
    """
    Evaluate a fitted classifier on the test set.

    Returns a dict with all metrics:
        accuracy, precision, recall, f1, roc_auc, confusion_matrix
    """
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "name":       name,
        "accuracy":   accuracy_score(y_test, y_pred),
        "precision":  precision_score(y_test, y_pred, zero_division=0),
        "recall":     recall_score(y_test, y_pred, zero_division=0),
        "f1":         f1_score(y_test, y_pred, zero_division=0),
        "roc_auc":    roc_auc_score(y_test, y_proba),
        "conf_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    if verbose:
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        print(f"\n  Model         : {name}")
        print(f"  Accuracy      : {metrics['accuracy']:.4f}  ({metrics['accuracy'] * 100:.2f}%)")
        print(f"  Precision     : {metrics['precision']:.4f}")
        print(f"  Recall        : {metrics['recall']:.4f}   ← important (catches true positives)")
        print(f"  F1-score      : {metrics['f1']:.4f}")
        print(f"  ROC-AUC       : {metrics['roc_auc']:.4f}  ← primary selection metric")
        print(f"  Confusion Matrix:")
        print(f"              Predicted 0  Predicted 1")
        print(f"    Actual 0     {tn:>7,}      {fp:>7,}   (TN, FP)")
        print(f"    Actual 1     {fn:>7,}      {tp:>7,}   (FN, TP)")
        print(f"\n  Full Classification Report:")
        print(classification_report(y_test, y_pred, target_names=["No Heart Disease", "Heart Disease"], zero_division=0))

    return metrics


# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------

def get_models() -> list[tuple[str, object]]:
    """
    Return list of (name, unfitted_model) tuples.

    All classifiers use class_weight='balanced' to handle the ~9:1 imbalance.
    Hyperparameters are set to reasonable defaults suitable for a 200k-row
    educational project — no exhaustive tuning yet.
    """
    models = [
        (
            "Logistic Regression",
            LogisticRegression(
                class_weight="balanced",
                max_iter=1000,        # enough iterations for convergence
                solver="lbfgs",       # efficient for medium-sized datasets
                random_state=42,
                n_jobs=-1,
            ),
        ),
        (
            "Random Forest",
            RandomForestClassifier(
                n_estimators=100,     # 100 trees — good balance of speed/accuracy
                class_weight="balanced",
                max_depth=None,       # let trees grow fully; pruned by min_samples
                min_samples_leaf=5,   # prevents over-fitting on noisy leaves
                random_state=42,
                n_jobs=-1,
            ),
        ),
        (
            "Gradient Boosting",
            GradientBoostingClassifier(
                n_estimators=200,     # more trees for boosting (each is shallow)
                learning_rate=0.05,   # lower LR + more trees → better generalisation
                max_depth=4,          # shallow trees prevent overfitting
                subsample=0.8,        # stochastic boosting for regularisation
                random_state=42,
                # Note: GBC doesn't support class_weight; instead we pass
                # sample_weight during .fit() — handled in training loop below
            ),
        ),
    ]
    return models


# ---------------------------------------------------------------------------
# Main training pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n" + "=" * 72)
    print("  HealthSense AI — Model Training Pipeline (Prompt 11)")
    print("=" * 72)

    # ------------------------------------------------------------------
    # Phase 1: Preprocessing
    # ------------------------------------------------------------------
    separator("PHASE 1: PREPROCESSING")
    data = load_and_preprocess(save_artifacts=True, verbose=True)

    X_train = data["X_train"]
    X_test  = data["X_test"]
    y_train = data["y_train"]
    y_test  = data["y_test"]

    print(f"\n  Training set : {X_train.shape[0]:,} samples, {X_train.shape[1]} features")
    print(f"  Test set     : {X_test.shape[0]:,} samples")

    # Compute sample weights for GradientBoosting (no class_weight param)
    # Weight = n_samples / (n_classes * n_samples_per_class)
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    sample_weights = np.where(y_train == 1, len(y_train) / (2 * n_pos),
                                             len(y_train) / (2 * n_neg))

    # ------------------------------------------------------------------
    # Phase 2: Train all models
    # ------------------------------------------------------------------
    separator("PHASE 2: TRAINING MODELS")
    print(f"\n  Training {len(get_models())} models with class_weight='balanced'...")
    print("  (This may take a few minutes for Random Forest and Gradient Boosting)\n")

    models        = get_models()
    trained       = {}   # name -> fitted model
    timing        = {}   # name -> seconds

    for name, model in models:
        print(f"  [{name}] Training...", end=" ", flush=True)
        t0 = time.time()

        if name == "Gradient Boosting":
            # GBC doesn't have class_weight — use sample_weight instead
            model.fit(X_train, y_train, sample_weight=sample_weights)
        else:
            model.fit(X_train, y_train)

        elapsed = time.time() - t0
        timing[name] = elapsed
        trained[name] = model
        print(f"done in {elapsed:.1f}s ✅")

    # ------------------------------------------------------------------
    # Phase 3: Evaluate all models
    # ------------------------------------------------------------------
    separator("PHASE 3: EVALUATION RESULTS")

    all_metrics = {}
    for name, model in trained.items():
        separator(f"  {name}")
        metrics = evaluate_model(name, model, X_test, y_test, verbose=True)
        all_metrics[name] = metrics

    # ------------------------------------------------------------------
    # Phase 4: Comparison table
    # ------------------------------------------------------------------
    separator("PHASE 4: MODEL COMPARISON TABLE")

    print(f"\n  {'Model':<26} {'Accuracy':>9} {'Precision':>9} {'Recall':>9} {'F1':>9} {'ROC-AUC':>9}")
    print("  " + "-" * 75)
    for name, m in all_metrics.items():
        print(
            f"  {name:<26} "
            f"{m['accuracy']:>9.4f} "
            f"{m['precision']:>9.4f} "
            f"{m['recall']:>9.4f} "
            f"{m['f1']:>9.4f} "
            f"{m['roc_auc']:>9.4f}"
        )
    print()

    # ------------------------------------------------------------------
    # Phase 5: Select best model
    # ------------------------------------------------------------------
    separator("PHASE 5: MODEL SELECTION")

    # Primary: highest ROC-AUC; tiebreaker: highest Recall
    best_name = max(
        all_metrics,
        key=lambda n: (all_metrics[n]["roc_auc"], all_metrics[n]["recall"])
    )
    best_model   = trained[best_name]
    best_metrics = all_metrics[best_name]

    print(f"\n  🏆 Best model selected: {best_name}")
    print(f"     ROC-AUC : {best_metrics['roc_auc']:.4f}  (primary metric)")
    print(f"     Recall  : {best_metrics['recall']:.4f}  (tiebreaker — minimise false negatives)")
    print(f"     F1      : {best_metrics['f1']:.4f}")
    print(f"\n  Selection rationale:")
    print("     • ROC-AUC chosen as primary metric because class imbalance makes")
    print("       raw accuracy misleading (a naive 'always predict 0' model gets ~91%).")
    print("     • Recall is the tiebreaker because in a health context, false negatives")
    print("       (missing actual heart disease cases) are costlier than false positives.")

    # ------------------------------------------------------------------
    # Phase 6: Save best model
    # ------------------------------------------------------------------
    separator("PHASE 6: SAVING BEST MODEL")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, BEST_MODEL_PATH)
    print(f"\n  ✅ Best model saved : {BEST_MODEL_PATH}")
    print(f"  ✅ Scaler saved     : {SCALER_PATH}")
    print(f"  ✅ Feature names    : {FEAT_NAMES_PATH}")

    # Save a training summary JSON (useful for documentation / README update)
    summary_path = MODELS_DIR / "training_summary.json"
    summary = {
        "best_model_name":    best_name,
        "best_model_file":    "best_model.pkl",
        "scaler_file":        "scaler.pkl",
        "feature_names_file": "feature_names.json",
        "random_state":       42,
        "test_size":          0.20,
        "n_train":            int(data["n_train"]),
        "n_test":             int(data["n_test"]),
        "class_imbalance_strategy": "class_weight='balanced' (sample_weight for GBC)",
        "models_evaluated": {
            name: {
                "accuracy":  round(m["accuracy"],  4),
                "precision": round(m["precision"], 4),
                "recall":    round(m["recall"],    4),
                "f1":        round(m["f1"],        4),
                "roc_auc":   round(m["roc_auc"],   4),
                "training_time_s": round(timing[name], 2),
            }
            for name, m in all_metrics.items()
        },
        "best_model_metrics": {
            "accuracy":  round(best_metrics["accuracy"],  4),
            "precision": round(best_metrics["precision"], 4),
            "recall":    round(best_metrics["recall"],    4),
            "f1":        round(best_metrics["f1"],        4),
            "roc_auc":   round(best_metrics["roc_auc"],   4),
        },
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  ✅ Training summary : {summary_path}")

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    separator("TRAINING COMPLETE")
    print(f"\n  Best model   : {best_name}")
    print(f"  ROC-AUC      : {best_metrics['roc_auc']:.4f}")
    print(f"  Recall       : {best_metrics['recall']:.4f}")
    print(f"  F1-score     : {best_metrics['f1']:.4f}")
    print(f"  Accuracy     : {best_metrics['accuracy']:.4f}")
    print(f"\n  Saved artifacts:")
    print(f"    ml/models/best_model.pkl")
    print(f"    ml/models/scaler.pkl")
    print(f"    ml/models/feature_names.json")
    print(f"    ml/models/training_summary.json")
    print(f"    ml/data/processed/X_test.csv")
    print(f"    ml/data/processed/y_test.csv")
    print(f"\n  ⚠️  Educational disclaimer: This is NOT a medical diagnostic tool.")
    print(f"     See ml/README.md for full context and limitations.\n")
    print("=" * 72)
    print(f"  🚀 Next step (Prompt 12): Integrate best_model.pkl into FastAPI /predict")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
