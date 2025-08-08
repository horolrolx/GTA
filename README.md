# ✈️ Good Travel Agent (GTA)

AI 기반 맞춤형 여행 계획 추천 시스템

## 📋 프로젝트 개요

Good Travel Agent는 여행 계획에 필요한 모든 정보를 통합적으로 제공하는 AI 기반 여행 추천 시스템입니다. 여행지, 예산, 선호도, 교통, 숙박, 음식 등 다양한 개인 특성을 고려하여 사용자 맞춤형 여행 계획을 효율적으로 제시합니다.

### 🤖 AI 에이전트 구성

- **🌤️ 날씨 에이전트**: 여행 기간 날씨 예보, 옷차림 및 준비물 추천
- **🚗 교통 에이전트**: 최적 이동수단 추천, 예상 비용 및 소요시간
- **🏨 숙박 에이전트**: 위치별 숙소 추천, 가격대 및 편의시설 정보
- **📅 일정 에이전트**: 효율적인 동선 계획, 관광지 및 체험 추천
- **🍽️ 음식 에이전트**: 현지 맛집 추천, 예산별 식당 정보

## 🚀 빠른 시작

### 방법 1: Docker로 실행 (권장)

가장 간편한 방법으로, 모든 의존성이 포함된 Docker 이미지를 사용합니다.

```bash
# 1. 프로젝트 클론
git clone https://github.com/horolrolx/GTA.git
cd GTA

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 필요한 API 키들을 설정

# 3. Docker Compose로 실행
docker compose up -d --build
```

**접속 주소:**
- 프론트엔드: http://localhost:8501
- 백엔드 API: http://localhost:5555

### 방법 2: 로컬 환경에서 실행

```bash
# 1. 프로젝트 클론
git clone https://github.com/horolrolx/GTA.git
cd GTA

# 2. Python 가상환경 생성 및 활성화
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 필요한 API 키들을 설정

# 5. 서버 실행
# 백엔드 실행
python run_backend.py

# 새 터미널에서 프론트엔드 실행
python run_frontend.py
```

### 방법 3: 프록스목스 배포

프록스목스 서버에 배포하여 외부에서 접속 가능하게 설정:

```bash
# 1. 서버에 프로젝트 업로드
git clone https://github.com/horolrolx/GTA.git
cd GTA

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 3. Docker Compose로 실행
docker compose up -d --build
```

**접속 주소:**
- 프론트엔드: http://211.227.149.168:8501
- 백엔드 API: http://211.227.149.168:5555

## 🔧 환경 변수 설정

프로젝트를 완전히 사용하려면 다음 API 키들이 필요합니다:

### 필수 API 키
- **OPENAI_API_KEY**: AI 에이전트들의 언어 모델 사용
- **SERPER_API_KEY**: 웹 검색 도구(Serper) 사용

### 선택적 API 키 (더 나은 추천을 위해)
- **OPENWEATHER_API_KEY**: 실시간 날씨 정보
- **NAVER_CLIENT_ID**: 네이버 검색 API
- **NAVER_CLIENT_SECRET**: 네이버 검색 API
- **VISITKOREA_API_KEY**: 한국관광공사 API

`.env` 파일 예시:
```env
# 필수 API 키
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# 선택적 API 키
OPENWEATHER_API_KEY=your_openweather_api_key_here
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here
VISITKOREA_API_KEY=your_visitkorea_api_key_here
```

## 💡 사용 방법

1. **프론트엔드 접속**: http://localhost:8501 (로컬) 또는 http://211.227.149.168:8501 (프록스목스)
2. **여행 정보 입력**:
   - 출발지와 목적지
   - 여행 기간
   - 인원수와 예산
   - 여행 목적 및 특이사항
3. **AI 추천 결과 확인**:
   - 날씨 정보 및 준비물
   - 교통편 추천
   - 숙소 추천
   - 상세 일정
   - 맛집 추천

## 🛠️ 프로젝트 구조

```
GTA/
├── backend/                    # 백엔드 API 서버
│   ├── agents/                # AI 에이전트들
│   │   ├── weather_agent.py   # 날씨 정보 에이전트
│   │   ├── transport_agent.py # 교통 정보 에이전트
│   │   ├── hotel_agent.py     # 숙박 정보 에이전트
│   │   ├── plan_agent.py      # 일정 계획 에이전트
│   │   ├── food_agent.py      # 맛집 추천 에이전트
│   │   └── crew_agent.py      # 통합 협업 에이전트
│   ├── utils/                 # 유틸리티
│   │   └── crew_logger.py     # 로깅 시스템
│   └── app.py                 # Flask API 서버
├── frontend/                   # 프론트엔드 웹 인터페이스
│   └── app.py                 # Streamlit 앱
├── requirements.txt           # Python 패키지 의존성
├── docker-compose.yml        # Docker Compose 설정
├── Dockerfile.backend        # 백엔드 Docker 이미지
├── Dockerfile.frontend       # 프론트엔드 Docker 이미지
├── .dockerignore             # Docker 빌드 제외 파일
├── .env.example              # 환경 변수 템플릿
├── run_backend.py            # 백엔드 실행 스크립트
├── run_frontend.py           # 프론트엔드 실행 스크립트
└── README.md                 # 프로젝트 문서
```

## 🔬 기술 스택

### 백엔드
- **Flask**: RESTful API 서버
- **CrewAI**: 멀티 에이전트 협업 프레임워크
- **OpenAI GPT**: 언어 모델
- **Gunicorn**: 프로덕션 WSGI 서버

### 프론트엔드
- **Streamlit**: 웹 인터페이스
- **Requests**: HTTP 클라이언트

### 도구 및 서비스
- **Serper**: 웹 검색 API
- **OpenWeatherMap**: 날씨 정보 API
- **네이버 검색 API**: 맛집 정보
- **한국관광공사 API**: 관광 정보

### 컨테이너화
- **Docker**: 컨테이너 플랫폼
- **Docker Compose**: 멀티 서비스 오케스트레이션

## 🐳 Docker 사용법

### 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# 필수 환경 변수 설정
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

### 서비스 실행
```bash
# 모든 서비스 시작
docker compose up -d --build

# 로그 확인
docker compose logs -f

# 서비스 중지
docker compose down
```

### 개별 서비스 관리
```bash
# 백엔드만 재시작
docker compose restart backend

# 프론트엔드만 재시작
docker compose restart frontend

# 특정 서비스 로그 확인
docker compose logs backend
```

## 🔍 API 엔드포인트

### 백엔드 API (포트: 5555)

- `GET /`: API 정보
- `GET /health`: 서버 상태 확인
- `POST /plan`: 통합 여행 계획 생성
- `POST /weather`: 날씨 정보만 조회

### 요청 예시
```bash
curl -X POST http://localhost:5555/plan \
  -H "Content-Type: application/json" \
  -d '{
    "departure": "서울",
    "destination": "제주도",
    "start_date": "2024-03-15",
    "end_date": "2024-03-18",
    "people": 2,
    "budget": 50,
    "purpose": "커플여행"
  }'
```

## 🚀 배포 가이드

### 로컬 개발 환경
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 서버 실행
python run_backend.py
python run_frontend.py
```

### Docker 배포
```bash
# 프로덕션 빌드
docker compose -f docker-compose.yml up -d --build

# 환경 변수 확인
docker compose config
```

### 프록스목스 배포
```bash
# 서버에 프로젝트 업로드
git clone https://github.com/horolrolx/GTA.git
cd GTA

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# Docker Compose로 실행
docker compose up -d --build

# 접속 확인
curl http://211.227.149.168:8501
```

### 클라우드 배포
- **AWS**: ECS 또는 EC2 + Docker
- **GCP**: Cloud Run 또는 GKE
- **Azure**: Container Instances 또는 AKS

## 🤝 기여하기

### 개발 환경 설정
1. 프로젝트 포크
2. 로컬에 클론
3. 브랜치 생성: `git checkout -b feature/your-feature`
4. 변경사항 커밋
5. Pull Request 생성

### 코드 스타일
- Python: PEP 8 준수
- 커밋 메시지: Conventional Commits 형식
- 문서화: 한글 주석 및 README 업데이트

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의 및 지원

- **이슈 리포트**: GitHub Issues 사용
- **기능 요청**: GitHub Discussions 사용
- **버그 리포트**: 상세한 재현 단계와 함께 이슈 생성

## 🔄 업데이트 로그

### v1.0.0 (2024-03-XX)
- ✅ Docker 컨테이너화 지원 추가
- ✅ AI 에이전트 안정성 개선
- ✅ 환경 변수 기반 설정 시스템
- ✅ 크로스 플랫폼 호환성 확보
- ✅ 헬스체크 및 의존성 관리
- ✅ 프로덕션급 서버 설정 (Gunicorn)
- ✅ 프록스목스 배포 지원 추가

---

🤖 **Powered by AI Agents** | Made with ❤️ for Better Travel Planning

각 분야 전문 에이전트들이 협업하여 최적의 여행 계획을 제공합니다.