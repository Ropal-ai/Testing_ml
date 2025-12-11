from androguard.core.bytecodes.apk import APK

def extract_apk_info(file_path):
    """
    Use androguard to extract manifest info. Returns a dict with:
    - app_name, package_name, version, permissions (list), activities, services, receivers
    """
    try:
        apk = APK(file_path)
        app_name = apk.get_app_name()
        package_name = apk.get_package()
        version = apk.get_androidversion_name()
        permissions = apk.get_permissions() or []
        # normalize: take last token (android.permission.INTERNET -> INTERNET)
        permissions = [p.split(".")[-1] for p in permissions]

        activities = apk.get_activities() or []
        services = apk.get_services() or []
        receivers = apk.get_receivers() or []

        return {
            "app_name": app_name,
            "package_name": package_name,
            "version": version,
            "permissions": permissions,
            "activities": activities,
            "services": services,
            "receivers": receivers
        }
    except Exception as e:
        # return minimal dict on failure
        return {
            "app_name": None,
            "package_name": None,
            "version": None,
            "permissions": [],
            "activities": [],
            "services": [],
            "receivers": [],
            "error": str(e)
        }
