\# 설치 가이드



\## Backend 설치



\### 1. Python 환경 설정



```bash

\# Python 버전 확인 (3.12 이상 권장)

python --version



\# 가상환경 생성

python -m venv venv



\# 가상환경 활성화

\# Windows:

venv\\Scripts\\activate

\# macOS/Linux:

source venv/bin/activate

2\. 의존성 설치

Copycd backend



\# Production 의존성

pip install -r requirements.txt



\# Development 의존성 (개발 시)

pip install -r requirements-dev.txt

3\. 환경 변수 설정

Copy# .env 파일 생성

cp .env.example .env



\# .env 파일 편집

\# DATABASE\_URL, SECRET\_KEY 등을 실제 값으로 변경

4\. 데이터베이스 설정

Copy# PostgreSQL 설치 확인

psql --version



\# 데이터베이스 생성

createdb ev\_life\_manager



\# 스키마 적용

psql -d ev\_life\_manager -f ../database/schema.sql



\# 또는 Alembic 사용

alembic upgrade head

5\. 서버 실행

Copy# 개발 서버 (Hot reload)

python main.py



\# 또는 Uvicorn 직접 실행

uvicorn main:app --reload --host 0.0.0.0 --port 8000

서버 확인:



API: http://localhost:8000

Docs: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Frontend 설치

1\. Node.js 환경 확인

Copy# Node.js 버전 확인 (18 이상 권장)

node --version



\# npm 버전 확인

npm --version

2\. 의존성 설치

Copycd mobile-app



\# npm 사용

npm install



\# 또는 yarn 사용

yarn install

3\. 환경 변수 설정

Copy# .env 파일 생성

cp .env.example .env



\# .env 파일 편집

\# API\_URL 등을 실제 값으로 변경

4\. 앱 실행

Copy# Expo 개발 서버 시작

npm start



\# Android 에뮬레이터

npm run android



\# iOS 시뮬레이터 (macOS only)

npm run ios



\# 웹 브라우저

npm run web

Docker로 실행 (권장)

Docker Compose 사용

Copy# 전체 스택 실행

docker-compose up -d



\# 로그 확인

docker-compose logs -f



\# 중지

docker-compose down

서비스:



Backend: http://localhost:8000

Database: localhost:5432

Redis: localhost:6379

트러블슈팅

Backend

문제: psycopg2 설치 실패



Copy# 해결: binary 버전 사용

pip install psycopg2-binary

문제: Alembic 마이그레이션 오류



Copy# 해결: 마이그레이션 초기화

alembic revision --autogenerate -m "initial"

alembic upgrade head

Frontend

문제: Metro bundler 오류



Copy# 해결: 캐시 클리어

npm start -- --clear

문제: iOS 시뮬레이터 실행 안 됨



Copy# 해결: pods 재설치

cd ios

pod install

cd ..

npm run ios

다음 단계

✅ Backend 서버 실행

✅ Frontend 앱 실행

✅ API 문서 확인 (http://localhost:8000/docs)

✅ 테스트 실행 (pytest / npm test)

✅ 개발 가이드 참고



\*\*저장 (Ctrl+S) 후 닫기 (Alt+F4)\*\*



---



\## \*\*📋 완료 체크리스트\*\*



\- ✅ README.md

\- ✅ LICENSE

\- ✅ .gitignore

\- ✅ backend/.env.example

\- ✅ mobile-app/.env.example

\- ✅ backend/config.py

\- ✅ backend/requirements.txt (완료!)

\- ✅ backend/requirements-dev.txt (보너스!)

\- ✅ mobile-app/package.json (완료!)

\- ✅ INSTALLATION.md (보너스!)



---



\## \*\*🎉 문서화 100% 완료!\*\*



\*\*생성된 파일 목록:\*\*

ev\_lifemanager\_mvp/ ├── README.md ✅ ├── LICENSE ✅ ├── .gitignore ✅ ├── INSTALLATION.md ✅ ├── backend/ │ ├── .env.example ✅ │ ├── config.py ✅ │ ├── requirements.txt ✅ │ └── requirements-dev.txt ✅ └── mobile-app/ ├── .env.example ✅ └── package.json ✅







