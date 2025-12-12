import joblib
import os

current_file_dir = os.path.dirname(os.path.abspath(__file__))

BACKEND_ROOT = os.path.dirname(os.path.dirname(current_file_dir))

MODEL_PATH = os.path.join(BACKEND_ROOT, "ml", "models", "apk_classifier.pkl")
VECT_PATH = os.path.join(BACKEND_ROOT, "ml", "preprocessing", "permission_columns.pkl")

# load once on import
_model = None
_vectorizer = None

def _ensure_loaded():
    global _model, _vectorizer
    if _model is None:
        print(f"DEBUG: Looking for model at: {MODEL_PATH}")
        print(f"DEBUG: Looking for vectorizer at: {VECT_PATH}")
        
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECT_PATH):
            raise FileNotFoundError(
                f"Model or vectorizer not found.\n"
                f"Checked Model Path: {MODEL_PATH}\n"
                f"Checked Vectorizer Path: {VECT_PATH}"
            )
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECT_PATH)
        print("DEBUG: Model and Vectorizer loaded successfully!")

def predict_from_permissions(permissions):
    """
    permissions: list of permission tokens e.g. ['INTERNET','READ_SMS']
    returns: dict {prediction: 0/1, confidence: float}
    """
    _ensure_loaded()
    perms_text = " ".join(permissions)
    
    # Handle different vectorizer types just in case
    try:
        x = _vectorizer.transform([perms_text])
    except AttributeError:
        # If vectorizer is just a list of columns
        import pandas as pd
        x = pd.DataFrame(0, index=[0], columns=_vectorizer)
        for p in permissions:
            if p in x.columns:
                x.loc[0, p] = 1

    pred = _model.predict(x)[0]
    proba = None
    try:
        proba = float(max(_model.predict_proba(x)[0]))
    except Exception:
        proba = None

    return {"prediction": int(pred), "confidence": proba}