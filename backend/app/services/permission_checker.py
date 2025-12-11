# quick mapping for dangerous permissions
DANGEROUS_PERMISSIONS = {
    "READ_SMS": "Can read your SMS messages.",
    "SEND_SMS": "Can send SMS messages without your consent.",
    "RECORD_AUDIO": "Can record audio using microphone.",
    "READ_CONTACTS": "Can access your contacts.",
    "ACCESS_FINE_LOCATION": "Can access precise GPS location.",
    "READ_CALL_LOG": "Can read call logs.",
    "WRITE_EXTERNAL_STORAGE": "Can write external storage.",
    "READ_EXTERNAL_STORAGE": "Can read external storage.",
    "REQUEST_INSTALL_PACKAGES": "Can install packages (dangerous).",
    "SYSTEM_ALERT_WINDOW": "Can overlay on screen (phishing risk)."
}

def analyze_permissions(permission_list):
    """
    Return a list of detected dangerous permissions and their human-friendly text.
    """
    risks = []
    for perm in permission_list:
        if perm in DANGEROUS_PERMISSIONS:
            risks.append({"permission": perm, "description": DANGEROUS_PERMISSIONS[perm]})
    return risks
