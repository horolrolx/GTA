import os
import requests
from crewai import Agent
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
import sys
sys.path.append('/Users/songchangseok/Desktop/GTA/backend')
from utils.crew_logger import crew_logger, log_function_execution

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if SERPER_API_KEY:
    os.environ["SERPER_API_KEY"] = SERPER_API_KEY

search_tool = SerperDevTool()
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)

transport_agent = Agent(
    role="여행 이동수단 추천 전문가",
    goal="출발지에서 목적지까지의 최적 이동수단을 추천한다. 반드시 검색 도구를 사용하여 실시간 정보를 수집하고, 검색 결과를 바탕으로 구체적인 교통편 정보를 제공해야 함.",
    backstory="여행 이동수단에 대한 다양한 정보를 알고 있으며, 사용자의 예산과 편의에 맞는 교통편을 추천한다. 모든 추천은 검색 도구를 통해 얻은 최신 정보를 바탕으로 한다. 검색 결과에서 실제 시간표, 요금, 예약 링크 등을 추출하여 표 형태로 정리한다.",
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
