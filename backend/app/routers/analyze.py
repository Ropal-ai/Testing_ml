from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

from app.services.apk_extractor import extract_apk_info
from app.services.permission_checker import analyze_permissions
from app.services.ml_model import predict_from_permissions
from app.services.report_builder import build_report

router = APIRouter()

class AnalyzeRequest(BaseModel):
    file_path: str

@router.post("/")
def analyze_apk(req: AnalyzeRequest):
    if not os.path.exists(req.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    apk_info = extract_apk_info(req.file_path)
    # apk_info contains permissions (list), activities, services, etc.
    perm_risks = analyze_permissions(apk_info.get("permissions", []))

    ml_out = predict_from_permissions(apk_info.get("permissions", []))
    report = build_report(apk_info, perm_risks, ml_out)

    return report
