def build_report(apk_info, perm_analysis, ml_prediction):
    """
    Combine objects into a single JSON-friendly report.
    """
    # simple risk score: model prediction + number of dangerous perms
    base = 0
    if ml_prediction.get("prediction") == 1:
        base += 60
    base += min(len(perm_analysis) * 8, 40)  # each dangerous perm adds up to 8 points
    risk_score = min(base, 100)

    verdict = "MALICIOUS" if risk_score >= 60 else ("SUSPICIOUS" if risk_score >= 35 else "LIKELY SAFE")

    return {
        "app_name": apk_info.get("app_name"),
        "package_name": apk_info.get("package_name"),
        "version": apk_info.get("version"),
        "permissions": apk_info.get("permissions"),
        "dangerous_permissions": perm_analysis,
        "ml_result": ml_prediction,
        "risk_score": risk_score,
        "verdict": verdict,
        "recommendation": "Do not install" if verdict in ("MALICIOUS","SUSPICIOUS") else "OK to install with caution"
    }
