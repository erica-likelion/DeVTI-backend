# DeVTI - Backend

> 멋쟁이사자처럼 한양대학교 ERICA 장기 프로젝트

## 프로젝트 설명

IT 동아리를 위한 AI 기반 팀 매칭 웹 서비스 - DeVTI

## 주요 기술 스택

- **Backend**: Django
- **Database**: MySQL
- **Infrastructure**: Docker

## 시작하기

### 1. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, `.env.example` 파일을 참고하여 환경 변수를 설정합니다.

```bash
cp .env.example .env
```

그런 다음 `.env` 파일에 실제 값을 입력합니다.

### 2. Docker로 실행하기

Docker와 Docker Compose가 설치되어 있어야 합니다.

```bash
# Docker Compose를 사용하여 빌드하고 백그라운드에서 실행합니다.
docker compose up --build -d

# 데이터베이스 마이그레이션 (최초 실행 시 또는 모델 변경 시)
docker compose exec web python manage.py migrate
```

### 3. 서버 접속

웹 브라우저에서 `http://localhost:8000`으로 접속합니다.
