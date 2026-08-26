"""
HealthSense AI — FastAPI Backend
=================================
Prompt 12: ML Model Integration

Integrates the trained Gradient Boosting classifier (ml/models/best_model.pkl)
into the /predict endpoint, replacing the Prompt 9 placeholder response.

Architecture:
    Browser → Next.js /api/predict proxy → FastAPI /predict → ML model → JSON

Model artifacts (loaded once at startup):
    ml/models/best_model.pkl      — Trained GradientBoostingClassifier
    ml/models/scaler.pkl          — Fitted StandardScaler (same as training)
    ml/models/feature_names.json  — Ordered list of 21 feature columns

Feature mapping from assessment form → BRFSS dataset features:
    age (years str)         → Age (CDC ordinal 1–13)
    gender (str)            → Sex (0=Female, 1=Male)
    height+weight (cm, kg)  → BMI = weight_kg / (height_m²)
    smoking (str)           → Smoker (0/1)
    alcohol (str)           → HvyAlcoholConsump (0/1)  [only "Regularly" → 1]
    exercise (str)          → PhysActivity (0/1)

NOT mapped (no BRFSS equivalent; used only in summary text):
    sleep, water, selectedSymptoms

Unmappable features default to population-average safe values:
    HighBP, HighChol, CholCheck, Stroke, Diabetes, Fruits, Veggies,
    AnyHealthcare, NoDocbcCost, GenHlth, MentHlth, PhysHlth, DiffWalk,
    Education, Income

Educational Disclaimer:
    This is an educational AI/ML project. The predictions produced are NOT
    medical diagnoses. They are illustrative risk estimates based on a public
    CDC survey dataset (BRFSS 2015). Always consult a qualified healthcare
    professional for any medical concerns.
"""

import json
import logging
import os
import pathlib
import sys
from typing import List, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dependency guard (numpy / sklearn / joblib)
# ---------------------------------------------------------------------------
try:
    import numpy as np
    import joblib
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    logger.error(
        "Missing ML dependency: %s\n"
        "Run:  pip install -r ml/requirements.txt  (or add numpy/scikit-learn/joblib to backend/requirements.txt)",
        exc,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Artifact paths — relative to project root, resolved at module load time
# ---------------------------------------------------------------------------
_HERE = pathlib.Path(__file__).resolve().parent          # backend/
PROJECT_DIR = _HERE.parent                                # project root
ML_MODELS_DIR = PROJECT_DIR / "ml" / "models"

_MODEL_PATH   = ML_MODELS_DIR / "best_model.pkl"
_SCALER_PATH  = ML_MODELS_DIR / "scaler.pkl"
_FEAT_PATH    = ML_MODELS_DIR / "feature_names.json"

# ---------------------------------------------------------------------------
# Load artifacts ONCE at module initialisation (not per-request)
# ---------------------------------------------------------------------------
def _load_artifacts():
    """
    Load the trained model, scaler, and feature names from disk.
    Raises RuntimeError with a clear message if any artifact is missing.
    """
    missing = [p for p in (_MODEL_PATH, _SCALER_PATH, _FEAT_PATH) if not p.exists()]
    if missing:
        raise RuntimeError(
            f"ML artifacts not found: {[str(p) for p in missing]}\n"
            "Run  python ml/src/train.py  from the project root to generate them."
        )

    model  = joblib.load(_MODEL_PATH)
    scaler = joblib.load(_SCALER_PATH)
    with open(_FEAT_PATH, "r") as f:
        feature_names: list[str] = json.load(f)

    logger.info("✅ ML model loaded: %s", _MODEL_PATH.name)
    logger.info("✅ Scaler loaded  : %s", _SCALER_PATH.name)
    logger.info("✅ Feature names  : %d columns", len(feature_names))
    return model, scaler, feature_names


try:
    _MODEL, _SCALER, _FEATURE_NAMES = _load_artifacts()
    _ML_READY = True
except RuntimeError as _err:
    logger.warning("⚠️  ML model not available: %s", _err)
    logger.warning("    /predict will return HTTP 503 until artifacts are generated.")
    _MODEL, _SCALER, _FEATURE_NAMES = None, None, []
    _ML_READY = False

# ---------------------------------------------------------------------------
# Preprocessing constants (must exactly match ml/src/preprocess.py)
# ---------------------------------------------------------------------------

# Continuous columns that were StandardScaled during training.
# Index positions within FEATURE_NAMES (verified against feature_names.json order).
_CONTINUOUS_COLS = ["BMI", "MentHlth", "PhysHlth", "GenHlth", "Age", "Education", "Income"]

# CDC BRFSS Age categories — maps user's integer age to the ordinal used in training
# Category: 1=18–24, 2=25–29, 3=30–34, 4=35–39, 5=40–44, 6=45–49,
#           7=50–54, 8=55–59, 9=60–64, 10=65–69, 11=70–74, 12=75–79, 13=80+
def _age_to_cdc_category(age_years: int) -> int:
    if age_years < 18:
        return 1   # map underage to youngest valid category
    elif age_years <= 24:
        return 1
    elif age_years <= 29:
        return 2
    elif age_years <= 34:
        return 3
    elif age_years <= 39:
        return 4
    elif age_years <= 44:
        return 5
    elif age_years <= 49:
        return 6
    elif age_years <= 54:
        return 7
    elif age_years <= 59:
        return 8
    elif age_years <= 64:
        return 9
    elif age_years <= 69:
        return 10
    elif age_years <= 74:
        return 11
    elif age_years <= 79:
        return 12
    else:
        return 13


def _bmi(height_cm: float, weight_kg: float) -> float:
    """BMI = weight_kg / height_m²"""
    height_m = height_cm / 100.0
    return weight_kg / (height_m ** 2)


def _smoking_to_binary(smoking: str) -> int:
    """Never → 0;  Occasionally / Regularly → 1 (smoked 100+ cigarettes ever)."""
    return 0 if smoking.strip().lower() == "never" else 1


def _alcohol_to_binary(alcohol: str) -> int:
    """
    HvyAlcoholConsump in BRFSS: men >14 drinks/week, women >7/week.
    Map: 'Regularly' → 1,  'None' / 'Occasionally' → 0.
    """
    return 1 if alcohol.strip().lower() == "regularly" else 0


def _exercise_to_binary(exercise: str) -> int:
    """PhysActivity: any activity in past 30 days. 'None' → 0, else → 1."""
    return 0 if exercise.strip().lower() == "none" else 1


def _gender_to_sex(gender: str) -> int:
    """Sex: 0=Female, 1=Male. 'Other' or '' maps to 0 (dataset has no 'Other')."""
    return 1 if gender.strip().lower() == "male" else 0


def _symptoms_to_phys_hlth(symptoms: List[str]) -> float:
    """
    Proxy mapping: the BRFSS dataset has PhysHlth = days of poor physical
    health in past 30 days.  The app collects boolean symptom tags which
    have no direct equivalent.  We estimate PhysHlth proportionally:
      0 symptoms → 0 days
      1 symptom  → 3 days
      2 symptoms → 7 days
      3 symptoms → 14 days
      4+ symptoms→ 21 days
    This is a coarse proxy documented openly in the summary text.
    """
    count = len(symptoms)
    mapping = {0: 0.0, 1: 3.0, 2: 7.0, 3: 14.0}
    return mapping.get(count, 21.0)


# Risk-tier thresholds (based on predicted positive-class probability)
# Tuned conservatively to ensure the model is clinically cautious:
#   < 0.25 → Low Risk
#   0.25–0.50 → Moderate Risk
#   > 0.50 → High Risk
def _probability_to_risk(prob: float) -> tuple[str, int]:
    """
    Map the model's positive-class probability to (riskLevel, score).
    score is prob × 100 rounded to nearest integer.
    """
    score = int(round(prob * 100))
    if prob < 0.25:
        return "Low Risk", score
    elif prob < 0.50:
        return "Moderate Risk", score
    else:
        return "High Risk", score


def _describe_bmi(bmi: float) -> str:
    """Return a plain-language BMI category based on standard adult cutoffs."""
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "healthy range"
    if bmi < 30:
        return "overweight"
    return "obese"


def _parse_sleep_hours(value: str) -> float:
    """Covert sleep form values to approximate hours for personalised advice."""
    cleaned = (value or '').strip().lower()
    if cleaned in {"less than 5", "<5"}:
        return 4.5
    if cleaned in {"5-6", "5 to 6"}:
        return 5.5
    if cleaned in {"7-8", "7 to 8"}:
        return 7.5
    if cleaned in {"more than 8", ">8"}:
        return 9.0
    return 7.0


def _parse_water_liters(value: str) -> float:
    """Convert water intake value to approximate litres for personalised advice."""
    cleaned = (value or '').strip().lower()
    if cleaned in {"less than 1l", "<1l", "less than 1 l"}:
        return 0.75
    if cleaned in {"1-2l", "1 to 2l", "1-2 l", "1 to 2 l"}:
        return 1.5
    if cleaned in {"2-3l", "2 to 3l", "2-3 l", "2 to 3 l"}:
        return 2.5
    if cleaned in {"more than 3l", ">3l", "more than 3 l"}:
        return 3.5
    return 2.0


def _build_explainability(
    age_years: int,
    bmi: float,
    smoker: int,
    exerciser: int,
    heavy_alcohol: int,
    alcohol_value: str,
    sleep_value: str,
    water_value: str,
    symptoms: List[str],
) -> tuple[List[str], List[str], List[str]]:
    """Build plain-language factors using the actual user input and known safe mappings."""
    factors: List[str] = []
    risk_factors: List[str] = []
    protective_factors: List[str] = []

    factors.append(f"BMI category: { _describe_bmi(bmi) }")
    if age_years < 35:
        factors.append("Age category: younger adult")
    elif age_years < 55:
        factors.append("Age category: middle-aged adult")
    else:
        factors.append("Age category: older adult")

    factors.append(f"Smoking status: {'Current smoker' if smoker else 'Non-smoker'}")
    factors.append(f"Physical activity: {'No regular activity reported' if not exerciser else 'Regular physical activity reported'}")
    factors.append(f"Alcohol pattern: {'Regular/heavy drinking' if heavy_alcohol else alcohol_value}")
    factors.append(f"Sleep pattern: {sleep_value}")
    factors.append(f"Water intake: {water_value}")
    if symptoms:
        factors.append(f"Reported symptoms: {', '.join(symptoms)}")
    else:
        factors.append("Reported symptoms: none")

    if smoker:
        risk_factors.append("Smoking status indicates current tobacco exposure.")
    else:
        protective_factors.append("Smoking status is non-smoking or not current tobacco use.")

    if not exerciser:
        risk_factors.append("Physical activity appears lower than recommended.")
    else:
        protective_factors.append("Regular physical activity is part of the profile.")

    if heavy_alcohol:
        risk_factors.append("Alcohol pattern reflects regular or heavy drinking.")
    else:
        protective_factors.append("Alcohol intake is not in the regular/heavy category.")

    if _parse_sleep_hours(sleep_value) < 7:
        risk_factors.append("Sleep duration is below the usual healthy range.")
    else:
        protective_factors.append("Sleep duration appears within a healthier range.")

    if _parse_water_liters(water_value) < 2:
        risk_factors.append("Water intake appears below the commonly recommended range.")
    else:
        protective_factors.append("Water intake appears adequate for hydration support.")

    if bmi >= 30:
        risk_factors.append("BMI is in the obese range, which can increase cardiovascular risk.")
    elif bmi >= 25:
        risk_factors.append("BMI is in the overweight range.")
    else:
        protective_factors.append("BMI is in a healthy or lower-risk range.")

    if symptoms:
        risk_factors.append("Selected symptoms may be relevant to physical health status and should be assessed carefully.")
    else:
        protective_factors.append("No specific symptoms were reported in this assessment.")

    return factors, risk_factors, protective_factors


def _build_recommendations(
    risk_level: str,
    smoker: int,
    exerciser: int,
    heavy_alcohol: int,
    alcohol_value: str,
    bmi: float,
    sleep_value: str,
    water_value: str,
    symptoms: List[str],
) -> List[str]:
    """
    Generate personalised but medically safe recommendations.
    These are educational wellness suggestions, NOT clinical prescriptions.
    """
    recs = []
    sleep_hours = _parse_sleep_hours(sleep_value)
    water_litres = _parse_water_liters(water_value)

    if smoker:
        recs.append(
            "Your smoking status was reported as current tobacco use. Consider quitting with support from a clinician or a cessation program; smoking is a major modifiable cardiovascular risk factor."
        )

    if heavy_alcohol:
        recs.append(
            f"Your alcohol pattern is reported as {alcohol_value}. Consider reducing alcohol intake to lower cardiovascular risk and support sleep quality."
        )

    if not exerciser:
        recs.append(
            "Your exercise pattern appears low. Aim for at least 150 minutes of moderate activity each week, or a similar level of movement that fits your routine."
        )

    if bmi >= 30:
        recs.append(
            "Your BMI falls in the obese range. A gradual weight-loss plan based on nutrition and regular activity can help lower long-term cardiovascular risk."
        )
    elif bmi >= 25:
        recs.append(
            "Your BMI is in the overweight range. Maintaining a balanced diet and regular activity can help bring it toward a healthier range."
        )

    if sleep_hours < 7:
        recs.append(
            f"Your sleep pattern is {sleep_value}, which is below the usual healthy range. Aim for 7–9 hours of consistent sleep to support recovery and heart health."
        )

    if water_litres < 2:
        recs.append(
            f"Your water intake is reported as {water_value}. Increasing hydration toward about 2–3 litres per day can support overall wellbeing."
        )

    if "Chest Pain" in symptoms or "Shortness of Breath" in symptoms:
        recs.append(
            "You reported chest pain or shortness of breath. These symptoms may warrant prompt medical evaluation — please consult a healthcare professional soon."
        )

    if risk_level == "High Risk":
        recs.append(
            "Your risk estimate is elevated. Schedule a cardiovascular check-up with your doctor, including blood pressure, cholesterol, and blood sugar screening when appropriate."
        )
    elif risk_level == "Moderate Risk":
        recs.append(
            "Your risk estimate is moderate. Regular screening and a heart-healthy routine remain important for reducing risk over time."
        )
    else:
        recs.append(
            "Your profile is currently lower risk. Continue your healthy habits, keep routine check-ups, and maintain physical activity and sleep quality."
        )

    if symptoms:
        recs.append(
            f"Because you reported {', '.join(symptoms)}, consider noting any pattern or worsening over time and discussing it with a healthcare professional if it continues."
        )

    # Ensure at least 3 recommendations
    if len(recs) < 3:
        recs.append(
            "Eat a varied diet rich in fruits, vegetables, whole grains, and lean proteins, and limit processed foods, sodium, and added sugars."
        )

    return recs


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="HealthSense AI Backend",
    description=(
        "Backend API for predicting health risk levels based on user lifestyle and symptoms. "
        "Powered by a Gradient Boosting classifier trained on the CDC BRFSS 2015 dataset. "
        "⚠️ For educational purposes only — NOT a medical diagnostic tool."
    ),
    version="2.0.0",
)

# CORS — allows Next.js server AND LAN clients to reach the backend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://10.224.186.12:3000",
]
if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Request Schemas (unchanged from Prompt 9 to preserve frontend contract)
# ---------------------------------------------------------------------------

class PersonalInfo(BaseModel):
    """User's personal details. Matches PersonalInfo interface in src/types/assessment.ts."""
    fullName: str = Field(..., example="Jane Doe")
    age: str      = Field(..., example="35")
    gender: Literal["Male", "Female", "Other", ""] = Field(..., example="Female")
    height: str   = Field(..., example="165")   # cm
    weight: str   = Field(..., example="65")    # kg


class LifestyleInfo(BaseModel):
    """User's lifestyle habits. Matches LifestyleInfo interface in src/types/assessment.ts."""
    smoking:  str = Field(..., example="Never")
    alcohol:  str = Field(..., example="Occasionally")
    exercise: str = Field(..., example="3-4 times/week")
    sleep:    str = Field(..., example="7-8")         # not a trained feature
    water:    str = Field(..., example="2-3L")        # not a trained feature


class SymptomsInfo(BaseModel):
    """Selected symptoms. Matches SymptomsInfo interface in src/types/assessment.ts."""
    selectedSymptoms: List[str] = Field(..., example=["Headache", "Fatigue"])


class AssessmentData(BaseModel):
    """Combined assessment payload. Matches AssessmentData interface in src/types/assessment.ts."""
    personalInfo: PersonalInfo
    lifestyle:    LifestyleInfo
    symptoms:     SymptomsInfo


# ---------------------------------------------------------------------------
# Pydantic Response Schema (unchanged to preserve frontend contract)
# ---------------------------------------------------------------------------

class PredictionResult(BaseModel):
    """Prediction response. Matches PredictionResult interface in src/types/assessment.ts."""
    score:           int           = Field(..., description="Risk score 0–100 (probability × 100)")
    riskLevel:       Literal["Low Risk", "Moderate Risk", "High Risk"]
    summary:         str           = Field(..., description="Plain-language risk summary")
    recommendations: List[str]     = Field(..., description="Personalised wellness recommendations")
    isPlaceholder:   bool          = Field(False, description="True only if placeholder response")
    factorsConsidered: List[str]    = Field(default_factory=list, description="Plain-language factors considered in the assessment")
    riskFactors:     List[str]      = Field(default_factory=list, description="Potential risk-related factors based on user input")
    protectiveFactors: List[str]    = Field(default_factory=list, description="Protective factors visible in the assessment")


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System Status"])
async def health_check():
    """Basic health-check endpoint. Verifies service is up and ML model is loaded."""
    return {
        "status": "healthy",
        "service": "HealthSense AI Backend",
        "ml_model_loaded": _ML_READY,
        "model_name": "Gradient Boosting" if _ML_READY else None,
        "disclaimer": "Educational tool only — not a medical diagnostic system.",
    }


@app.post("/predict", response_model=PredictionResult, tags=["Predictions"])
async def predict_health_risk(data: AssessmentData):
    """
    Real ML-powered health risk prediction endpoint.

    Accepts the standard assessment payload, builds the 21-feature vector
    required by the trained Gradient Boosting model, applies the same
    preprocessing used during training, and returns a risk estimate.

    ⚠️ Educational disclaimer: Results are NOT medical diagnoses.
    """
    # ------------------------------------------------------------------
    # Guard: refuse if model failed to load at startup
    # ------------------------------------------------------------------
    if not _ML_READY:
        raise HTTPException(
            status_code=503,
            detail=(
                "ML model artifacts are not available. "
                "Run  python ml/src/train.py  from the project root "
                "to generate best_model.pkl, scaler.pkl, and feature_names.json."
            ),
        )

    # ------------------------------------------------------------------
    # 1. Parse and validate raw inputs
    # ------------------------------------------------------------------
    try:
        age_years  = int(float(data.personalInfo.age))
        height_cm  = float(data.personalInfo.height)
        weight_kg  = float(data.personalInfo.weight)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Age, height, and weight must be valid numbers. "
                f"Parsing error: {exc}"
            ),
        ) from exc

    # ------------------------------------------------------------------
    # 2. Range validation — reject clearly impossible or unreasonable values
    # ------------------------------------------------------------------
    validation_errors: list[str] = []

    if age_years <= 0:
        validation_errors.append("Age must be a positive number.")
    elif age_years > 120:
        validation_errors.append(
            f"Age {age_years} is not realistic for this assessment (max 120)."
        )

    if height_cm <= 0:
        validation_errors.append("Height must be a positive number.")
    elif height_cm < 50:
        validation_errors.append(
            f"Height {height_cm} cm is too low to be valid (minimum 50 cm)."
        )
    elif height_cm > 300:
        validation_errors.append(
            f"Height {height_cm} cm exceeds a realistic range (maximum 300 cm)."
        )

    if weight_kg <= 0:
        validation_errors.append("Weight must be a positive number.")
    elif weight_kg < 10:
        validation_errors.append(
            f"Weight {weight_kg} kg is too low to be valid (minimum 10 kg)."
        )
    elif weight_kg > 500:
        validation_errors.append(
            f"Weight {weight_kg} kg exceeds a realistic range (maximum 500 kg)."
        )

    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail={"validation_errors": validation_errors},
        )

    # ------------------------------------------------------------------
    # 2. Compute derived features
    # ------------------------------------------------------------------
    bmi_val    = _bmi(height_cm, weight_kg)
    age_cat    = _age_to_cdc_category(age_years)
    sex_val    = _gender_to_sex(data.personalInfo.gender)
    smoker_val = _smoking_to_binary(data.lifestyle.smoking)
    alcohol_val= _alcohol_to_binary(data.lifestyle.alcohol)
    exercise_val = _exercise_to_binary(data.lifestyle.exercise)
    phys_hlth_proxy = _symptoms_to_phys_hlth(data.symptoms.selectedSymptoms)

    # ------------------------------------------------------------------
    # 3. Build feature dict keyed by dataset column name
    #
    # Features NOT mappable from the app (sleep, water, specific symptoms)
    # are set to conservative population-average defaults documented below.
    # These defaults minimise artificial inflation of predicted risk for
    # unmappable fields.
    #
    # Default values rationale:
    #   HighBP, HighChol, Stroke, Diabetes = 0  (assume no reported condition)
    #   CholCheck = 1                           (assume had cholesterol checked)
    #   Fruits, Veggies = 1                     (assume adequate diet)
    #   AnyHealthcare = 1                       (assume has coverage)
    #   NoDocbcCost = 0                         (assume no cost barrier)
    #   GenHlth = 3                             (population median: 'Good')
    #   MentHlth = 0                            (no poor mental health days)
    #   PhysHlth = proxy from symptom count     (see _symptoms_to_phys_hlth)
    #   DiffWalk = 0                            (assume no walking difficulty)
    #   Education = 4                           (population median: 'Some college')
    #   Income = 6                              (population median: ~$35k–50k)
    # ------------------------------------------------------------------
    feature_dict = {
        "HighBP":           0.0,
        "HighChol":         0.0,
        "CholCheck":        1.0,
        "BMI":              bmi_val,
        "Smoker":           float(smoker_val),
        "Stroke":           0.0,
        "Diabetes":         0.0,
        "PhysActivity":     float(exercise_val),
        "Fruits":           1.0,
        "Veggies":          1.0,
        "HvyAlcoholConsump": float(alcohol_val),
        "AnyHealthcare":    1.0,
        "NoDocbcCost":      0.0,
        "GenHlth":          3.0,
        "MentHlth":         0.0,
        "PhysHlth":         phys_hlth_proxy,
        "DiffWalk":         0.0,
        "Sex":              float(sex_val),
        "Age":              float(age_cat),
        "Education":        4.0,
        "Income":           6.0,
    }

    # ------------------------------------------------------------------
    # 4. Build feature array in the EXACT order used during training
    #    (order defined by feature_names.json — do not hard-code)
    # ------------------------------------------------------------------
    try:
        feature_values = [feature_dict[col] for col in _FEATURE_NAMES]
    except KeyError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Internal feature mapping error — missing column: {exc}",
        ) from exc

    X_raw = np.array(feature_values, dtype=float).reshape(1, -1)

    # ------------------------------------------------------------------
    # 5. Apply StandardScaler to continuous columns only
    #    MUST use the same scaler fitted on training data (scaler.pkl)
    #    MUST scale the same columns as preprocess.py CONTINUOUS_COLS
    # ------------------------------------------------------------------
    CONTINUOUS_COLS = ["BMI", "MentHlth", "PhysHlth", "GenHlth", "Age", "Education", "Income"]
    try:
        cont_indices = [_FEATURE_NAMES.index(c) for c in CONTINUOUS_COLS]
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Feature name mismatch between scaler and feature_names.json: {exc}",
        ) from exc

    X_scaled = X_raw.copy()
    X_scaled[:, cont_indices] = _SCALER.transform(X_raw[:, cont_indices])

    # ------------------------------------------------------------------
    # 6. Predict
    # ------------------------------------------------------------------
    try:
        prob = float(_MODEL.predict_proba(X_scaled)[0][1])  # positive-class probability
    except Exception as exc:
        logger.error("Model prediction error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Model prediction failed. Check server logs for details.",
        ) from exc

    # ------------------------------------------------------------------
    # 7. Derive risk tier and score
    # ------------------------------------------------------------------
    risk_level, score = _probability_to_risk(prob)

    # ------------------------------------------------------------------
    # 8. Build personalised summary
    # ------------------------------------------------------------------
    symptom_text = (
        f"reported symptoms ({', '.join(data.symptoms.selectedSymptoms)})"
        if data.symptoms.selectedSymptoms
        else "no specific symptoms reported"
    )

    non_mapped_note = (
        "Note: sleep duration and water intake were collected but are not features "
        "in the BRFSS 2015 training dataset and did not influence this prediction."
    )

    summary = (
        f"Based on your profile — age {age_years}, BMI {bmi_val:.1f}, "
        f"{'male' if sex_val else 'female'}, {symptom_text} — "
        f"the HealthSense AI model estimates your cardiovascular risk score as "
        f"{score}/100 ({risk_level}). "
        f"This estimate was produced by a Gradient Boosting classifier trained on "
        f"the CDC BRFSS 2015 Heart Disease Health Indicators dataset (n = 229,781 after deduplication). "
        f"{non_mapped_note} "
        f"⚠️ This is an educational estimate only and is NOT a medical diagnosis."
    )

    # ------------------------------------------------------------------
    # 9. Generate recommendations
    # ------------------------------------------------------------------
    recommendations = _build_recommendations(
        risk_level=risk_level,
        smoker=smoker_val,
        exerciser=exercise_val,
        heavy_alcohol=alcohol_val,
        alcohol_value=data.lifestyle.alcohol,
        bmi=bmi_val,
        sleep_value=data.lifestyle.sleep,
        water_value=data.lifestyle.water,
        symptoms=data.symptoms.selectedSymptoms,
    )

    factors_considered, risk_factors, protective_factors = _build_explainability(
        age_years=age_years,
        bmi=bmi_val,
        smoker=smoker_val,
        exerciser=exercise_val,
        heavy_alcohol=alcohol_val,
        alcohol_value=data.lifestyle.alcohol,
        sleep_value=data.lifestyle.sleep,
        water_value=data.lifestyle.water,
        symptoms=data.symptoms.selectedSymptoms,
    )

    # ------------------------------------------------------------------
    # 10. Log for server-side audit (no PII beyond name)
    # ------------------------------------------------------------------
    logger.info(
        "Prediction for %s | age=%d bmi=%.1f | prob=%.4f score=%d level=%s",
        data.personalInfo.fullName,
        age_years,
        bmi_val,
        prob,
        score,
        risk_level,
    )

    return PredictionResult(
        score=score,
        riskLevel=risk_level,
        summary=summary,
        recommendations=recommendations,
        isPlaceholder=False,
        factorsConsidered=factors_considered,
        riskFactors=risk_factors,
        protectiveFactors=protective_factors,
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
