import os

def validate_apk_path(path: str):
    """
    Check if APK exists and has correct extension.
    """
    if not os.path.exists(path):
        raise FileNotFoundError("APK file not found!")

    if not path.lower().endswith(".apk"):
        raise ValueError("Provided file is not an APK!")

    return True


def format_output(label, confidence):
    """
    Return a clean dictionary output for APIs/UI.
    """
    return {
        "prediction": label,
        "confidence": round(confidence, 4)
    }
