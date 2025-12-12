from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()


from app.routers import upload, analyze, explain

app = FastAPI(
    title="CyberGuardian APK Analyzer",
    description="AI + static analysis APK scanner",
    version="1.0"
)

# CORS (allow all during hackathon; lock down in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# mount routers
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(analyze.router, prefix="/analyze", tags=["Analyze"])
app.include_router(explain.router, prefix="/explain", tags=["Explain"])

@app.get("/")
def root():
    return {"status": "ok", "service": "CyberGuardian APK Analyzer"}
