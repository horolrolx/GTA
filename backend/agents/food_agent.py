import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_naver_community.utils import NaverSearchAPIWrapper

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if SERPER_API_KEY:
    os.environ["SERPER_API_KEY"] = SERPER_API_KEY

search_tool = SerperDevTool()

food_agent = Agent(
    name="FoodAgent",
    role="여행 맛집 추천 전문가",
    goal="여행 목적지의 대표 맛집을 추천한다.",
    backstory="여행지의 다양한 맛집 정보를 알고 있으며, 사용자의 취향에 맞는 맛집을 추천한다.",
    llm_config={
        "provider": "openai",
        "config": {
            "model": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY
        }
    }
)

planner = Agent(
    role="맛집 탐색 기획 전문가",
    goal="사용자의 모호한 맛집 요청을 분석하여 구체적인 검색 키워드와 실행 계획으로 변환",
    backstory="당신은 고객의 숨은 니즈까지 파악하는 베테랑 기획자로, "
              "어떤 요청이든 명확한 분석을 통해 실행 가능한 계획을 수립합니다.",
    verbose=True,
    allow_delegation=False,
)

searcher = Agent(
    role="정보 검색의 달인",
    goal="수립된 계획에 따라 웹에서 가장 정확하고 연관성 높은 맛집 후보 리스트를 수집",
    backstory="당신은 최신 정보를 가장 빠르게 찾아내는 디지털 탐정입니다. "
              "광고와 실제 정보를 구분하는 날카로운 눈을 가지고 있습니다.",
    tools=[search_tool],
    verbose=True,
    allow_delegation=False,
)

analyst = Agent(
    role="데이터 기반 맛집 비평가",
    goal="수집된 맛집 후보들의 리뷰, 평점 등을 심층 분석하여 최종 추천 리스트와 근거를 제시",
    backstory="당신은 수많은 리뷰 속에서 진짜 정보를 꿰뚫어 보는 데이터 분석가입니다. "
              "객관적인 데이터에 기반하여 최적의 맛집을 가려냅니다.",
    verbose=True,
    allow_delegation=False,
)

def naver_search(query):
    search = NaverSearchAPIWrapper()
    results = search.results(query)
    return results

def get_real_time_food_data(destination):
    query = f"{destination} 맛집 추천"
    results = naver_search(query)
    summary = ""
    for i, item in enumerate(results[:3], 1):
        summary += f"{i}. {item['title']} - {item['description']} (링크: {item['link']})\n"
    return summary

def get_food_plan(data):
    real_time_food = get_real_time_food_data(data.get('destination', ''))
    prompt = f"""
목적지: {data.get('destination', '')}
여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
인원수: {data.get('people', '')}
여행 목적/특이사항: {data.get('purpose', '')}

아래 조건을 모두 반영해서 현실적으로 추천해줘.
- 네이버 실시간 검색 결과(아래 참고)를 반영해서 추천
- 여행 일정과 동선을 고려해 방문하기 좋은 맛집 추천(아침, 점심, 저녁 구분)
- 지역별 대표 음식, 현지 인기 맛집, 숨은 맛집 등 다양하게 제안
- 가격대, 위치, 대표 메뉴, 예약 필요 여부, 현지인/관광객 평점 등도 안내
- 표 형태로 정리

[네이버 실시간 검색 결과]
{real_time_food}
"""
    result = food_agent.run(prompt)
    return {'맛집': str(result)}

def get_enhanced_food_plan(user_request):
    plan_task = Task(
        description=f"사용자 요청 '{user_request}'을 분석하여, 검색에 사용할 핵심 조건(지역, 메뉴, 분위기, 인원)을 명확히 정리하고, 검색할 키워드 목록을 생성하라.",
        expected_output="검색에 사용할 구체적인 키워드 목록과 검색 조건이 담긴 보고서",
        agent=planner,
    )

    search_task = Task(
        description="생성된 키워드를 사용하여 웹 검색을 실행하고, 조건에 부합하는 맛집 후보 5곳의 이름, 대표 메뉴, 특징, 리뷰 요약을 수집하라.",
        expected_output="각 맛집 후보에 대한 기본 정보(이름, 메뉴, 특징)와 온라인 리뷰 요약이 포함된 리스트",
        agent=searcher,
        context=[plan_task],
    )

    analysis_task = Task(
        description="수집된 맛집 리스트를 최종 분석하여, 사용자의 요청에 가장 적합한 Top 3를 선정하고, 각 맛집을 추천하는 이유와 고려할 점을 상세히 정리하여 최종 보고서를 작성하라.",
        expected_output="최종 추천 맛집 3곳의 이름, 주소, 추천 이유, 대표 메뉴, 가격대, 분위기, 그리고 예약 필요 여부 등 상세 정보가 담긴 완결된 보고서",
        agent=analyst,
        context=[search_task],
    )

    matjip_crew = Crew(
        agents=[planner, searcher, analyst],
        tasks=[plan_task, search_task, analysis_task],
        process=Process.sequential,
        verbose=2,
    )

    result = matjip_crew.kickoff()
    return {'맛집': str(result)}

def get_hybrid_food_plan(data):
    destination = data.get('destination', '')
    
    # 1. 네이버 검색으로 실시간 맛집 정보 수집
    real_time_food = get_real_time_food_data(destination)
    
    # 2. 사용자 요청을 자연어로 구성
    user_request = f"""
    목적지: {destination}
    여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
    인원수: {data.get('people', '')}명
    여행 목적: {data.get('purpose', '')}
    예산: {data.get('budget', '')}만원
    
    이 조건에 맞는 맛집을 추천해주세요.
    """
    
    # 3. 크루 에이전트가 네이버 검색 결과를 활용하도록 설정
    enhanced_searcher = Agent(
        role="정보 검색 및 분석 전문가",
        goal="네이버 검색 결과와 웹 검색을 결합하여 가장 정확한 맛집 후보 리스트를 수집",
        backstory="당신은 네이버 검색 결과와 구글 검색을 모두 활용하여 최신 정보를 찾아내는 전문가입니다. "
                  "광고와 실제 정보를 구분하는 날카로운 눈을 가지고 있습니다.",
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
    )
    
    # 4. 태스크 정의 (네이버 검색 결과 포함)
    plan_task = Task(
        description=f"사용자 요청 '{user_request}'을 분석하여, 검색에 사용할 핵심 조건을 명확히 정리하고, 검색할 키워드 목록을 생성하라.",
        expected_output="검색에 사용할 구체적인 키워드 목록과 검색 조건이 담긴 보고서",
        agent=planner,
    )

    hybrid_search_task = Task(
        description=f"""
        다음 네이버 실시간 검색 결과를 참고하여 추가 웹 검색을 실행하고, 
        조건에 부합하는 맛집 후보 5곳의 이름, 대표 메뉴, 특징, 리뷰 요약을 수집하라.
        
        [네이버 검색 결과 참고]
        {real_time_food}
        
        위 정보를 바탕으로 추가 검색을 실행하여 더 상세한 정보를 수집하라.
        """,
        expected_output="네이버 검색 결과를 포함한 각 맛집 후보에 대한 기본 정보(이름, 메뉴, 특징)와 온라인 리뷰 요약이 포함된 리스트",
        agent=enhanced_searcher,
        context=[plan_task],
    )

    analysis_task = Task(
        description="수집된 맛집 리스트를 최종 분석하여, 사용자의 요청에 가장 적합한 Top 3를 선정하고, 각 맛집을 추천하는 이유와 고려할 점을 상세히 정리하여 최종 보고서를 작성하라.",
        expected_output="최종 추천 맛집 3곳의 이름, 주소, 추천 이유, 대표 메뉴, 가격대, 분위기, 그리고 예약 필요 여부 등 상세 정보가 담긴 완결된 보고서",
        agent=analyst,
        context=[hybrid_search_task],
    )

    # 5. 크루 실행
    hybrid_crew = Crew(
        agents=[planner, enhanced_searcher, analyst],
        tasks=[plan_task, hybrid_search_task, analysis_task],
        process=Process.sequential,
        verbose=2,
    )

    result = hybrid_crew.kickoff()
    return {'맛집': str(result)}
