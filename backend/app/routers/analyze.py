from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import logging

from app.services.apk_extractor import extract_apk_info
from app.services.permission_checker import analyze_permissions
from app.services.ml_model import predict_from_permissions
from app.services.report_builder import build_report

# Setup Logger
logger = logging.getLogger(__name__)

router = APIRouter()

class AnalyzeRequest(BaseModel):
    file_path: str

@router.post("/")
def analyze_apk(req: AnalyzeRequest):
    # 1. Validate existence
    if not os.path.exists(req.file_path):
        logger.warning(f"File not found for analysis: {req.file_path}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        logger.info(f"Starting analysis for: {req.file_path}")

        # 2. Extract Info
        apk_info = extract_apk_info(req.file_path)

        # Check if extraction failed (e.g., corrupt file)
        if apk_info.get("app_name") is None:
            error_msg = apk_info.get('error', 'Unknown error')
            logger.error(f"Extraction failed: {error_msg}")
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to parse APK. Error: {error_msg}"
            )

        # 3. Static Analysis (Permissions)
        permissions = apk_info.get("permissions", [])
        perm_risks = analyze_permissions(permissions)

        # 4. AI Prediction
        ml_out = predict_from_permissions(permissions)

        # 5. Build Report
        report = build_report(apk_info, perm_risks, ml_out)
        
        logger.info("Analysis complete. Sending report.")
        return report

    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise e  # Re-raise to let FastAPI handle the error response

    finally:
        # 6. CLEANUP: Delete the file
        # This block runs ALWAYS (success or failure)
        if os.path.exists(req.file_path):
            try:
                os.remove(req.file_path)
                logger.info(f"🗑️ Deleted temporary file: {req.file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to delete file {req.file_path}: {cleanup_error}")