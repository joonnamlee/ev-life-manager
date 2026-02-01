```python
# LifeOS Engine 2.0 - System Architecture
# Project: EV 라이프 매니저 (Electric Vehicle Life Manager)

# 1. 시스템 개요
# 핵심 기능:
# - AI 기반 배터리 헬스케어: 실시간 배터리 상태 모니터링, 수명 예측, 성능 최적화 알고리즘 제공
# - 스마트 충전 스케줄러: 전력 요금, 배터리 온도, 사용 패턴 분석을 통한 최적 충전 시간 및 방식 제안
# - 통합 정비소 네트워크: AI 진단 기반 정비 필요성 예측, 주변 정비소 연결, 예약 및 이력 관리

# 주요 컴포넌트:
# - Mobile Application (React Native): 사용자 인터페이스 및 실시간 데이터 표시
# - AI Analytics Engine (LifeOS Engine 2.0): 배터리 데이터 분석, 예측 모델링, 최적화 알고리즘
# - Backend API Server (FastAPI): 비즈니스 로직, 데이터 처리, 외부 서비스 통합
# - Data Management Layer (PostgreSQL): 차량 데이터, 사용자 정보, 분석 결과 저장
# - Cloud Infrastructure (AWS): 확장 가능한 서버리스 아키텍처 및 데이터 파이프라인

# 2. 아키텍처 다이어그램 (ASCII)
"""
┌─────────────────────────────────────────────────────────────────────┐
│                          EV Life Manager                            │
│                         System Architecture                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Mobile Apps    │    │   Web Dashboard  │    │  Service Portal  │
│  (React Native)  │    │     (React)      │    │   (정비소용)      │
└─────────┬────────┘    └─────────┬────────┘    └─────────┬────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
          ┌───────────────────────▼───────────────────────┐
          │              API Gateway                      │
          │            (AWS API Gateway)                  │
          └───────────────────────┬───────────────────────┘
                                  │
          ┌───────────────────────▼───────────────────────┐
          │           FastAPI Backend Server              │
          │  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │
          │  │   Auth      │  │  Business   │  │  API   │ │
          │  │  Service    │  │   Logic     │  │ Routes │ │
          │  └─────────────┘  └─────────────┘  └────────┘ │
          └─────────────┬─────────────────┬─────────────────┘
                        │                 │
        ┌───────────────▼──────┐    ┌─────▼──────────────────┐
        │   LifeOS Engine 2.0  │    │    External APIs       │
        │  ┌─────────────────┐ │    │ ┌────────────────────┐ │
        │  │ ML Prediction   │ │    │ │  Charging Station  │ │
        │  │    Models       │ │    │ │     Networks       │ │
        │  └─────────────────┘ │    │ └────────────────────┘ │
        │  ┌─────────────────┐ │    │ ┌────────────────────┐ │
        │  │  Battery AI     │ │    │ │   Weather API      │ │
        │  │   Analytics     │ │    │ │   (충전 최적화)     │ │
        │  └─────────────────┘ │    │ └────────────────────┘ │
        │  ┌─────────────────┐ │    │ ┌────────────────────┐ │
        │  │ Optimization    │ │    │ │  Maintenance       │ │
        │  │   Algorithms    │ │    │ │    Services        │ │
        │  └─────────────────┘ │    │ └────────────────────┘ │
        └──────────────────────┘    └────────────────────────┘
                        │
        ┌───────────────▼──────────────────────────────────┐
        │              PostgreSQL Database                 │
        │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
        │  │  Users  │ │Vehicles │ │Battery  │ │Service  │ │
        │  │  Data   │ │  Data   │ │  Logs   │ │Records  │ │
        │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
        └──────────────────────────────────────────────────┘
                        │
        ┌───────────────▼──────────────────────────────────┐
        │                AWS Cloud Services                │
        │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ │
        │ │    S3    │ │ Lambda   │ │CloudWatch│ │  SQS  │ │
        │ │ (Storage)│ │(Serverless)│(Monitoring)│(Queue)│ │
        │ └──────────┘ └──────────┘ └──────────┘ └───────┘ │
        └──────────────────────────────────────────────────┘
"""

# 3. 기술 스택 상세

# Frontend - React Native:
# - 선택 이유: 크로스 플랫폼 개발로 개발 비용 절약, 네이티브 성능 제공
# - 활용: 실시간 배터리 모니터링 UI, 푸시 알림, 차량 연결 기능
# - 주요 라이브러리: React Navigation, Redux Toolkit, React Native Paper

# Backend - FastAPI:
# - 선택 이유: 고성능 비동기 처리, 자동 API 문서화, Python ML 생태계와 호환
# - 활용: RESTful API 제공, 실시간 데이터 처리, AI 모델 서빙
# - 주요 기능: JWT 인증, WebSocket 실시간 통신, Celery 백그라운드 작업

# Database - PostgreSQL:
# - 선택 이유: ACID 트랜잭션, 시계열 데이터 처리 최적화, JSON 지원
# - 활용: 배터리 로그 저장, 사용자 데이터 관리, 복잡한 분석 쿼리
# - 확장: TimescaleDB 확장으로 시계열 데이터 최적화

# AI - LifeOS Engine 2.0:
# - 선택 이유: 전용 배터리 분석 알고리즘, 실시간 예측 모델링
# - 활용: 배터리 수명 예측, 충전 패턴 최적화, 이상 징후 감지
# - 기술: TensorFlow, scikit-learn, 시계열 분석 모델

# Cloud - AWS:
# - 선택 이유: 확장성, 보안, 다양한 AI/ML 서비스 제공
# - 활용: ECS 컨테이너 배포, RDS 데이터베이스, S3 파일 저장
# - 서비스: API Gateway, Lambda, CloudWatch, SQS

# 4. 디렉토리 구조

"""
ev-life-manager/
├── mobile-app/                    # React Native 모바일 앱
│   ├── src/
│   │   ├── components/            # 재사용 가능한 UI 컴포넌트
│   │   │   ├── BatteryStatus.tsx
│   │   │   ├── ChargingScheduler.tsx
│   │   │   └── ServiceMap.tsx
│   │   ├── screens/               # 화면 컴포넌트
│   │   │   ├── Dashboard.tsx
│   │   │   ├── BatteryHealth.tsx
│   │   │   ├── ChargingPlan.tsx
│   │   │   └── ServiceCenter.tsx
│   │   ├── services/              # API 통신 및 비즈니스 로직
│   │   │   ├── api.ts
│   │   │   ├── battery.ts
│   │   │   └── charging.ts
│   │   ├── store/                 # Redux 상태 관리
│   │   │   ├── slices/
│   │   │   └── store.ts
│   │   └── utils/                 # 유틸리티 함수
│   ├── package.json
│   └── metro.config.js
│
├── backend/                       # FastAPI 백엔드 서버
│   ├── app/
│   │   ├── api/                   # API 라우터
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── battery.py
│   │   │   │   ├── charging.py
│   │   │   │   ├── vehicles.py
│   │   │   │   └── services.py
│   │   │   └── deps.py           # 의존성 주입
│   │   ├── core/                  # 핵심 설정
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/                # SQLAlchemy 모델
│   │   │   ├── user.py
│   │   │   ├── vehicle.py
│   │   │   ├── battery.py
│   │   │   └── service.py
│   │   ├── schemas/               # Pydantic 스키마
│   │   │   ├── user.py
│   │   │   ├── vehicle.py
│   │   │   └── battery.py
│   │   ├── services/              # 비즈니스 로직
│   │   │   ├── battery_analyzer.py
│   │   │   ├── charging_optimizer.py
│   │   │   └── ai_predictor.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── ai-engine/                     # LifeOS Engine 2.0
│   ├── models/                    # AI 모델
│   │   ├── battery_health/
│   │   │   ├── lstm_predictor.py
│   │   │   └── health_classifier.py
│   │   ├── charging_optimizer/
│   │   │   ├── schedule_optimizer.py
│   │   │   └── cost_minimizer.py
│   │   └── anomaly_detector/
│   │       ├── isolation_forest.py
│   │       └── statistical_detector.py
│   ├── data/                      # 데이터 처리
│   │   ├── preprocessor.py
│   │   ├── feature_engineer.py
│   │   └── data_validator.py
│   ├── training/                  # 모델 학습
│   │   ├── train_battery_model.py
│   │   ├── train_charging_model.py
│   │   └── model_evaluator.py
│   └── inference/                 # 추론 서비스
│       ├── prediction_service.py
│       └── batch_processor.py
│
├── infrastructure/                # 인프라 코드
│   ├── terraform/                 # AWS 리소스 정의
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── modules/
│   │       ├── vpc/
│   │       ├── ecs/
│   │       ├── rds/
│   │       └── s3/
│   ├── docker/                    # Docker 설정
│   │   ├── backend.Dockerfile
│   │   ├── ai-engine.Dockerfile
│   │   └── docker-compose.yml
│   └── kubernetes/                # K8s 배포 설정
│       ├── backend-deployment.yaml
│       ├── ai-engine-deployment.yaml
│       └── ingress.yaml
│
├── database/                      # 데이터베이스 관련
│   ├── migrations/                # Alembic 마이그레이션
│   │   ├── versions/
│   │   └── alembic.ini
│   ├── seeds/                     # 초기 데이터
│   │   ├── users.sql
│   │   └── vehicle_models.sql
│   └── schemas/                   # DB 스키마 정의
│       └── init.sql
│
├── docs/                          # 문서
│   ├── api/                       # API 문서
│   ├── architecture/              # 아키텍처 문서
│   └── deployment/                # 배포 가이드
│
├── tests/                         # 테스트 코드
│   ├── backend/
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_models/
│   ├── ai-engine/
│   │   ├── test_models/
│   │   └── test_inference/
│   └── integration/
│       └── test_e2e.py
│
├── scripts/                       # 유틸리티 스크립트
│   ├── deploy.sh
│   ├── backup.sh
│   └── data_migration.py
│
├── .github/                       # GitHub Actions
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       └── tests.yml
│
├── docker-compose.yml             # 로컬 개발 환경
├── README.md                      # 프로젝트 설명
└── .gitignore                     # Git 제외 파일
"""

# 5. 데이터 모델 (주요 3개)

# User 모델 - 사용자 정보 및 인증
class User:
    """
    사용자 기본 정보 및 인증 데이터