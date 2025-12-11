import joblib
import os

# adjust these paths if your model files are in different locations
MODEL_PATH = os.path.join("backend", "ml", "models", "apk_classifier.pkl")
VECT_PATH = os.path.join("backend", "ml", "preprocessing", "vectorizer.pkl")

# load once on import
_model = None
_vectorizer = None

def _ensure_loaded():
    global _model, _vectorizer
    if _model is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECT_PATH):
            raise FileNotFoundError("Model or vectorizer not found. Expected at: "
                                    f"{MODEL_PATH}, {VECT_PATH}")
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECT_PATH)

def predict_from_permissions(permissions):
    """
    permissions: list of permission tokens e.g. ['INTERNET','READ_SMS']
    returns: dict {prediction: 0/1, confidence: float}
    """
    _ensure_loaded()
    perms_text = " ".join(permissions)
    x = _vectorizer.transform([perms_text])
    pred = _model.predict(x)[0]
    proba = None
    try:
        proba = float(max(_model.predict_proba(x)[0]))
    except Exception:
        proba = None

    return {"prediction": int(pred), "confidence": proba}
