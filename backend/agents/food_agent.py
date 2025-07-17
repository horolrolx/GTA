import os
from crewai import Agent
from crewai_tools import SerperDevTool
from langchain_naver_community.utils import NaverSearchAPIWrapper
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

food_agent = Agent(
    role="여행 맛집 추천 전문가",
    goal="여행 목적지의 대표 맛집을 추천한다. 반드시 검색 도구를 사용하여 실시간 정보를 수집하고, 검색 결과를 바탕으로 구체적인 맛집 정보를 제공해야 함.",
    backstory="여행지의 다양한 맛집 정보를 알고 있으며, 사용자의 취향에 맞는 맛집을 추천한다. 모든 추천은 검색 도구를 통해 얻은 최신 정보를 바탕으로 한다. 검색 결과에서 실제 맛집 이름, 위치, 가격, 전화번호, 링크 등을 추출하여 표 형태로 정리한다.",
    tools=[search_tool],
    llm=llm,
    verbose=True,
    max_iter=5
)

planner = Agent(
    role="맛집 탐색 기획 전문가",
    goal="사용자의 모호한 맛집 요청을 분석하여 구체적인 검색 키워드와 실행 계획으로 변환. 반드시 검색 도구를 사용해야 함.",
    backstory="당신은 고객의 숨은 니즈까지 파악하는 베테랑 기획자로, 어떤 요청이든 명확한 분석을 통해 실행 가능한 계획을 수립합니다. 모든 계획은 검색 도구를 통해 확인된 정보를 바탕으로 합니다.",
    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

searcher = Agent(
    role="정보 검색의 달인",
    goal="수립된 계획에 따라 웹에서 가장 정확하고 연관성 높은 맛집 후보 리스트를 수집",
    backstory="당신은 최신 정보를 가장 빠르게 찾아내는 디지털 탐정입니다. 광고와 실제 정보를 구분하는 날카로운 눈을 가지고 있습니다.",
    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

analyst = Agent(
    role="데이터 기반 맛집 비평가",
    goal="수집된 맛집 후보들의 리뷰, 평점 등을 심층 분석하여 최종 추천 리스트와 근거를 제시. 반드시 검색 도구로 추가 정보 수집.",
    backstory="당신은 수많은 리뷰 속에서 진짜 정보를 꿰뚫어 보는 데이터 분석가입니다. 객관적인 데이터에 기반하여 최적의 맛집을 가려냅니다. 모든 분석은 검색 도구를 통해 확인된 최신 정보를 바탕으로 합니다.",
    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

def naver_search(query):
    search = NaverSearchAPIWrapper()
    results = search.results(query)
    return results

@log_function_execution("네이버_맛집_검색")
def get_real_time_food_data(destination):
    query = f"{destination} 맛집 추천"
    results = naver_search(query)
    summary = ""
    for i, item in enumerate(results[:3], 1):
        summary += f"{i}. {item['title']} - {item['description']} (링크: {item['link']})\n"
    return summary

# Only export agent objects and helper functions for use by the central workflow
# No Crew/Task orchestration here
