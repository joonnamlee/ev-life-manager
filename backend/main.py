"""
EV Life Manager - Backend API
FastAPI-based REST API for EV battery healthcare platform
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import uuid4, UUID
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="EV Life Manager API",
    description="AI-powered EV Battery Healthcare Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Pydantic Models (Request/Response Schemas)
# ============================================================


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    phone: Optional[str]
    created_at: datetime


class VehicleCreate(BaseModel):
    user_id: UUID
    make: str = Field(..., max_length=50)
    model: str = Field(..., max_length=50)
    year: int = Field(..., ge=1900, le=2026)
    vin: str = Field(..., min_length=17, max_length=17)
    battery_capacity: float = Field(..., gt=0)


class VehicleResponse(BaseModel):
    id: UUID
    user_id: UUID
    make: str
    model: str
    year: int
    vin: str
    battery_capacity: float
    created_at: datetime


class BatteryLogCreate(BaseModel):
    vehicle_id: UUID
    soc: float = Field(..., ge=0, le=100)  # State of Charge
    soh: float = Field(..., ge=0, le=100)  # State of Health
    voltage: Optional[float] = Field(None, gt=0)
    temperature: Optional[float] = None
    health_score: Optional[float] = Field(None, ge=0, le=100)


class BatteryLogResponse(BaseModel):
    id: UUID
    vehicle_id: UUID
    soc: float
    soh: float
    voltage: Optional[float]
    temperature: Optional[float]
    health_score: Optional[float]
    recorded_at: datetime
    created_at: datetime


class ChargingSessionCreate(BaseModel):
    vehicle_id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    energy_consumed: Optional[float] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)


class ChargingSessionResponse(BaseModel):
    id: UUID
    vehicle_id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    energy_consumed: Optional[float]
    cost: Optional[float]
    created_at: datetime


# ============================================================
# In-Memory Storage (임시 데이터베이스)
# ============================================================

# 실제 프로덕션에서는 PostgreSQL을 사용합니다
users_db = {}
vehicles_db = {}
battery_logs_db = {}
charging_sessions_db = {}


# ============================================================
# API Endpoints
# ============================================================


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "EV Life Manager API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================
# User Endpoints
# ============================================================


@app.post(
    "/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate):
    """Create a new user"""
    user_id = uuid4()

    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    user_data = {
        "id": user_id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "created_at": datetime.now(),
    }

    users_db[user_id] = user_data

    return UserResponse(**user_data)


@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    """Get user by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse(**users_db[user_id])


@app.get("/api/users", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100):
    """List all users with pagination"""
    users_list = list(users_db.values())[skip : skip + limit]
    return [UserResponse(**user) for user in users_list]


# ============================================================
# Vehicle Endpoints
# ============================================================


@app.post(
    "/api/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED
)
async def create_vehicle(vehicle: VehicleCreate):
    """Register a new vehicle"""
    vehicle_id = uuid4()

    # Check if VIN already exists
    for existing_vehicle in vehicles_db.values():
        if existing_vehicle["vin"] == vehicle.vin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="VIN already registered"
            )

    vehicle_data = {
        "id": vehicle_id,
        "user_id": vehicle.user_id,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "vin": vehicle.vin,
        "battery_capacity": vehicle.battery_capacity,
        "created_at": datetime.now(),
    }

    vehicles_db[vehicle_id] = vehicle_data

    return VehicleResponse(**vehicle_data)


@app.get("/api/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: UUID):
    """Get vehicle by ID"""
    if vehicle_id not in vehicles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )

    return VehicleResponse(**vehicles_db[vehicle_id])


@app.get("/api/vehicles/{vehicle_id}/battery", response_model=BatteryLogResponse)
async def get_vehicle_battery_status(vehicle_id: UUID):
    """Get latest battery status for a vehicle"""
    if vehicle_id not in vehicles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )

    # Find latest battery log for this vehicle
    vehicle_logs = [
        log for log in battery_logs_db.values() if log["vehicle_id"] == vehicle_id
    ]

    if not vehicle_logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No battery data found for this vehicle",
        )

    latest_log = max(vehicle_logs, key=lambda x: x["recorded_at"])

    return BatteryLogResponse(**latest_log)


# ============================================================
# Battery Log Endpoints
# ============================================================


@app.post(
    "/api/vehicles/{vehicle_id}/battery-log",
    response_model=BatteryLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_battery_log(vehicle_id: UUID, log: BatteryLogCreate):
    """Add a new battery log entry"""
    if vehicle_id not in vehicles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )

    log_id = uuid4()

    log_data = {
        "id": log_id,
        "vehicle_id": vehicle_id,
        "soc": log.soc,
        "soh": log.soh,
        "voltage": log.voltage,
        "temperature": log.temperature,
        "health_score": log.health_score,
        "recorded_at": datetime.now(),
        "created_at": datetime.now(),
    }

    battery_logs_db[log_id] = log_data

    return BatteryLogResponse(**log_data)


# ============================================================
# Charging Session Endpoints
# ============================================================


@app.get(
    "/api/vehicles/{vehicle_id}/charging-sessions",
    response_model=List[ChargingSessionResponse],
)
async def get_charging_sessions(vehicle_id: UUID, skip: int = 0, limit: int = 100):
    """Get charging sessions for a vehicle"""
    if vehicle_id not in vehicles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )

    sessions = [
        session
        for session in charging_sessions_db.values()
        if session["vehicle_id"] == vehicle_id
    ]

    sessions = sorted(sessions, key=lambda x: x["start_time"], reverse=True)

    return [
        ChargingSessionResponse(**session) for session in sessions[skip : skip + limit]
    ]


@app.post(
    "/api/charging/schedule",
    response_model=ChargingSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_charging_schedule(session: ChargingSessionCreate):
    """Create a new charging session/schedule"""
    if session.vehicle_id not in vehicles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )

    session_id = uuid4()

    session_data = {
        "id": session_id,
        "vehicle_id": session.vehicle_id,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "energy_consumed": session.energy_consumed,
        "cost": session.cost,
        "created_at": datetime.now(),
    }

    charging_sessions_db[session_id] = session_data

    return ChargingSessionResponse(**session_data)


# ============================================================
# Server Startup
# ============================================================

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    print(
        f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  EV Life Manager API Server                             ║
    ║  Version: 1.0.0                                         ║
    ║  Powered by: Claude Sonnet 4 (LifeOS Engine 2.0)      ║
    ╚══════════════════════════════════════════════════════════╝
    
    🚀 Server starting on: http://{host}:{port}
    📚 API Docs (Swagger): http://{host}:{port}/docs
    📖 API Docs (ReDoc): http://{host}:{port}/redoc
    
    Press CTRL+C to quit
    """
    )

    uvicorn.run("main:app", host=host, port=port, reload=True)
