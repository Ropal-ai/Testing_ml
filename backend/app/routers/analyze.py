from fastapi import APIRouter, HTTPException, File, UploadFile
import os
import logging
import shutil
from pathlib import Path

from app.services.apk_extractor import extract_apk_info
from app.services.permission_checker import analyze_permissions
from app.services.ml_model import predict_from_permissions
from app.services.report_builder import build_report

logger = logging.getLogger(__name__)
router = APIRouter()

# REMOVE the AnalyzeRequest class, we use UploadFile now

@router.post("/")
async def analyze_apk(file: UploadFile = File(...)): # Changed to accept actual file
    # 1. Create a safe temp path
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / file.filename

    try:
        # 2. Save the uploaded file bytes to disk
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Starting analysis for uploaded file: {file.filename}")

        # 3. Extract Info (using the local path we just saved)
        apk_info = extract_apk_info(str(file_path))

        if apk_info.get("app_name") is None:
            error_msg = apk_info.get('error', 'Unknown error')
            logger.error(f"Extraction failed: {error_msg}")
            raise HTTPException(status_code=400, detail=f"Failed to parse APK: {error_msg}")

        # 4. Static Analysis & ML Prediction
        permissions = apk_info.get("permissions", [])
        perm_risks = analyze_permissions(permissions)
        ml_out = predict_from_permissions(permissions)

        # 5. Build Report
        report = build_report(apk_info, perm_risks, ml_out)
        
        return report

    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 6. CLEANUP
        if file_path.exists():
            os.remove(file_path)
            logger.info(f"🗑️ Deleted temporary file: {file_path}")
