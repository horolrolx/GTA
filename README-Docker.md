# Good Travel Agent - Docker 환경 구축 가이드

## 🐳 Docker 환경 개요

Good Travel Agent는 Docker와 Docker Compose를 사용하여 쉽게 배포하고 실행할 수 있습니다.

### 아키텍처
- **Backend**: Flask API 서버 (포트 5555)
- **Frontend**: Streamlit 웹 애플리케이션 (포트 8501)
- **네트워크**: Docker bridge 네트워크로 서비스 간 통신

## 📋 사전 요구사항

### 1. Docker 설치
```bash
# macOS (Homebrew)
brew install docker docker-compose

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Windows
# Docker Desktop 설치: https://docs.docker.com/desktop/windows/
```

### 2. API 키 준비
다음 API 키들이 필요합니다:
- **OpenAI API Key** (필수)
- **Serper API Key** (필수) 
- **OpenWeatherMap API Key** (필수)
- **Naver Search API** (선택사항)
- **LangSmith API Key** (선택사항)

## 🚀 빠른 시작

### 1. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 API 키 입력
vi .env
```

### 2. Docker 실행
```bash
# 자동 실행 스크립트 사용 (권장)
./docker-run.sh

# 또는 수동 실행
docker-compose up --build -d
```

### 3. 서비스 접속
- **웹 애플리케이션**: http://localhost:8501
- **API 서버**: http://localhost:5555
- **헬스체크**: http://localhost:5555/health

## 📁 Docker 파일 구조

```
├── Dockerfile              # 백엔드 컨테이너 이미지
├── Dockerfile.frontend     # 프론트엔드 컨테이너 이미지  
├── docker-compose.yml      # 서비스 오케스트레이션
├── .dockerignore           # Docker 빌드 제외 파일
├── .env.example            # 환경변수 템플릿
└── docker-run.sh           # 자동 실행 스크립트
```

## 🔧 Docker 명령어

### 기본 명령어
```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 개발 명령어
```bash
# 이미지 강제 재빌드
docker-compose build --no-cache

# 컨테이너 접속
docker exec -it gta-backend bash
docker exec -it gta-frontend bash

# 볼륨 정리
docker-compose down --volumes

# 시스템 정리
docker system prune -f
```

## 🏥 헬스체크 및 모니터링

### 서비스 상태 확인
```bash
# 컨테이너 상태
docker-compose ps

# 리소스 사용량
docker stats

# 백엔드 헬스체크
curl http://localhost:5555/health

# 프론트엔드 접속 확인
curl http://localhost:8501
```

### 로그 모니터링
```bash
# 실시간 로그 모니터링
docker-compose logs -f

# 특정 시간 이후 로그
docker-compose logs --since="2024-01-01T00:00:00"

# 로그 파일 확인 (컨테이너 내)
docker exec gta-backend cat /app/crew_llm_responses.log
```

## 🔧 환경변수 설정

### 필수 환경변수
```bash
OPENAI_API_KEY=sk-...                 # OpenAI API 키
SERPER_API_KEY=...                    # Serper 검색 API 키
OPENWEATHERMAP_API_KEY=...            # 날씨 API 키
```

### 선택적 환경변수
```bash
NAVER_CLIENT_ID=...                   # 네이버 검색 클라이언트 ID
NAVER_CLIENT_SECRET=...               # 네이버 검색 시크릿
LANGSMITH_API_KEY=...                 # LangSmith 모니터링 키
LANGSMITH_TRACING=true                # LangSmith 추적 활성화
```

## 🚨 문제 해결

### 일반적인 문제들

1. **포트 충돌**
   ```bash
   # 포트 사용 확인
   lsof -i :5555
   lsof -i :8501
   
   # 포트 변경 (docker-compose.yml 수정)
   ports:
     - "5556:5555"  # 다른 포트 사용
   ```

2. **컨테이너 시작 실패**
   ```bash
   # 로그 확인
   docker-compose logs backend
   
   # 컨테이너 재시작
   docker-compose restart backend
   ```

3. **환경변수 누락**
   ```bash
   # .env 파일 확인
   cat .env
   
   # 환경변수 확인
   docker exec gta-backend env | grep API
   ```

4. **네트워크 문제**
   ```bash
   # 네트워크 확인
   docker network ls
   docker network inspect gta_gta-network
   
   # 네트워크 재생성
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

### 성능 최적화

1. **메모리 제한 설정**
   ```yaml
   # docker-compose.yml에 추가
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 2G
           reservations:
             memory: 1G
   ```

2. **캐시 활용**
   ```bash
   # 이미지 빌드 시 캐시 활용
   docker-compose build
   
   # BuildKit 사용 (빠른 빌드)
   DOCKER_BUILDKIT=1 docker-compose build
   ```

## 📊 프로덕션 배포

### 프로덕션 환경 설정
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - DEBUG=false
    
  frontend:
    restart: always
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### SSL 인증서 설정
```bash
# Let's Encrypt 사용 예시
certbot --nginx -d yourdomain.com
```

## 🤝 개발 가이드

### 로컬 개발 환경
```bash
# 개발용 볼륨 마운트
docker-compose -f docker-compose.dev.yml up
```

### 코드 변경 반영
```bash
# 백엔드 재시작 (코드 변경 시)
docker-compose restart backend

# 이미지 재빌드 (의존성 변경 시)
docker-compose build backend
```