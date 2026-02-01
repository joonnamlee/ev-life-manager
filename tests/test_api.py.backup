```python
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

# Fixtures
@pytest.fixture
def sample_user():
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+82-10-1234-5678",
        "location": "Seoul, South Korea"
    }

@pytest.fixture
def sample_vehicle():
    return {
        "user_id": 1,
        "make": "Tesla",
        "model": "Model 3",
        "year": 2023,
        "battery_capacity": 75.0,
        "vin": "5YJ3E1EA3KF123456"
    }

@pytest.fixture
def sample_charging_station():
    return {
        "name": "Seoul Station Charger",
        "location": "Seoul Station",
        "latitude": 37.5547,
        "longitude": 126.9707,
        "power_rating": 150.0,
        "connector_type": "CCS2",
        "status": "available"
    }

@pytest.fixture
def sample_maintenance_request():
    return {
        "vehicle_id": 1,
        "service_type": "battery_check",
        "description": "Battery health inspection needed",
        "preferred_date": "2024-02-15"
    }

# Health Check Tests
def test_root_endpoint():
    # Given: API가 실행 중
    # When: 루트 엔드포인트 호출
    response = client.get("/")
    
    # Then: 정상 응답
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "EV Life Manager API"
    assert "version" in data

def test_health_check():
    # Given: API가 실행 중
    # When: /health 엔드포인트 호출
    response = client.get("/health")
    
    # Then: 200 OK 응답
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "database" in data
    assert data["database"] == "connected"

# User CRUD Tests
def test_create_user_success(sample_user):
    # Given: 유효한 사용자 데이터
    # When: POST /api/users 호출
    response = client.post("/api/users", json=sample_user)
    
    # Then: 사용자 생성 성공 (201 Created)
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert data["message"] == "User created successfully"
    assert data["user"]["name"] == sample_user["name"]
    assert data["user"]["email"] == sample_user["email"]

def test_create_user_invalid_email():
    # Given: 잘못된 이메일 형식
    invalid_user = {
        "name": "John",
        "email": "invalid-email",
        "phone": "+82-10-1234-5678"
    }
    
    # When: POST /api/users 호출
    response = client.post("/api/users", json=invalid_user)
    
    # Then: 422 Validation Error
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("email" in str(error).lower() for error in data["detail"])

def test_create_user_duplicate_email(sample_user):
    # Given: 이미 존재하는 이메일로 사용자 생성
    client.post("/api/users", json=sample_user)
    
    # When: 같은 이메일로 다시 사용자 생성 시도
    response = client.post("/api/users", json=sample_user)
    
    # Then: 409 Conflict
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_get_user_success():
    # Given: 기존 사용자 ID
    user_id = 1
    
    # When: GET /api/users/{user_id} 호출
    response = client.get(f"/api/users/{user_id}")
    
    # Then: 사용자 정보 반환 (200 OK)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert "name" in data
    assert "email" in data
    assert "created_at" in data

def test_get_user_not_found():
    # Given: 존재하지 않는 사용자 ID
    user_id = 99999
    
    # When: GET /api/users/{user_id} 호출
    response = client.get(f"/api/users/{user_id}")
    
    # Then: 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Vehicle Tests
def test_create_vehicle_success(sample_vehicle):
    # Given: 유효한 차량 데이터
    # When: POST /api/vehicles 호출
    response = client.post("/api/vehicles", json=sample_vehicle)
    
    # Then: 차량 등록 성공 (201 Created)
    assert response.status_code == 201
    data = response.json()
    assert "vehicle_id" in data
    assert data["message"] == "Vehicle registered successfully"
    assert data["vehicle"]["make"] == sample_vehicle["make"]
    assert data["vehicle"]["model"] == sample_vehicle["model"]

def test_create_vehicle_invalid_user():
    # Given: 존재하지 않는 사용자 ID
    invalid_vehicle = {
        "user_id": 99999,
        "make": "Tesla",
        "model": "Model 3",
        "year": 2023,
        "battery_capacity": 75.0,
        "vin": "5YJ3E1EA3KF123456"
    }
    
    # When: POST /api/vehicles 호출
    response = client.post("/api/vehicles", json=invalid_vehicle)
    
    # Then: 404 Not Found
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_get_battery_status():
    # Given: 기존 차량 ID
    vehicle_id = 1
    
    # When: GET /api/vehicles/{vehicle_id}/battery 호출
    response = client.get(f"/api/vehicles/{vehicle_id}/battery")
    
    # Then: 배터리 상태 반환 (200 OK)
    assert response.status_code == 200
    data = response.json()
    
    # 필수 필드 검증
    required_fields = ["soc", "soh", "temperature", "voltage", "current", "health_score", "estimated_range"]
    for field in required_fields:
        assert field in data
    
    # 값 범위 검증
    assert 0 <= data["soc"] <= 100
    assert 0 <= data["soh"] <= 100
    assert -40 <= data["temperature"] <= 60
    assert 0 <= data["health_score"] <= 100

def test_get_battery_status_not_found():
    # Given: 존재하지 않는 차량 ID
    vehicle_id = 99999
    
    # When: GET /api/vehicles/{vehicle_id}/battery 호출
    response = client.get(f"/api/vehicles/{vehicle_id}/battery")
    
    # Then: 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"

# Charging Station Tests
def test_get_nearby_charging_stations():
    # Given: 사용자 위치 좌표
    latitude = 37.5665
    longitude = 126.9780
    radius = 5.0
    
    # When: GET /api/charging-stations/nearby 호출
    response = client.get(
        f"/api/charging-stations/nearby?lat={latitude}&lon={longitude}&radius={radius}"
    )
    
    # Then: 주변 충전소 목록 반환 (200 OK)
    assert response.status_code == 200
    data = response.json()
    assert "stations" in data
    assert isinstance(data["stations"], list)
    
    # 각 충전소 데이터 검증
    if data["stations"]:
        station = data["stations"][0]
        required_fields = ["station_id", "name", "location", "latitude", "longitude", "power_rating", "status"]
        for field in required_fields:
            assert field in station

def test_create_charging_schedule():
    # Given: 충전 스케줄 데이터
    schedule_data = {
        "vehicle_id": 1,
        "station_id": 1,
        "start_time": "2024-02-15T09:00:00",
        "target_soc": 80,
        "charging_type": "fast"
    }
    
    # When: POST /api/charging/schedule 호출
    response = client.post("/api/charging/schedule", json=schedule_data)
    
    # Then: 충전 스케줄 생성 성공 (201 Created)
    assert response.status_code == 201
    data = response.json()
    assert "schedule_id" in data
    assert data["message"] == "Charging schedule created successfully"

# AI-based Battery Analysis Tests
@patch('main.ai_service.analyze_battery_health')
def test_get_battery_ai_analysis(mock_ai_analysis):
    # Given: AI 분석 결과 모킹
    mock_ai_analysis.return_value = {
        "health_score": 85.5,
        "degradation_rate": 2.1,
        "predicted_lifespan": 8.5,
        "recommendations": [
            "Avoid charging to 100% daily",
            "Use slow charging when possible"
        ],
        "risk_factors": ["high_temperature_exposure"]
    }
    vehicle_id = 1
    
    # When: GET /api/vehicles/{vehicle_id}/ai-analysis 호출
    response = client.get(f"/api/vehicles/{vehicle_id}/ai-analysis")
    
    # Then: AI 분석 결과 반환 (200 OK)
    assert response.status_code == 200
    data = response.json()
    assert data["health_score"] == 85.5
    assert data["degradation_rate"] == 2.1
    assert len(data["recommendations"]) == 2
    assert "high_temperature_exposure" in data["risk_factors"]

# Maintenance Service Tests
def test_create_maintenance_request(sample_maintenance_request):
    # Given: 정비 요청 데이터
    # When: POST /api/maintenance/request 호출
    response = client.post("/api/maintenance/request", json=sample_maintenance_request)
    
    # Then: 정비 요청 생성 성공 (201 Created)
    assert response.status_code == 201
    data = response.json()
    assert "request_id" in data
    assert data["status"] == "pending"
    assert data["service_type"] == sample_maintenance_request["service_type"]

def test_get_nearby_service_centers():
    # Given: 사용자 위치
    latitude = 37.5665
    longitude = 126.9780
    
    # When: GET /api/service-centers/nearby 호출
    response = client.get(f"/api/service-centers/nearby?lat={latitude}&lon={longitude}")
    
    # Then: 주변 서비스센터 목록 반환 (200 OK)
    assert response.status_code == 200
    data = response.json()
    assert "service_centers" in data
    assert isinstance(data["service_centers"], list)

# Integration Tests
def test_full_user_vehicle_flow(sample_user, sample_vehicle):
    # Given: 새 사용자 생성
    user_response = client.post("/api/users", json=sample_user)
    assert user_response.status_code == 201
    user_id = user_response.json()["user_id"]
    
    # When: 해당 사용자의 차량 등록
    sample_vehicle["user_id"] = user_id
    vehicle_response = client.post("/api/vehicles", json=sample_vehicle)
    assert vehicle_response.status_code == 201
    vehicle_id = vehicle_response.json()["vehicle_id"]
    
    # Then: 차량 배터리 상태 조회 가능
    battery_response = client.get(f"/api/vehicles/{vehicle_id}/battery")
    assert battery_response.status_code == 200
    
    # And: 사용자 정보에 차량이 연결됨
    user_vehicles_response = client.get(f"/api/users/{user_id}/vehicles")
    assert user_vehicles_response.status_code == 200
    vehicles = user_vehicles_response.json()["vehicles"]
    assert len(vehicles) == 1
    assert vehicles[0]["vehicle_id"] == vehicle_id

def test_complete_charging_workflow(sample_user, sample_vehicle):
    # Given: 사용자와 차량 생성
    user_response = client.post("/api/users", json=sample_user)
    user_id = user_response.json()["user_id"]
    
    sample_vehicle["user_id"] = user_id
    vehicle_response = client.post("/api/vehicles", json=sample_vehicle)
    vehicle_id = vehicle_response.json()["vehicle_id"]
    
    # When: 주변 충전소 검색
    stations_response = client.get("/api/charging-stations/nearby?lat=37.5665&lon=126.9780&radius=5")
    assert stations_response.status_code == 200
    stations = stations_response.json()["stations"]
    
    # And: 충전 스케줄 생성
    if stations:
        schedule_data = {
            "vehicle_id": vehicle_id,
            "station_id": stations[0]["station_id"],
            "start_time": "2024-02-15T09:00:00",
            "target_soc": 80,
            "charging_type": "fast"
        }
        schedule_response = client.post("/api/charging/schedule", json=schedule_data)
        assert schedule_response.status_code == 201
        
        # Then: 스케줄 조회 가능
        schedule_id = schedule_response.json()["schedule_id"]
        get_schedule_response = client.get(f"/api/charging/schedule/{schedule_id}")
        assert get_schedule_response.status_code == 200

# Error Handling Tests
def test_invalid_json_request():
    # Given: 잘못된 JSON 데이터
    # When: POST 요청 시 잘못된 데이터 전송
    response = client.post(
        "/api/users",
        data="invalid json",
        headers={"content-type": "application/json"}
    )
    
    # Then: 422 Unprocessable Entity
    assert response.status_code == 422

def test_missing_required_fields():
    # Given: 필수 필드가 누락된 사용자 데이터
    incomplete_user = {"name": "John"}
    
    # When: POST /api/users 호출
    response = client.post("/api/users", json=incomplete