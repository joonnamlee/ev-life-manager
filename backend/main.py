```python
from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uvicorn

# FastAPI 앱 초기화
app = FastAPI(
    title="EV Life Manager API",
    description="전기차 배터리 헬스케어 플랫폼 - AI 기반 배터리 모니터링, 스마트 충전 스케줄러, 정비소 네트워크 연결",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Enum 정의
class VehicleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class ChargingStatus(str, Enum):
    CHARGING = "charging"
    IDLE = "idle"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"

class BatteryHealthLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

# Pydantic 모델 정의
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, regex=r"^\+?[1-9]\d{1,14}$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    make: str = Field(..., min_length=1, max_length=30)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=2010, le=2030)
    battery_capacity: float = Field(..., gt=0, le=200)  # kWh
    vin: str = Field(..., min_length=17, max_length=17)

class VehicleCreate(VehicleBase):
    user_id: int

class Vehicle(VehicleBase):
    id: int
    user_id: int
    status: VehicleStatus = VehicleStatus.ACTIVE
    odometer: float = 0.0  # km
    registered_at: datetime
    
    class Config:
        from_attributes = True

class BatteryLogBase(BaseModel):
    soc: float = Field(..., ge=0, le=100)  # State of Charge (%)
    soh: float = Field(..., ge=0, le=100)  # State of Health (%)
    temperature: float = Field(..., ge=-40, le=80)  # Celsius
    voltage: float = Field(..., gt=0)
    current: float = Field(...)
    charging_cycles: int = Field(..., ge=0)

class BatteryLogCreate(BatteryLogBase):
    vehicle_id: int

class BatteryLog(BatteryLogBase):
    id: int
    vehicle_id: int
    timestamp: datetime
    health_score: float = Field(..., ge=0, le=100)
    health_level: BatteryHealthLevel
    
    class Config:
        from_attributes = True

class ChargingSessionBase(BaseModel):
    start_time: datetime
    end_time: Optional[datetime] = None
    start_soc: float = Field(..., ge=0, le=100)
    end_soc: Optional[float] = Field(None, ge=0, le=100)
    charging_power: float = Field(..., gt=0)  # kW
    location: str

class ChargingSessionCreate(ChargingSessionBase):
    vehicle_id: int

class ChargingSession(ChargingSessionBase):
    id: int
    vehicle_id: int
    status: ChargingStatus = ChargingStatus.SCHEDULED
    energy_consumed: Optional[float] = None  # kWh
    cost: Optional[float] = None
    
    class Config:
        from_attributes = True

class MaintenanceShop(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    rating: float = Field(..., ge=0, le=5)
    specialties: List[str]
    
    class Config:
        from_attributes = True

# 임시 데이터베이스 (실제로는 SQLAlchemy나 다른 ORM 사용)
fake_users_db: Dict[int, User] = {}
fake_vehicles_db: Dict[int, Vehicle] = {}
fake_battery_logs_db: Dict[int, BatteryLog] = {}
fake_charging_sessions_db: Dict[int, ChargingSession] = {}

# 헬퍼 함수
def calculate_health_score(soc: float, soh: float, temperature: float, cycles: int) -> tuple[float, BatteryHealthLevel]:
    """배터리 건강 점수 및 레벨 계산"""
    # AI 기반 건강 점수 계산 로직 (단순화된 버전)
    temp_factor = 1.0 if -10 <= temperature <= 35 else 0.8
    cycle_factor = max(0.5, 1.0 - (cycles / 2000) * 0.3)
    
    health_score = soh * temp_factor * cycle_factor
    
    if health_score >= 90:
        level = BatteryHealthLevel.EXCELLENT
    elif health_score >= 75:
        level = BatteryHealthLevel.GOOD
    elif health_score >= 60:
        level = BatteryHealthLevel.FAIR
    else:
        level = BatteryHealthLevel.POOR
    
    return round(health_score, 2), level

# API 엔드포인트
@app.get("/", tags=["Root"])
async def root():
    """루트 엔드포인트 - API 정보 반환"""
    return {
        "message": "EV Life Manager API",
        "version": "1.0.0",
        "description": "전기차 배터리 헬스케어 플랫폼",
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "EV Life Manager API",
        "version": "1.0.0"
    }

# 사용자 관련 엔드포인트
@app.post("/api/users", response_model=Dict[str, Any], status_code=201, tags=["Users"])
async def create_user(user: UserCreate):
    """새 사용자 등록"""
    # 이메일 중복 체크
    for existing_user in fake_users_db.values():
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    
    user_id = len(fake_users_db) + 1
    new_user = User(
        id=user_id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        created_at=datetime.now(),
        is_active=True
    )
    
    fake_users_db[user_id] = new_user
    
    return {
        "user_id": user_id,
        "message": "사용자가 성공적으로 등록되었습니다.",
        "user": new_user
    }

@app.get("/api/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: int = Path(..., description="사용자 ID", gt=0)):
    """특정 사용자 정보 조회"""
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return fake_users_db[user_id]

@app.get("/api/users", response_model=List[User], tags=["Users"])
async def get_users(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """사용자 목록 조회 (페이지네이션)"""
    users = list(fake_users_db.values())
    return users[skip:skip + limit]

# 차량 관련 엔드포인트
@app.post("/api/vehicles", response_model=Dict[str, Any], status_code=201, tags=["Vehicles"])
async def create_vehicle(vehicle: VehicleCreate):
    """새 차량 등록"""
    # 사용자 존재 확인
    if vehicle.user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    # VIN 중복 체크
    for existing_vehicle in fake_vehicles_db.values():
        if existing_vehicle.vin == vehicle.vin:
            raise HTTPException(status_code=400, detail="이미 등록된 차량입니다.")
    
    vehicle_id = len(fake_vehicles_db) + 1
    new_vehicle = Vehicle(
        id=vehicle_id,
        user_id=vehicle.user_id,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        battery_capacity=vehicle.battery_capacity,
        vin=vehicle.vin,
        status=VehicleStatus.ACTIVE,
        odometer=0.0,
        registered_at=datetime.now()
    )
    
    fake_vehicles_db[vehicle_id] = new_vehicle
    
    return {
        "vehicle_id": vehicle_id,
        "message": "차량이 성공적으로 등록되었습니다.",
        "vehicle": new_vehicle
    }

@app.get("/api/vehicles/{vehicle_id}", response_model=Vehicle, tags=["Vehicles"])
async def get_vehicle(vehicle_id: int = Path(..., description="차량 ID", gt=0)):
    """특정 차량 정보 조회"""
    if vehicle_id not in fake_vehicles_db:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다.")
    
    return fake_vehicles_db[vehicle_id]

@app.get("/api/vehicles/{vehicle_id}/battery", response_model=Dict[str, Any], tags=["Battery"])
async def get_battery_status(vehicle_id: int = Path(..., description="차량 ID", gt=0)):
    """차량 배터리 상태 조회"""
    if vehicle_id not in fake_vehicles_db:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다.")
    
    # 최신 배터리 로그 조회 (실제로는 데이터베이스에서 조회)
    latest_log = None
    for log in fake_battery_logs_db.values():
        if log.vehicle_id == vehicle_id:
            if latest_log is None or log.timestamp > latest_log.timestamp:
                latest_log = log
    
    if latest_log:
        return {
            "vehicle_id": vehicle_id,
            "soc": latest_log.soc,
            "soh": latest_log.soh,
            "temperature": latest_log.temperature,
            "voltage": latest_log.voltage,
            "current": latest_log.current,
            "health_score": latest_log.health_score,
            "health_level": latest_log.health_level,
            "charging_cycles": latest_log.charging_cycles,
            "last_updated": latest_log.timestamp,
            "recommendations": [
                "정기적인 배터리 점검을 받으세요." if latest_log.health_score < 80 else "배터리 상태가 양호합니다.",
                "극한 온도에서의 충전을 피하세요." if abs(latest_log.temperature) > 35 else None
            ]
        }
    else:
        # 기본 배터리 상태 (데모용)
        return {
            "vehicle_id": vehicle_id,
            "soc": 85.5,
            "soh": 92.3,
            "temperature": 28.5,
            "voltage": 400.2,
            "current": 0.0,
            "health_score": 88.7,
            "health_level": "good",
            "charging_cycles": 245,
            "last_updated": datetime.now(),
            "recommendations": [
                "배터리 상태가 양호합니다.",
                "최적 충전 온도를 유지하고 있습니다."
            ]
        }

@app.post("/api/vehicles/{vehicle_id}/battery-log", response_model=Dict[str, Any], status_code=201, tags=["Battery"])
async def create_battery_log(
    vehicle_id: int,
    battery_data: BatteryLogBase
):
    """배터리 로그 데이터 추가"""
    if vehicle_id not in fake_vehicles_db:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다.")
    
    health_score, health_level = calculate_health_score(
        battery_data.soc,
        battery_data.soh,
        battery_data.temperature,
        battery_data.charging_cycles
    )
    
    log_id = len(fake_battery_logs_db) + 1
    new_log = BatteryLog(
        id=log_id,
        vehicle_id=vehicle_id,
        soc=battery_data.soc,
        soh=battery_data.soh,
        temperature=battery_data.temperature,
        voltage=battery_data.voltage,
        current=battery_data.current,
        charging_cycles=battery_data.charging_cycles,
        timestamp=datetime.now(),
        health_score=health_score,
        health_level=health_level
    )
    
    fake_battery_logs_db[log_id] = new_log
    
    return {
        "log_id": log_id,
        "message": "배터리 로그가 성공적으로 기록되었습니다.",
        "battery_log": new_log
    }

# 충전 관련 엔드포인트
@app.get("/api/vehicles/{vehicle_id}/charging-sessions", response_model=List[ChargingSession], tags=["Charging"])
async def get_charging_sessions(
    vehicle_id: int,
    limit: int = Query(10, ge=1, le=100)
):
    """차량의 충전 세션 내역 조회"""
    if vehicle_id not in fake_