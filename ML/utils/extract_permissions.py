from androguard.misc import AnalyzeAPK

def extract_permissions(apk_path: str):
    """
    Extract permissions from an APK file.
    Returns a Python list of permissions.
    """
    a, d, dx = AnalyzeAPK(apk_path)
    permissions = a.get_permissions()
    return permissions
