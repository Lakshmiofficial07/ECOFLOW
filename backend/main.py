"""
EcoFlow AI — Python Backend (FastAPI)

Serves all API endpoints for waste analysis, chat, complaints,
route planning, admin reports, and policy document management.

Run with:
    uvicorn main:app --reload --port 8000
"""

from pathlib import Path
from dotenv import load_dotenv

# Load environment variables before importing route modules
# so they can read GROQ_API_KEY and HF_TOKEN at module level.
backend_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=backend_dir.parent / ".env.local")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.admin_report import router as admin_report_router
from routes.analyze_waste import router as analyze_waste_router
from routes.chat import router as chat_router
from routes.complaint import router as complaint_router
from routes.policy_db import router as policy_db_router
from routes.route_plan import router as route_plan_router
from routes.upload_policy import router as upload_policy_router

app = FastAPI(
    title="EcoFlow AI Backend",
    description="Intelligent Waste Management API for Kerala Panchayats",
    version="1.0.0",
)

# CORS — allow the Next.js dev server and any local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route modules
app.include_router(analyze_waste_router)
app.include_router(chat_router)
app.include_router(complaint_router)
app.include_router(route_plan_router)
app.include_router(admin_report_router)
app.include_router(upload_policy_router)
app.include_router(policy_db_router)


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "EcoFlow AI Backend"}
