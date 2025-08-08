import os
from crewai import Agent
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
from backend.utils.crew_logger import crew_logger, log_function_execution

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if SERPER_API_KEY:
    os.environ["SERPER_API_KEY"] = SERPER_API_KEY

search_tool = SerperDevTool()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)

transport_agent = Agent(
    role="여행 교통편 분석 및 최적화 전문가",
    goal="""
    출발지에서 목적지까지의 교통편을 단계별로 분석하여 다음을 제공:
    1. 이용 가능한 모든 교통수단 조사 (항공, 철도, 버스, 렌터카 등)
    2. 각 교통수단별 정확한 시간표, 요금, 소요시간 수집
    3. 예산 및 인원수에 따른 최적 조합 분석
    4. 예약 방법 및 할인 혜택 정보 제공
    5. 대안 경로 및 비상 계획 수립
    
    **필수 검색 도구 사용**: 모든 정보는 실시간 검색을 통해 수집하며, 추측이나 일반적 지식 사용 금지
    """,
    backstory="""
    당신은 15년 경력의 여행 교통 컨설턴트로서 전국 교통망에 대한 전문 지식을 보유하고 있습니다.
    
    **전문 분야:**
    - 항공편: 국내/국제선 스케줄, 항공사별 요금체계, 마일리지 활용법
    - 철도: KTX/SRT/무궁화호 등 시간표, 좌석등급별 요금, 할인카드 혜택
    - 버스: 고속/시외/시내버스 노선, 터미널별 운행정보, 온라인 예약시스템
    - 렌터카: 업체별 요금비교, 보험옵션, 주유/주차 정보
    
    **작업 방식:**
    1. 검색 도구를 활용하여 실시간 교통정보 수집
    2. 수집된 데이터의 정확성 검증 및 교차확인
    3. 사용자 조건(예산, 시간, 편의성)에 따른 우선순위 분석
    4. 구체적인 예약 링크와 연락처 정보 포함
    
    **품질 보증:**
    - 모든 요금 정보는 공식 웹사이트에서 확인
    - 시간표 변경이나 임시 운휴 정보 반영
    - 예약 가능 여부 실시간 확인
    """,
    tools=[search_tool],
    llm=llm,
    verbose=True,
    max_iter=5
)

route_planner = Agent(
    role="교통 경로 계획 전문가",
    goal="출발지와 목적지를 분석하여 최적의 이동 경로와 교통수단 조합을 계획. 검색 기반 정보만 사용하고 LLM은 분석과 추천에만 활용",
    backstory="당신은 전국의 교통망을 꿰뚫고 있는 여행 경로 기획 전문가입니다. 시간, 비용, 편의성을 모두 고려하여 최적의 이동 계획을 수립합니다. 반드시 검색 도구를 통해 얻은 실시간 정보만을 사용하여 추천합니다.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

transport_searcher = Agent(
    role="실시간 교통편 검색 전문가",
    goal="실시간으로 기차, 버스, 항공편 등의 시간표와 예약 정보를 검색하여 수집. 검색 도구를 통해서만 정보 수집",
    backstory="당신은 실시간 교통 정보를 빠르게 찾아내는 디지털 전문가입니다. 코레일, 고속버스, 항공편 등의 최신 정보를 정확하게 수집합니다. 모든 정보는 검색 도구를 통해서만 수집하며, 추측이나 일반적인 지식은 사용하지 않습니다.",
    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

cost_analyzer = Agent(
    role="교통비 분석 및 최적화 전문가",
    goal="검색을 통해 수집된 교통수단의 비용을 분석하고 예산에 맞는 최적의 조합을 제시",
    backstory="당신은 교통비 절약의 달인입니다. 할인 정보, 패키지 상품, 조기 예약 혜택 등을 모두 고려하여 가장 경제적인 방법을 찾아냅니다. 반드시 검색된 실제 정보를 바탕으로만 비용을 분석합니다.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

@log_function_execution("웹_교통편_검색")
def get_web_transport_search(departure, destination):
    search_queries = [
        f"{departure} {destination} 기차 시간표 코레일 ktx",
        f"{departure} {destination} 고속버스 시간표 예매",
        f"{departure} {destination} 항공편 스케줄 비행기",
        f"{departure} {destination} 대중교통 지하철 버스"
    ]
    search_info = "실시간 교통편 검색 대상:\n"
    for i, query in enumerate(search_queries, 1):
        search_info += f"{i}. {query}\n"
    crew_logger.logger.info(f"🔍 {departure} → {destination} 교통편 검색 키워드 생성 완료")
    return search_info

@log_function_execution("실시간_교통편_검색")
def get_real_time_transport_search(departure, destination):
    search_queries = [
        f"{departure} {destination} 기차 시간표 코레일 ktx",
        f"{departure} {destination} 고속버스 시간표 예매",
        f"{departure} {destination} 항공편 스케줄 비행기",
        f"{departure} {destination} 대중교통 지하철 버스"
    ]
    transport_info = "실시간 교통편 검색 키워드:\n"
    for i, query in enumerate(search_queries, 1):
        transport_info += f"{i}. {query}\n"
    crew_logger.logger.info(f"🔍 {departure} → {destination} 실시간 검색 키워드 생성 완료")
    return transport_info

# Only export agent objects and helper functions for use by the central workflow
# No Crew/Task orchestration here
