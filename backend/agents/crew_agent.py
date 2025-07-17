from crewai import Task, Crew
import logging
from datetime import datetime
from .weather_agent import weather_agent, get_weather_data
from .transport_agent import transport_agent, route_planner, transport_searcher, cost_analyzer, get_web_transport_search, get_real_time_transport_search
from .hotel_agent import hotel_agent, get_hotel_recommendations
from .plan_agent import plan_agent
from .food_agent import food_agent, planner, searcher, analyst, get_real_time_food_data

# 로깅 설정

def setup_crew_logging():
    logger = logging.getLogger('crewai_llm_responses')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler('crew_llm_responses.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger

crew_logger = setup_crew_logging()

def log_agent_interaction(agent_name, task_name, prompt, response, execution_time=None):
    log_message = f"""
{'='*80}
🤖 AGENT: {agent_name}
📋 TASK: {task_name}
⏰ TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{f'⚡ EXECUTION_TIME: {execution_time:.2f}초' if execution_time else ''}

📤 PROMPT:
{prompt}

📥 RESPONSE:
{response}
{'='*80}
"""
    crew_logger.info(log_message)

def get_travel_plan_with_crew(data):
    crew_logger.info(f"🚀 여행 계획 생성 시작 - 목적지: {data.get('destination', '')}")
    import time
    results = {}

    # 1. 날씨 정보
    start_time = time.time()
    weather_info = get_weather_data(
        data.get('destination', ''),
        data.get('start_date', ''),
        data.get('end_date', '')
    )
    weather_prompt = f"""
## 여행 날씨 분석 및 준비물 추천 작업

### 📋 기본 정보
- **목적지**: {data.get('destination', '')}
- **여행 기간**: {data.get('start_date', '')} ~ {data.get('end_date', '')}
- **인원수**: {data.get('people', '')}명
- **여행 목적**: {data.get('purpose', '')}

### 🎯 작업 목표
제공된 실시간 날씨 데이터를 분석하여 여행자가 날씨에 최적화된 준비를 할 수 있도록 구체적이고 실용적인 가이드를 제공합니다.

### 📝 단계별 분석 요구사항

**1단계: 날씨 패턴 분석**
- 여행 기간 중 날씨 변화 패턴 파악
- 기온 변화폭 및 강수 확률 분석
- 특이 날씨 (폭염, 한파, 태풍 등) 가능성 평가

**2단계: 맞춤형 옷차림 추천**
- 일별/시간대별 최적 복장 조합
- 레이어링 기법을 활용한 온도 변화 대응
- 활동별 (관광, 식사, 휴식) 적합한 의류

**3단계: 필수 준비물 선별**
- 날씨별 필수 아이템 (우산, 선크림, 보온용품 등)
- 여행 목적에 따른 특수 준비물
- 현지 구매 vs 미리 준비 구분

**4단계: 안전 및 편의 팁 제공**
- 날씨로 인한 주의사항 및 대처법
- 실내/실외 활동 비율 최적화 제안
- 비상상황 대비 계획

### 📊 출력 형식 (필수)
다음 표 형식으로 정확히 작성해주세요:

| 날짜 | 날씨 | 기온(°C) | 강수확률 | 추천 옷차림 | 필수 준비물 | 주의사항 |
|------|------|----------|----------|-------------|-------------|----------|
| MM/DD | 예: 맑음 | 예: 15-25 | 예: 10% | 예: 긴팔+얇은 겉옷 | 예: 선글라스, 선크림 | 예: 자외선 주의 |

### 📎 참고 데이터
```
{weather_info}
```

### ✅ 품질 검증 요구사항
- 모든 추천은 제공된 날씨 데이터에 근거해야 함
- 여행 목적과 인원수를 고려한 실용적 조언 포함
- 현지에서 쉽게 구할 수 있는 품목과 미리 준비해야 할 품목 구분 명시

### 📎 필수 참고자료 섹션
응답 마지막에 반드시 다음 형식으로 참고 링크를 포함하세요:

**📚 참고자료 및 출처:**
- [사이트명1] URL1 - 정보 설명
- [사이트명2] URL2 - 정보 설명
- [사이트명3] URL3 - 정보 설명

예시:
- [기상청] https://www.weather.go.kr - 날씨 예보 정보
- [OpenWeatherMap] https://openweathermap.org - 실시간 날씨 데이터
"""
    weather_task = Task(
        name="weather",
        description=weather_prompt,
        agent=weather_agent,
        expected_output="날짜별 날씨 예보, 추천 옷차림, 필수 준비물이 표로 정리된 결과"
    )
    weather_crew = Crew(tasks=[weather_task])
    weather_result = weather_crew.kickoff()
    weather_time = time.time() - start_time
    log_agent_interaction("WeatherAgent", "weather_analysis", weather_prompt, str(weather_result), weather_time)
    results['weather'] = str(weather_result)

    # 2. 교통 정보
    start_time = time.time()
    transport_prompt = f"""
## 교통편 분석 및 최적 이동 방안 제시 작업

### 📋 여행 정보
- **출발지**: {data.get('departure', '')}
- **목적지**: {data.get('destination', '')}  
- **여행 기간**: {data.get('start_date', '')} ~ {data.get('end_date', '')}
- **인원수**: {data.get('people', '')}명
- **예산**: {data.get('budget', '')}만원
- **여행 목적**: {data.get('purpose', '')}

### 🎯 분석 목표
출발지에서 목적지까지의 모든 가능한 교통수단을 실시간 검색을 통해 조사하고, 여행자의 조건에 최적화된 이동 방안을 제시합니다.

### 🔍 단계별 분석 요구사항

**1단계: 교통수단 전수조사** (검색 도구 필수 사용)
- 항공편: 직항/경유, 항공사별 요금 및 시간표
- 철도: KTX/SRT/무궁화호 등 등급별 요금 및 소요시간  
- 버스: 고속버스/시외버스 노선 및 요금
- 기타: 렌터카, 지하철, 개인차량 등

**2단계: 비용 대비 효율성 분석**
- 인원수에 따른 총 비용 계산 (개별 vs 단체 할인)
- 예산 범위 내 최적 옵션 선별
- 숨은 비용 (주차비, 식사비, 숙박비 등) 고려

**3단계: 편의성 및 안전성 평가**
- 소요시간 대비 피로도 분석
- 짐 운반 편의성 및 제약사항
- 날씨/계절적 영향 요소 고려

**4단계: 예약 정보 및 실용적 팁**
- 실시간 예약 가능성 확인
- 할인 혜택 및 특가 정보
- 예약 취소/변경 정책

### 📊 출력 형식 (필수)
다음 표 형식으로 정확히 작성해주세요:

| 순위 | 교통수단 | 소요시간 | 총비용 | 예약방법 | 장점 | 단점 | 추천이유 |
|------|----------|----------|--------|----------|------|------|----------|
| 1 | 예: KTX | 예: 2시간30분 | 예: 15만원 | 코레일톡 앱 | 빠름, 편안함 | 비쌈 | 시간 절약 중시시 최적 |

### 🔗 예약 정보 섹션
각 교통수단별로 다음 정보를 포함해야 합니다:
- **공식 예약 사이트 URL**
- **예약 앱 이름**  
- **전화 예약 번호**
- **현재 예약 가능 여부**

### ⚠️ 중요 지침
- **모든 정보는 검색 도구를 통해 수집**: 추측이나 일반적 지식 사용 금지
- **실시간 정보 확인**: 운휴, 지연, 요금 변동 등 최신 상황 반영
- **출처 명시**: 참고한 웹사이트 URL을 반드시 포함
- **검증 가능성**: 제시된 모든 정보가 검증 가능해야 함

### 📎 필수 참고자료 섹션
응답 마지막에 반드시 다음 형식으로 참고 링크를 포함하세요:

**📚 참고자료 및 출처:**
- [사이트명1] URL1 - 정보 설명
- [사이트명2] URL2 - 정보 설명
- [사이트명3] URL3 - 정보 설명

예시:
- [코레일] https://www.letskorail.com - KTX 요금 및 시간표
- [고속버스통합예매] https://www.kobus.co.kr - 고속버스 노선 정보

### 📈 개인화 추천 기준
- 예산 제약: {data.get('budget', '')}만원 범위 내 최적화
- 인원수 고려: {data.get('people', '')}명 단체/개인 특성 반영
- 여행 목적: {data.get('purpose', '')}에 적합한 이동 방식 우선순위
"""
    transport_task = Task(
        name="transport",
        description=transport_prompt,
        agent=transport_agent,
        expected_output="추천 교통수단, 예상 소요 시간, 비용, 장단점이 표로 정리된 결과"
    )
    transport_crew = Crew(tasks=[transport_task])
    transport_result = transport_crew.kickoff()
    transport_time = time.time() - start_time
    log_agent_interaction("TransportAgent", "transport_recommendation", transport_prompt, str(transport_result), transport_time)
    results['transport'] = str(transport_result)

    # 3. 숙소 정보
    start_time = time.time()
    hotel_data = get_hotel_recommendations(
        data.get('destination', ''),
        checkin=data.get('start_date', None),
        checkout=data.get('end_date', None),
        people=data.get('people', None),
        budget=data.get('budget', None),
        purpose=data.get('purpose', None)
    )
    hotel_prompt = f"""
## 숙박시설 분석 및 최적 숙소 추천 작업

### 📋 숙박 조건
- **목적지**: {data.get('destination', '')}
- **체크인**: {data.get('start_date', '')}
- **체크아웃**: {data.get('end_date', '')}
- **인원수**: {data.get('people', '')}명
- **예산**: {data.get('budget', '')}만원
- **여행 목적**: {data.get('purpose', '')}

### 🎯 분석 목표
다양한 숙박시설을 종합적으로 분석하여 여행자의 조건과 목적에 가장 적합한 숙소 옵션을 제시합니다.

### 🔍 단계별 분석 요구사항

**1단계: 숙소 유형별 분석** (검색 도구 필수 사용)
- 호텔: 체인호텔, 부티크호텔, 비즈니스호텔
- 리조트: 올인클루시브, 풀빌라, 스파리조트
- 대안숙소: 펜션, 게스트하우스, 에어비앤비, 한옥스테이

**2단계: 위치적 장점 분석**
- 관광지 접근성: 주요 명소까지의 거리 및 교통편
- 교통 편의성: 공항/역 접근성, 대중교통 연결
- 주변 편의시설: 식당, 편의점, 병원, 쇼핑센터

**3단계: 가성비 및 가격 분석**  
- 1박당 비용 대비 제공 서비스 분석
- 포함 서비스: 조식, 와이파이, 주차, 수영장 등
- 숨은 비용: 리조트피, 세금, 서비스료 등
- 예약 취소 정책 및 유연성

**4단계: 만족도 및 품질 평가**
- 최근 리뷰 동향 및 평점 분석
- 청결도, 서비스 품질, 시설 상태
- 특별한 장점이나 주의사항

### 📊 출력 형식 (필수)
다음 표 형식으로 정확히 작성해주세요:

| 순위 | 숙소명 | 유형 | 위치 | 1박요금 | 총비용 | 주요시설 | 장점 | 단점 | 예약링크 |
|------|--------|------|------|---------|--------|----------|------|------|----------|
| 1 | 예: 그랜드호텔 | 5성급호텔 | 시내중심가 | 15만원 | 45만원 | 조식,주차,스파 | 교통편리 | 비쌈 | booking.com |

### 🏨 세부 정보 섹션
각 추천 숙소별로 다음 정보를 포함:
- **정확한 주소 및 연락처**
- **체크인/아웃 시간**  
- **포함/불포함 서비스 명시**
- **객실 타입 및 최대 수용인원**
- **예약 가능 플랫폼 및 URL**

### 🎯 맞춤형 추천 기준
- **인원수 최적화**: {data.get('people', '')}명에 적합한 객실 구성
- **예산 효율성**: {data.get('budget', '')}만원 내에서 최고 가치
- **목적 부합성**: {data.get('purpose', '')}에 특화된 시설/서비스
- **안전성**: 여행자 안전 및 보안 수준

### 📎 참고 데이터
```
{hotel_data}
```

### ✅ 품질 보증 요구사항
- **실시간 검색 기반**: 모든 정보는 검색 도구로 확인된 최신 정보
- **예약 가능 확인**: 해당 날짜에 실제 예약 가능한 숙소만 추천
- **가격 정확성**: 모든 비용은 세금 및 추가 요금 포함 총액
- **출처 신뢰성**: 공식 웹사이트 또는 검증된 예약 플랫폼 정보

### 📎 필수 참고자료 섹션
응답 마지막에 반드시 다음 형식으로 참고 링크를 포함하세요:

**📚 참고자료 및 출처:**
- [사이트명1] URL1 - 정보 설명
- [사이트명2] URL2 - 정보 설명
- [사이트명3] URL3 - 정보 설명

예시:
- [부킹닷컴] https://www.booking.com - 숙소 정보 및 예약
- [아고다] https://www.agoda.com - 호텔 가격 비교
"""
    hotel_task = Task(
        name="hotel",
        description=hotel_prompt,
        agent=hotel_agent,
        expected_output="추천 숙소 리스트, 위치, 가격대, 편의시설, 객실 타입이 표로 정리된 결과"
    )
    hotel_crew = Crew(tasks=[hotel_task])
    hotel_result = hotel_crew.kickoff()
    hotel_time = time.time() - start_time
    log_agent_interaction("HotelAgent", "hotel_recommendation", hotel_prompt, str(hotel_result), hotel_time)
    results['hotel'] = str(hotel_result)

    # 4. 일정 정보
    start_time = time.time()
    plan_prompt = f"""
## 여행 일정 설계 및 동선 최적화 작업

### 📋 여행 계획 정보
- **목적지**: {data.get('destination', '')}
- **여행 기간**: {data.get('start_date', '')} ~ {data.get('end_date', '')}
- **인원수**: {data.get('people', '')}명
- **여행 목적**: {data.get('purpose', '')}

### 🎯 일정 설계 목표
효율적인 동선과 시간 관리를 통해 여행자가 최대한의 만족도와 경험을 얻을 수 있는 실행 가능한 일정을 제공합니다.

### 🔍 단계별 일정 설계 요구사항

**1단계: 관광자원 조사 및 분류**
- 필수 방문지: 대표 명소, 문화유산, 자연경관
- 체험 활동: 지역 특색 체험, 액티비티, 워크샵
- 휴식 공간: 카페, 공원, 전망대, 휴게시설
- 쇼핑/먹거리: 전통시장, 쇼핑몰, 특산품점

**2단계: 동선 최적화 설계**
- 지리적 근접성을 고려한 효율적 경로 설계
- 교통편 연계 및 이동시간 최소화
- 개장/폐장 시간 고려한 시간대별 배치
- 혼잡도 예상 시간 회피 전략

**3단계: 시간 배분 및 일정 균형**
- 활동 강도와 휴식의 적절한 균형
- 연령대와 체력을 고려한 일정 조절
- 여행 목적에 따른 우선순위 반영
- 날씨 변수 고려한 실내/실외 활동 배치

**4단계: 실용 정보 및 팁 제공**
- 예약 필요 시설 및 마감시간 안내
- 입장료, 주차비 등 예상 비용
- 준비물 및 주의사항
- 대안 계획 및 비상 옵션

### 📊 출력 형식 (필수)
다음 표 형식으로 정확히 작성해주세요:

| 일차 | 시간 | 장소/활동 | 소요시간 | 예상비용 | 이동방법 | 예약필요 | 준비물/팁 |
|------|------|-----------|----------|----------|----------|----------|-----------|
| 1일차 | 09:00 | 예: 경복궁 관람 | 2시간 | 3,000원 | 지하철 | X | 편한 신발 |
| 1일차 | 12:00 | 예: 북촌 한옥마을 | 1시간 | 무료 | 도보 | X | 사진 촬영 |

### 🚀 맞춤화 기준
- **여행 목적 반영**: {data.get('purpose', '')}에 특화된 활동 우선 배치
- **체력 관리**: {data.get('people', '')}명 그룹의 연령대/체력 고려
- **시간 효율성**: 제한된 기간 내 핵심 경험 극대화
- **현실 가능성**: 실제 운영시간과 이동시간 정확 반영

### 📅 일별 구성 원칙
- **오전**: 주요 관광지, 체력 소모가 큰 활동
- **점심**: 지역 특색 음식 체험, 휴식
- **오후**: 문화 체험, 쇼핑, 가벼운 관광
- **저녁**: 야경 명소, 현지 문화 체험
- **야간**: 휴식 또는 선택적 활동

### ⚠️ 중요 고려사항
- **계절/날씨 영향**: 실외 활동의 날씨 의존성 고려
- **현지 사정**: 지역 축제, 휴무일, 특별 이벤트 확인
- **예산 관리**: 일정별 예상 비용의 현실적 산정
- **유연성 확보**: 상황 변화에 대응할 수 있는 대안 제시

### 📎 필수 참고자료 섹션
응답 마지막에 반드시 다음 형식으로 참고 링크를 포함하세요:

**📚 참고자료 및 출처:**
- [사이트명1] URL1 - 정보 설명
- [사이트명2] URL2 - 정보 설명
- [사이트명3] URL3 - 정보 설명

예시:
- [한국관광공사] https://visitkorea.or.kr - 관광지 정보 및 운영시간
- [네이버 지도] https://map.naver.com - 위치 및 교통정보
"""
    plan_task = Task(
        name="plan",
        description=plan_prompt,
        agent=plan_agent,
        expected_output="1일 단위 여행 일정, 각 일정별 소요 시간, 추천 이유, 참고 팁이 표로 정리된 결과"
    )
    plan_crew = Crew(tasks=[plan_task])
    plan_result = plan_crew.kickoff()
    plan_time = time.time() - start_time
    log_agent_interaction("PlanAgent", "itinerary_planning", plan_prompt, str(plan_result), plan_time)
    results['plan'] = str(plan_result)

    # 5. 맛집 정보
    start_time = time.time()
    real_time_food = get_real_time_food_data(data.get('destination', ''))
    food_prompt = f"""
## 맛집 분석 및 미식 여행 큐레이션 작업

### 📋 미식 여행 정보  
- **목적지**: {data.get('destination', '')}
- **여행 기간**: {data.get('start_date', '')} ~ {data.get('end_date', '')}
- **인원수**: {data.get('people', '')}명
- **여행 목적**: {data.get('purpose', '')}

### 🎯 큐레이션 목표
여행지의 음식문화를 깊이 있게 체험할 수 있도록 현지 특색과 여행자 취향을 모두 만족하는 맛집을 선별하여 추천합니다.

### 🔍 단계별 맛집 분석 요구사항

**1단계: 지역 음식문화 조사** (검색 도구 필수 사용)
- 지역 특산물 및 향토 요리 분석
- 계절별 별미 및 제철 재료 활용 메뉴
- 전통 조리법과 현대적 해석의 퓨전 요리
- 현지인 vs 관광객 선호 맛집 구분

**2단계: 카테고리별 분류 및 분석**
- 식사 유형: 아침식사, 점심식사, 저녁식사, 간식/디저트
- 가격대: 서민 맛집, 중급 레스토랑, 고급 다이닝
- 분위기: 캐주얼, 데이트, 가족 친화, 단체 모임
- 특화점: 뷰 맛집, 인스타 핫플, 전통 한식, 이색 체험

**3단계: 접근성 및 편의성 평가**
- 여행 일정과의 동선 연계성
- 대중교통 접근성 및 주차 가능성
- 예약 필요성 및 대기 시간
- 운영 시간 및 휴무일 확인

**4단계: 품질 및 만족도 검증**
- 최신 리뷰 동향 및 평점 분석
- 가격 대비 만족도 평가
- 서비스 품질 및 청결도
- 특별한 장점이나 주의사항

### 📊 출력 형식 (필수)
다음 표 형식으로 정확히 작성해주세요:

| 순위 | 맛집명 | 음식종류 | 가격대 | 대표메뉴 | 위치 | 예약방법 | 추천시간 | 특징/팁 |
|------|--------|----------|--------|----------|------|----------|----------|----------|
| 1 | 예: 할머니국수 | 한식/면요리 | 5천원-1만원 | 멸치국수 | 시내중심가 | 불필요 | 점심 | 현지인 단골, 대기 필수 |

### 🍽️ 상세 정보 섹션
각 추천 맛집별로 다음 정보를 포함:
- **정확한 주소 및 연락처**
- **운영시간 및 휴무일**
- **메뉴 및 가격 정보**
- **예약 방법 (전화/앱/웹사이트)**
- **특별 메뉴나 할인 정보**
- **주차 및 교통편 안내**

### 🎯 맞춤형 큐레이션 기준
- **그룹 특성**: {data.get('people', '')}명 그룹에 적합한 좌석/분위기
- **여행 목적**: {data.get('purpose', '')}에 어울리는 다이닝 경험
- **일정 연계**: 관광 동선과 연계한 효율적 맛집 배치
- **다양성**: 다양한 맛과 경험을 위한 균형 잡힌 선택

### 📎 참고 데이터
```
{real_time_food}
```

### ✅ 품질 보증 요구사항
- **실시간 검색 기반**: 모든 정보는 검색 도구로 확인된 최신 정보
- **운영 상태 확인**: 현재 운영 중이며 예약 가능한 맛집만 추천
- **정보 정확성**: 메뉴, 가격, 운영시간 등 모든 정보의 정확성 보장
- **출처 신뢰성**: 공식 홈페이지, SNS, 신뢰할 수 있는 리뷰 플랫폼 기반

### 📎 필수 참고자료 섹션
응답 마지막에 반드시 다음 형식으로 참고 링크를 포함하세요:

**📚 참고자료 및 출처:**
- [사이트명1] URL1 - 정보 설명
- [사이트명2] URL2 - 정보 설명
- [사이트명3] URL3 - 정보 설명

예시:
- [망고플레이트] https://www.mangoplate.com - 맛집 리뷰 및 평점
- [카카오맵] https://map.kakao.com - 맛집 위치 및 정보

### 🌟 특별 고려사항
- **식이 제한**: 할랄, 비건, 알레르기 대응 가능 맛집 별도 표시
- **현지 에티켓**: 주문 방법, 팁 문화, 테이블 매너 등 안내
- **계절성**: 제철 메뉴나 계절 한정 특별 요리 정보
- **예산 관리**: 식사별 예상 비용 및 전체 예산 내 배분
"""
    food_task = Task(
        name="food",
        description=food_prompt,
        agent=food_agent,
        expected_output="아침/점심/저녁별 추천 맛집, 위치, 가격대, 대표 메뉴, 평점이 표로 정리된 결과"
    )
    food_crew = Crew(tasks=[food_task])
    food_result = food_crew.kickoff()
    food_time = time.time() - start_time
    log_agent_interaction("FoodAgent", "restaurant_recommendation", food_prompt, str(food_result), food_time)
    results['food'] = str(food_result)

    total_time = weather_time + transport_time + hotel_time + plan_time + food_time
    crew_logger.info(f"✅ 모든 에이전트 작업 완료 - 총 소요시간: {total_time:.2f}초")
    return results
