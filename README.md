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
- 서버 주소: http://localhost:5555
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

## 🤝 기여하기 및 GitHub 운영 가이드

### 📋 핵심 원칙
- **`main` 브랜치는 항상 배포 가능한 상태를 유지합니다**
- **모든 변경 사항은 Pull Request를 통해 이루어집니다**
- **작업 단위는 GitHub Issue를 기반으로 합니다**

### 🌿 브랜치 전략
- `main`: 최종 제품, 항상 안정적이며 배포 가능한 상태
- `feature/{이슈번호}-{설명}`: 새로운 기능 개발 (예: `feature/123-login-ui-update`)
- `hotfix/{이슈번호}-{설명}`: 긴급 버그 수정 (예: `hotfix/145-critical-payment-bug`)

### 📝 커밋 메시지 규칙 (Conventional Commits)
```
type(scope): subject

타입:
- feat: 새로운 기능 추가
- fix: 버그 수정  
- docs: 문서 수정
- style: 코드 포맷팅 (로직 변경 없음)
- refactor: 코드 리팩토링
- test: 테스트 코드 추가/수정
- chore: 빌드, 패키지 매니저 설정 등

예시:
- feat(auth): 소셜 로그인 기능 추가
- fix(api): 사용자 정보 누락 문제 수정 (#123)
```

### 🔄 개발 워크플로우
1. **이슈 생성**: GitHub에서 작업할 내용을 이슈로 등록
2. **브랜치 생성**: `git checkout -b feature/{이슈번호}-{설명}`
3. **개발 및 커밋**: Conventional Commits 규칙에 따라 커밋
4. **Push**: `git push origin feature/{이슈번호}-{설명}`
5. **PR 생성**: 템플릿에 따라 상세한 PR 작성
6. **코드 리뷰**: 최소 1명 이상의 리뷰어 승인 필요
7. **CI 통과**: 자동화된 테스트 및 린트 검사 통과
8. **병합**: Squash and Merge로 `main` 브랜치에 병합

### ✅ PR 체크리스트
- [ ] 관련 이슈 번호 연결
- [ ] 변경 사항 상세 설명
- [ ] 테스트 방법 명시
- [ ] CI 검사 통과
- [ ] 코드 리뷰 승인

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이나 버그 리포트는 이슈를 통해 알려주세요.

---
🤖 **Powered by AI Agents** | Made with ❤️ for Better Travel Planning