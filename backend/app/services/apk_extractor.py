import logging
# Make sure to use the correct import for Androguard 4.x
from androguard.core.apk import APK  

logger = logging.getLogger(__name__)

def extract_apk_info(file_path):
    """
    Use androguard to extract manifest info.
    """
    logger.info(f"Starting analysis for file: {file_path}")
    
    try:
        apk = APK(file_path)
        app_name = apk.get_app_name()
        package_name = apk.get_package()
        version = apk.get_androidversion_name()
        
        raw_perms = apk.get_permissions() or []
        # normalize: take last token (android.permission.INTERNET -> INTERNET)
        permissions = [p.split(".")[-1] for p in raw_perms]

        activities = apk.get_activities() or []
        services = apk.get_services() or []
        receivers = apk.get_receivers() or []

        logger.info(f"Successfully parsed APK: {package_name} (v{version})")
        logger.debug(f"Found {len(permissions)} permissions")

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
        # Log the full error traceback so you can debug it later
        logger.error(f"❌ Failed to extract APK info from {file_path}: {e}", exc_info=True)
        
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