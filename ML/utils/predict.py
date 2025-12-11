import joblib
from ml.utils.preprocess import permissions_to_vector

MODEL_PATH = "ml/models/apk_classifier.pkl"

# Load model once (for fast API performance)
model = joblib.load(MODEL_PATH)

def predict_from_permissions(permissions):
    """
    Convert permissions to vector → ML model prediction.
    Returns:
        label (str)
        confidence (float)
    """
    X = permissions_to_vector(permissions)
    prediction = model.predict(X)[0]
    proba = model.predict_proba(X)[0]

    label = "Benign (SAFE)" if prediction == 0 else "Malware (DANGEROUS)"
    confidence = float(proba[prediction])

    return label, confidence
