from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import Base, engine
from app.routers import procedures, irradiation, operators, frames, teaching, analytics, search

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IR Procedure Platform API",
    description="IR Procedure Intelligence Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(procedures.router, prefix="/api/procedures", tags=["procedures"])
app.include_router(irradiation.router, prefix="/api/irradiation", tags=["irradiation"])
app.include_router(operators.router, prefix="/api/operators", tags=["operators"])
app.include_router(frames.router, prefix="/api/frames", tags=["frames"])
app.include_router(teaching.router, prefix="/api/teaching", tags=["teaching"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

@app.get("/")
def read_root():
    return {"message": "IR Procedure Platform API - IR Procedure Intelligence Platform"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
