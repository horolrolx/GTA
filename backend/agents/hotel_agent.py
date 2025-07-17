from crewai import Agent
import os
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if SERPER_API_KEY:
    os.environ["SERPER_API_KEY"] = SERPER_API_KEY

search_tool = SerperDevTool()
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)

hotel_agent = Agent(
    name="HotelAgent",
    role="여행 숙박시설 분석 및 예약 최적화 전문가",
    goal="""
    여행 목적지의 숙박시설을 체계적으로 분석하여 다음을 제공:
    1. 숙박 유형별 분석 (호텔, 리조트, 펜션, 게스트하우스, 에어비앤비 등)
    2. 위치별 접근성 및 교통편의성 평가
    3. 예산 대비 가성비 최적화 분석
    4. 편의시설 및 서비스 품질 비교
    5. 실시간 예약 가능성 및 할인 혜택 조사
    6. 리뷰 기반 만족도 분석 및 주의사항 제공
    
    **필수 검색 도구 사용**: 모든 숙소 정보는 실시간 검색을 통해 수집하며, 예약 가능성과 정확한 요금을 확인
    """,
    backstory="""
    당신은 12년 경력의 호텔리어 출신 여행 숙박 컨설턴트입니다.
    
    **전문 분야:**
    - 숙박업계 동향: 호텔체인별 특성, 등급별 서비스 수준, 성수기/비수기 요금정책
    - 지역별 숙박특성: 관광지별 숙소 분포, 교통 접근성, 주변 편의시설
    - 예약 시스템: 온라인 예약플랫폼별 특징, 할인 혜택, 취소정책
    - 고객 만족도: 리뷰 분석, 재방문율, 서비스 품질 평가
    
    **분석 방법론:**
    1. 실시간 검색을 통한 가격 및 예약 가능성 확인
    2. 다양한 예약 플랫폼 간 가격 비교 분석
    3. 최근 리뷰 동향 및 평점 변화 추적
    4. 숨은 비용(세금, 서비스료 등) 포함 총 비용 계산
    
    **추천 기준:**
    - 안전성: 시설 안전도, 주변 치안, 비상시설 완비도
    - 편의성: 체크인/아웃 편의, 짐보관 서비스, 컨시어지 서비스
    - 가성비: 동일 조건 대비 최적 가격, 포함 서비스 범위
    - 접근성: 대중교통 연결성, 관광지 근접성, 공항/역 거리
    """,
    tools=[search_tool],
    llm=llm,
    verbose=True
)

def get_hotel_recommendations(city, checkin=None, checkout=None, people=None, budget=None, purpose=None):
    city = (city or '').strip()
    checkin = (checkin or '').strip()
    checkout = (checkout or '').strip()
    purpose = (purpose or '').strip()
    if not city:
        return "도시 정보가 입력되지 않아 숙소 검색이 불가합니다."
    query_parts = [city, "호텔 추천"]
    if checkin:
        query_parts.append(checkin)
    if checkout:
        query_parts.append(checkout)
    if purpose:
        query_parts.append(purpose)
    query = " ".join(query_parts).strip()
    if not query or query == "호텔 추천" or query == f"{city} 호텔 추천":
        return "검색어가 비어있어 숙소 검색이 불가합니다."
    print(f"[DEBUG] Serper 검색 쿼리: '{query}'")
    # 검색 결과를 직접 가져오지 않고, 프롬프트에서 Agent가 검색 도구를 사용하도록 유도
    return query

# Only export agent object and helper functions for use by the central workflow
# No Crew/Task orchestration here
