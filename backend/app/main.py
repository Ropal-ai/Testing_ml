import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 🔇 SILENCE NOISY LIBRARIES
# This specific line stops the huge flood of androguard DEBUG logs
logging.getLogger("androguard").setLevel(logging.WARNING)
logging.getLogger("multipart").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Create a logger for this file
logger = logging.getLogger(__name__)

load_dotenv()

from app.routers import upload, analyze, explain

app = FastAPI(
    title="CyberGuardian APK Analyzer",
    description="AI + static analysis APK scanner",
    version="1.0"
)

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

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 CyberGuardian Backend Started Successfully")

@app.get("/")
def root():
    logger.info("Health check endpoint called")
    return {"status": "ok", "service": "CyberGuardian APK Analyzer"}