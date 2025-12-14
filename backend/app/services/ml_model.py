import joblib
import os
import logging
import pandas as pd

# Initialize logger for this module
logger = logging.getLogger(__name__)

current_file_dir = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(os.path.dirname(current_file_dir))

MODEL_PATH = os.path.join(BACKEND_ROOT, "ml", "models", "apk_classifier.pkl")
VECT_PATH = os.path.join(BACKEND_ROOT, "ml", "preprocessing", "permission_columns.pkl")

_model = None
_vectorizer = None

def _ensure_loaded():
    global _model, _vectorizer
    if _model is None:
        logger.info(f"Loading ML resources...")
        logger.debug(f"Model Path: {MODEL_PATH}")
        logger.debug(f"Vectorizer Path: {VECT_PATH}")
        
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECT_PATH):
            logger.critical("Model or vectorizer file missing!")
            raise FileNotFoundError(
                f"Model or vectorizer not found.\n"
                f"Checked Model Path: {MODEL_PATH}\n"
                f"Checked Vectorizer Path: {VECT_PATH}"
            )
        
        try:
            _model = joblib.load(MODEL_PATH)
            _vectorizer = joblib.load(VECT_PATH)
            logger.info("✅ Model and Vectorizer loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model files: {e}")
            raise e

def predict_from_permissions(permissions):
    """
    permissions: list of permission tokens e.g. ['INTERNET','READ_SMS']
    returns: dict {prediction: 0/1, confidence: float}
    """
    _ensure_loaded()
    
    # Log the input (useful for debugging, change to DEBUG in production)
    logger.info(f"Running prediction on {len(permissions)} permissions")
    
    perms_text = " ".join(permissions)
    
    try:
        # Handle different vectorizer types
        try:
            x = _vectorizer.transform([perms_text])
        except AttributeError:
            # Fallback for list-based vectorizer
            x = pd.DataFrame(0, index=[0], columns=_vectorizer)
            for p in permissions:
                if p in x.columns:
                    x.loc[0, p] = 1

        pred = _model.predict(x)[0]
        
        try:
            proba = float(max(_model.predict_proba(x)[0]))
        except Exception:
            proba = 0.0

        logger.info(f"Prediction Result: Class={pred}, Confidence={proba:.2f}")
        return {"prediction": int(pred), "confidence": proba}

    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return {"prediction": -1, "confidence": 0.0}