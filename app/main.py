from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uvicorn
from datetime import datetime, timedelta
import os

from .models import FinancialInput, MonthlyProjection, ProjectionResponse
from .calculations import calculate_projections

app = FastAPI(
    title="Financial Projection Tool",
    description="A comprehensive tool for financial planning and projections",
    version="1.0.0"
)

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/calculate-projection", response_model=ProjectionResponse)
async def calculate_financial_projection(data: FinancialInput):
    """Calculate financial projections based on user input"""
    try:
        return calculate_projections(data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/categories")
async def get_commitment_categories():
    """Get predefined commitment categories"""
    categories = [
        "Housing", "Transportation", "Food", "Utilities", "Insurance",
        "Healthcare", "Entertainment", "Shopping", "Education", "Debt", "Other"
    ]
    return {"categories": categories}

# Serve static files (frontend)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint serves the frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main application page"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>Financial Projection Tool</title></head>
            <body>
                <h1>Financial Projection Tool API</h1>
                <p>API is running! Frontend files not found in static directory.</p>
                <p>Visit <a href="/docs">/docs</a> for API documentation.</p>
            </body>
        </html>
        """)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )