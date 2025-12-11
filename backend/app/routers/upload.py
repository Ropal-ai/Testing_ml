from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil, os, uuid

router = APIRouter()

UPLOAD_DIR = "uploaded_apks"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_apk(file: UploadFile = File(...)):
    # basic validation
    if not file.filename.lower().endswith(".apk"):
        raise HTTPException(status_code=400, detail="Only .apk files are accepted")

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        with open(file_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
    finally:
        await file.close()

    return {"status": "ok", "file_path": file_path, "filename": file.filename}
