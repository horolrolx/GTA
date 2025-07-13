# ✈️ Good Travel Agent (GTA)

맞춤형 여행 일정 추천 AI 에이전트 시스템

## 📋 프로젝트 개요

Good Travel Agent는 여행 계획에 필요한 모든 정보를 통합적으로 제공하는 AI 기반 여행 추천 시스템입니다. 여행지, 예산, 선호도, 교통, 숙박, 음식 등 다양한 개인 특성을 고려하여 사용자 맞춤형 여행 계획을 효율적으로 제시합니다.

### 🤖 AI 에이전트 구성

- **날씨 에이전트**: 여행 기간 날씨 예보, 옷차림 및 준비물 추천
- **교통 에이전트**: 최적 이동수단 추천, 예상 비용 및 소요시간
- **숙박 에이전트**: 위치별 숙소 추천, 가격대 및 편의시설 정보
- **일정 에이전트**: 효율적인 동선 계획, 관광지 및 체험 추천
- **음식 에이전트**: 현지 맛집 추천, 예산별 식당 정보

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 필수 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 필요한 API 키들을 설정
```

### 2. 서버 실행

**백엔드 서버 실행:**
```bash
python run_backend.py
```
- 서버 주소: http://localhost:5000
- API 엔드포인트:
  - `GET /health`: 서버 상태 확인
  - `POST /plan`: 통합 여행 계획 생성
  - `POST /weather`: 날씨 정보만 조회

**프론트엔드 실행:**
```bash
python run_frontend.py
```
- 웹 주소: http://localhost:8501

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
│   └── app.py                 # Flask API 서버
├── frontend/                   # 프론트엔드 웹 인터페이스
│   └── app.py                 # Streamlit 앱
├── requirements.txt           # Python 패키지 의존성
├── .env.example              # 환경 변수 템플릿
├── run_backend.py            # 백엔드 실행 스크립트
├── run_frontend.py           # 프론트엔드 실행 스크립트
└── README.md                 # 프로젝트 문서
```

## 🔧 API 키 설정

프로젝트를 완전히 사용하려면 다음 API 키들이 필요합니다:

### 필수 API 키
- **OpenAI API Key**: AI 에이전트들의 언어 모델 사용

### 선택적 API 키 (더 나은 추천을 위해)
- **OpenWeatherMap API**: 실시간 날씨 정보
- **네이버 검색 API**: 실시간 맛집 정보
- **한국관광공사 API**: 교통 및 관광 정보

`.env` 파일 예시:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here
VISITKOREA_API_KEY=your_visitkorea_api_key_here
```

## 💡 사용 방법

1. **프론트엔드 접속**: http://localhost:8501
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

## 🔬 기술 스택

- **백엔드**: Flask, CrewAI, OpenAI
- **프론트엔드**: Streamlit
- **AI Framework**: CrewAI (Multi-Agent Collaboration)
- **API 통합**: OpenWeatherMap, 네이버 검색, 한국관광공사

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이나 버그 리포트는 이슈를 통해 알려주세요.

---
🤖 **Powered by AI Agents** | Made with ❤️ for Better Travel Planning