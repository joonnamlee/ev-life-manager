-- EV Life Manager Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vehicles Table
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    vin VARCHAR(17) UNIQUE NOT NULL CHECK (LENGTH(vin) = 17),
    battery_capacity FLOAT NOT NULL CHECK (battery_capacity > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Battery Logs Table
CREATE TABLE battery_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    soc FLOAT NOT NULL CHECK (soc >= 0 AND soc <= 100),
    soh FLOAT NOT NULL CHECK (soh >= 0 AND soh <= 100),
    voltage FLOAT CHECK (voltage > 0),
    temperature FLOAT,
    health_score FLOAT CHECK (health_score >= 0 AND health_score <= 100),
    recorded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Charging Sessions Table
CREATE TABLE charging_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    energy_consumed FLOAT CHECK (energy_consumed >= 0),
    cost DECIMAL(10,2) CHECK (cost >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_end_time_after_start CHECK (end_time IS NULL OR end_time > start_time)
);

-- Performance Indexes
-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Vehicles table indexes
CREATE INDEX idx_vehicles_user_id ON vehicles(user_id);
CREATE INDEX idx_vehicles_vin ON vehicles(vin);
CREATE INDEX idx_vehicles_make_model ON vehicles(make, model);
CREATE INDEX idx_vehicles_created_at ON vehicles(created_at DESC);

-- Battery logs table indexes
CREATE INDEX idx_battery_logs_vehicle_id ON battery_logs(vehicle_id);
CREATE INDEX idx_battery_logs_recorded_at ON battery_logs(recorded_at DESC);
CREATE INDEX idx_battery_logs_vehicle_recorded ON battery_logs(vehicle_id, recorded_at DESC);
CREATE INDEX idx_battery_logs_health_score ON battery_logs(health_score);
CREATE INDEX idx_battery_logs_soc ON battery_logs(soc);
CREATE INDEX idx_battery_logs_soh ON battery_logs(soh);

-- Charging sessions table indexes
CREATE INDEX idx_charging_sessions_vehicle_id ON charging_sessions(vehicle_id);
CREATE INDEX idx_charging_sessions_start_time ON charging_sessions(start_time DESC);
CREATE INDEX idx_charging_sessions_vehicle_start ON charging_sessions(vehicle_id, start_time DESC);
CREATE INDEX idx_charging_sessions_created_at ON charging_sessions(created_at DESC);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vehicles_updated_at 
    BEFORE UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Additional utility views for common queries
CREATE VIEW vehicle_latest_battery_status AS
SELECT DISTINCT ON (bl.vehicle_id)
    v.id as vehicle_id,
    v.make,
    v.model,
    v.vin,
    bl.soc,
    bl.soh,
    bl.health_score,
    bl.recorded_at as last_updated
FROM vehicles v
JOIN battery_logs bl ON v.id = bl.vehicle_id
ORDER BY bl.vehicle_id, bl.recorded_at DESC;

CREATE VIEW user_vehicle_summary AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    COUNT(v.id) as vehicle_count,
    ARRAY_AGG(v.make || ' ' || v.model) as vehicles
FROM users u
LEFT JOIN vehicles v ON u.id = v.user_id
GROUP BY u.id, u.name, u.email;

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts for EV Life Manager platform';
COMMENT ON TABLE vehicles IS 'Electric vehicles registered by users';
COMMENT ON TABLE battery_logs IS 'Time-series battery health monitoring data';
COMMENT ON TABLE charging_sessions IS 'Charging session records and analytics';

COMMENT ON COLUMN battery_logs.soc IS 'State of Charge (0-100%)';
COMMENT ON COLUMN battery_logs.soh IS 'State of Health (0-100%)';
COMMENT ON COLUMN battery_logs.health_score IS 'AI-calculated battery health score (0-100)';
COMMENT ON COLUMN vehicles.battery_capacity IS 'Battery capacity in kWh';
COMMENT ON COLUMN charging_sessions.energy_consumed IS 'Energy consumed in kWh';