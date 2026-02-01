"""
EV Life Manager - API Tests
Comprehensive test suite for all API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
from pathlib import Path
import uuid

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from main import app

# Test client
client = TestClient(app)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    random_email = f"test_{uuid.uuid4().hex[:8]}@pytest.com"
    
    response = client.post(
        "/api/users",
        json={
            "email": random_email,
            "password": "TestPassword123!",
            "name": "Pytest User",
            "phone": "010-9999-8888"
        }
    )
    assert response.status_code == 201, f"Failed to create user: {response.json()}"
    return response.json()


@pytest.fixture
def sample_vehicle(sample_user):
    """Create a sample vehicle for testing"""
    random_vin = f"VIN{uuid.uuid4().hex[:14].upper()}"
    
    response = client.post(
        "/api/vehicles",
        json={
            "user_id": sample_user["id"],
            "make": "Tesla",
            "model": "Model 3",
            "year": 2024,
            "vin": random_vin,
            "battery_capacity": 75.0
        }
    )
    assert response.status_code == 201, f"Failed to create vehicle: {response.json()}"
    return response.json()


@pytest.fixture
def sample_battery_log(sample_vehicle):
    """Create a sample battery log for testing"""
    response = client.post(
        f"/api/vehicles/{sample_vehicle['id']}/battery-log",
        json={
            "vehicle_id": sample_vehicle["id"],
            "soc": 85.5,
            "soh": 98.2,
            "voltage": 400.0,
            "temperature": 25.5,
            "health_score": 95.0
        }
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_charging_session(sample_vehicle):
    """Create a sample charging session for testing"""
    response = client.post(
        "/api/charging/schedule",
        json={
            "vehicle_id": sample_vehicle["id"],
            "start_time": "2026-02-01T22:00:00",
            "end_time": "2026-02-02T06:00:00",
            "energy_consumed": 45.5,
            "cost": 12000
        }
    )
    assert response.status_code == 201
    return response.json()


# ============================================================
# Root & Health Check Tests
# ============================================================

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "EV Life Manager API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


# ============================================================
# User Endpoint Tests
# ============================================================

def test_create_user():
    """Test user creation"""
    email = f"newuser_{uuid.uuid4().hex[:8]}@test.com"
    
    response = client.post(
        "/api/users",
        json={
            "email": email,
            "password": "SecurePass123!",
            "name": "New User",
            "phone": "010-1234-5678"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["name"] == "New User"
    assert "id" in data
    assert "created_at" in data


def test_create_user_duplicate_email():
    """Test user creation with duplicate email"""
    email = f"duplicate_{uuid.uuid4().hex[:8]}@test.com"
    
    # Create first user
    response1 = client.post(
        "/api/users",
        json={
            "email": email,
            "password": "Pass123!",
            "name": "User 1",
            "phone": "010-1111-1111"
        }
    )
    assert response1.status_code == 201
    
    # Try to create second user with same email
    response2 = client.post(
        "/api/users",
        json={
            "email": email,
            "password": "Pass456!",
            "name": "User 2",
            "phone": "010-2222-2222"
        }
    )
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]


def test_get_user(sample_user):
    """Test get user by ID"""
    response = client.get(f"/api/users/{sample_user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_user["id"]
    assert data["email"] == sample_user["email"]


def test_get_user_not_found():
    """Test get user with invalid ID"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/users/{fake_id}")
    assert response.status_code == 404


def test_list_users(sample_user):
    """Test list all users"""
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_users_pagination():
    """Test user list pagination"""
    response = client.get("/api/users?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5


# ============================================================
# Vehicle Endpoint Tests
# ============================================================

def test_create_vehicle(sample_user):
    """Test vehicle creation"""
    vin = f"HYU{uuid.uuid4().hex[:14].upper()}"
    
    response = client.post(
        "/api/vehicles",
        json={
            "user_id": sample_user["id"],
            "make": "Hyundai",
            "model": "IONIQ 5",
            "year": 2023,
            "vin": vin,
            "battery_capacity": 77.4
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["make"] == "Hyundai"
    assert data["model"] == "IONIQ 5"
    assert data["year"] == 2023
    assert "id" in data


def test_create_vehicle_duplicate_vin(sample_user):
    """Test vehicle creation with duplicate VIN"""
    vin = f"DUP{uuid.uuid4().hex[:14].upper()}"
    
    # Create first vehicle
    response1 = client.post(
        "/api/vehicles",
        json={
            "user_id": sample_user["id"],
            "make": "Tesla",
            "model": "Model 3",
            "year": 2024,
            "vin": vin,
            "battery_capacity": 75.0
        }
    )
    assert response1.status_code == 201
    
    # Try to create second vehicle with same VIN
    response2 = client.post(
        "/api/vehicles",
        json={
            "user_id": sample_user["id"],
            "make": "Tesla",
            "model": "Model Y",
            "year": 2024,
            "vin": vin,
            "battery_capacity": 75.0
        }
    )
    assert response2.status_code == 400
    assert "VIN already registered" in response2.json()["detail"]


def test_create_vehicle_invalid_year(sample_user):
    """Test vehicle creation with invalid year"""
    response = client.post(
        "/api/vehicles",
        json={
            "user_id": sample_user["id"],
            "make": "Tesla",
            "model": "Model 3",
            "year": 1899,
            "vin": f"INV{uuid.uuid4().hex[:14].upper()}",
            "battery_capacity": 75.0
        }
    )
    assert response.status_code == 422


def test_get_vehicle(sample_vehicle):
    """Test get vehicle by ID"""
    response = client.get(f"/api/vehicles/{sample_vehicle['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_vehicle["id"]
    assert data["make"] == sample_vehicle["make"]


def test_get_vehicle_not_found():
    """Test get vehicle with invalid ID"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/vehicles/{fake_id}")
    assert response.status_code == 404


# ============================================================
# Battery Log Endpoint Tests
# ============================================================

def test_create_battery_log(sample_vehicle):
    """Test battery log creation"""
    response = client.post(
        f"/api/vehicles/{sample_vehicle['id']}/battery-log",
        json={
            "vehicle_id": sample_vehicle["id"],
            "soc": 90.0,
            "soh": 99.5,
            "voltage": 410.0,
            "temperature": 23.0,
            "health_score": 98.0
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["soc"] == 90.0
    assert data["soh"] == 99.5
    assert "id" in data
    assert "recorded_at" in data


def test_create_battery_log_invalid_soc(sample_vehicle):
    """Test battery log with invalid SOC (> 100)"""
    response = client.post(
        f"/api/vehicles/{sample_vehicle['id']}/battery-log",
        json={
            "vehicle_id": sample_vehicle["id"],
            "soc": 150.0,
            "soh": 95.0,
            "voltage": 400.0,
            "temperature": 25.0,
            "health_score": 90.0
        }
    )
    assert response.status_code == 422


def test_get_vehicle_battery_status(sample_battery_log):
    """Test get latest battery status"""
    vehicle_id = sample_battery_log["vehicle_id"]
    response = client.get(f"/api/vehicles/{vehicle_id}/battery")
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_id"] == vehicle_id
    assert "soc" in data
    assert "soh" in data
    assert "health_score" in data


def test_get_battery_status_no_data(sample_vehicle):
    """Test get battery status when no data exists"""
    vin = f"NOB{uuid.uuid4().hex[:14].upper()}"
    
    new_vehicle_response = client.post(
        "/api/vehicles",
        json={
            "user_id": sample_vehicle["user_id"],
            "make": "Kia",
            "model": "EV6",
            "year": 2024,
            "vin": vin,
            "battery_capacity": 77.4
        }
    )
    new_vehicle = new_vehicle_response.json()
    
    response = client.get(f"/api/vehicles/{new_vehicle['id']}/battery")
    assert response.status_code == 404
    assert "No battery data found" in response.json()["detail"]


# ============================================================
# Charging Session Endpoint Tests
# ============================================================

def test_create_charging_session(sample_vehicle):
    """Test charging session creation"""
    response = client.post(
        "/api/charging/schedule",
        json={
            "vehicle_id": sample_vehicle["id"],
            "start_time": "2026-02-02T23:00:00",
            "end_time": "2026-02-03T07:00:00",
            "energy_consumed": 50.0,
            "cost": 15000
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["vehicle_id"] == sample_vehicle["id"]
    assert data["energy_consumed"] == 50.0
    assert data["cost"] == 15000


def test_get_charging_sessions(sample_charging_session):
    """Test get charging sessions for a vehicle"""
    vehicle_id = sample_charging_session["vehicle_id"]
    response = client.get(f"/api/vehicles/{vehicle_id}/charging-sessions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["vehicle_id"] == vehicle_id


def test_get_charging_sessions_pagination(sample_charging_session):
    """Test charging sessions pagination"""
    vehicle_id = sample_charging_session["vehicle_id"]
    response = client.get(
        f"/api/vehicles/{vehicle_id}/charging-sessions?skip=0&limit=10"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10


def test_get_charging_sessions_no_vehicle():
    """Test get charging sessions for non-existent vehicle"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/vehicles/{fake_id}/charging-sessions")
    assert response.status_code == 404


# ============================================================
# Integration Tests
# ============================================================

def test_full_user_journey():
    """Test complete user journey: user → vehicle → battery → charging"""
    
    # Step 1: Create user
    email = f"journey_{uuid.uuid4().hex[:8]}@test.com"
    user_response = client.post(
        "/api/users",
        json={
            "email": email,
            "password": "JourneyPass123!",
            "name": "Journey User",
            "phone": "010-5555-5555"
        }
    )
    assert user_response.status_code == 201
    user = user_response.json()
    
    # Step 2: Register vehicle
    vin = f"JRN{uuid.uuid4().hex[:14].upper()}"
    vehicle_response = client.post(
        "/api/vehicles",
        json={
            "user_id": user["id"],
            "make": "Tesla",
            "model": "Model S",
            "year": 2025,
            "vin": vin,
            "battery_capacity": 100.0
        }
    )
    assert vehicle_response.status_code == 201
    vehicle = vehicle_response.json()
    
    # Step 3: Add battery data
    battery_response = client.post(
        f"/api/vehicles/{vehicle['id']}/battery-log",
        json={
            "vehicle_id": vehicle["id"],
            "soc": 80.0,
            "soh": 100.0,
            "voltage": 420.0,
            "temperature": 22.0,
            "health_score": 100.0
        }
    )
    assert battery_response.status_code == 201
    
    # Step 4: Create charging session
    charging_response = client.post(
        "/api/charging/schedule",
        json={
            "vehicle_id": vehicle["id"],
            "start_time": "2026-02-03T00:00:00",
            "end_time": "2026-02-03T08:00:00",
            "energy_consumed": 60.0,
            "cost": 18000
        }
    )
    assert charging_response.status_code == 201
    
    # Step 5: Verify all data
    battery_status = client.get(f"/api/vehicles/{vehicle['id']}/battery")
    assert battery_status.status_code == 200
    
    charging_sessions = client.get(f"/api/vehicles/{vehicle['id']}/charging-sessions")
    assert charging_sessions.status_code == 200
    assert len(charging_sessions.json()) >= 1


# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
