import os
import requests
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if SERPER_API_KEY:
    os.environ["SERPER_API_KEY"] = SERPER_API_KEY

search_tool = SerperDevTool()

transport_agent = Agent(
    name="TransportAgent",
    role="여행 이동수단 추천 전문가",
    goal="출발지에서 목적지까지의 최적 이동수단을 추천한다.",
    backstory="여행 이동수단에 대한 다양한 정보를 알고 있으며, 사용자의 예산과 편의에 맞는 교통편을 추천한다.",
    llm_config={
        "provider": "openai",
        "config": {
            "model": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY
        }
    }
)

route_planner = Agent(
    role="교통 경로 계획 전문가",
    goal="출발지와 목적지를 분석하여 최적의 이동 경로와 교통수단 조합을 계획",
    backstory="당신은 전국의 교통망을 꿰뚫고 있는 여행 경로 기획 전문가입니다. "
              "시간, 비용, 편의성을 모두 고려하여 최적의 이동 계획을 수립합니다.",
    verbose=True,
    allow_delegation=False,
)

transport_searcher = Agent(
    role="실시간 교통편 검색 전문가",
    goal="실시간으로 기차, 버스, 항공편 등의 시간표와 예약 정보를 검색하여 수집",
    backstory="당신은 실시간 교통 정보를 빠르게 찾아내는 디지털 전문가입니다. "
              "코레일, 고속버스, 항공편 등의 최신 정보를 정확하게 수집합니다.",
    tools=[search_tool],
    verbose=True,
    allow_delegation=False,
)

cost_analyzer = Agent(
    role="교통비 분석 및 최적화 전문가",
    goal="다양한 교통수단의 비용을 분석하고 예산에 맞는 최적의 조합을 제시",
    backstory="당신은 교통비 절약의 달인입니다. "
              "할인 정보, 패키지 상품, 조기 예약 혜택 등을 모두 고려하여 가장 경제적인 방법을 찾아냅니다.",
    verbose=True,
    allow_delegation=False,
)

def get_web_transport_search(departure, destination):
    """웹 검색 기반 교통편 정보 수집"""
    search_queries = [
        f"{departure} {destination} 기차 시간표 코레일 ktx",
        f"{departure} {destination} 고속버스 시간표 예매",
        f"{departure} {destination} 항공편 스케줄 비행기",
        f"{departure} {destination} 대중교통 지하철 버스"
    ]
    
    search_info = "실시간 교통편 검색 대상:\n"
    for i, query in enumerate(search_queries, 1):
        search_info += f"{i}. {query}\n"
    
    return search_info

def get_real_time_transport_search(departure, destination):
    """실시간 교통편 검색 키워드 생성"""
    search_queries = [
        f"{departure} {destination} 기차 시간표 코레일 ktx",
        f"{departure} {destination} 고속버스 시간표 예매",
        f"{departure} {destination} 항공편 스케줄 비행기",
        f"{departure} {destination} 대중교통 지하철 버스"
    ]
    
    transport_info = "실시간 교통편 검색 키워드:\n"
    for i, query in enumerate(search_queries, 1):
        transport_info += f"{i}. {query}\n"
    
    return transport_info

def get_transport_plan(data):
    departure = data.get('departure', '')
    destination = data.get('destination', '')
    web_search_info = get_web_transport_search(departure, destination)
    
    prompt = f"""
출발지: {departure}
목적지: {destination}
여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
인원수: {data.get('people', '')}
예산: {data.get('budget', '')}만원
여행 목적/특이사항: {data.get('purpose', '')}

아래 조건을 모두 반영해서 현실적으로 추천해줘.
- 출발지에서 목적지까지 이동 가능한 실제 교통수단(항공, 기차, 버스, 지하철 등)을 구체적으로 제시
- 예상 소요 시간, 대략적인 비용, 장단점(예: 빠름/저렴함/경유 필요 등)도 함께 안내
- 예산과 인원수, 여행 목적(예: 가족, 커플, 액티비티 등)에 따라 추천 우선순위가 달라지도록
- 추천 교통수단별로 표 형태로 정리
- 실시간 예약 가능한 사이트나 앱 정보도 포함

[웹 검색 기반 교통편 정보]
{web_search_info}
"""
    result = transport_agent.run(prompt)
    return {'이동수단': str(result)}

def get_enhanced_transport_plan(user_request):
    route_task = Task(
        description=f"사용자 요청 '{user_request}'을 분석하여 최적의 이동 경로를 계획하고, 검색할 교통수단과 키워드를 정리하라.",
        expected_output="출발지-목적지 경로 분석과 추천 교통수단 목록이 포함된 계획서",
        agent=route_planner,
    )

    search_task = Task(
        description="계획된 경로에 따라 실시간 교통편(기차, 버스, 항공편) 시간표와 예약 정보를 검색하여 수집하라.",
        expected_output="각 교통수단별 시간표, 요금, 예약 방법이 포함된 상세 정보 리스트",
        agent=transport_searcher,
        context=[route_task],
    )

    cost_task = Task(
        description="수집된 교통편 정보를 바탕으로 비용을 분석하고, 예산에 맞는 최적의 교통수단을 추천하라.",
        expected_output="비용 분석 결과와 예산별 추천 교통수단 Top 3 (시간, 비용, 편의성 포함)",
        agent=cost_analyzer,
        context=[search_task],
    )

    transport_crew = Crew(
        agents=[route_planner, transport_searcher, cost_analyzer],
        tasks=[route_task, search_task, cost_task],
        process=Process.sequential,
        verbose=2,
    )

    result = transport_crew.kickoff()
    return {'이동수단': str(result)}

def get_hybrid_transport_plan(data):
    departure = data.get('departure', '')
    destination = data.get('destination', '')
    
    # 1. 웹 검색 기반 교통편 정보 수집
    web_search_info = get_web_transport_search(departure, destination)
    
    # 2. 실시간 교통편 검색 정보 수집
    realtime_search = get_real_time_transport_search(departure, destination)
    
    # 3. 사용자 요청을 자연어로 구성
    user_request = f"""
    출발지: {departure}
    목적지: {destination}
    여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
    인원수: {data.get('people', '')}명
    예산: {data.get('budget', '')}만원
    여행 목적: {data.get('purpose', '')}
    
    이 조건에 맞는 최적의 교통수단을 추천해주세요.
    """
    
    # 4. 통합 검색 에이전트 생성
    hybrid_searcher = Agent(
        role="실시간 교통 정보 검색 전문가",
        goal="웹 검색을 통해 가장 정확하고 최신의 교통 정보를 수집",
        backstory="당신은 웹 검색을 활용하여 최신 교통 정보를 찾아내는 전문가입니다. "
                  "정확한 시간표와 요금 정보를 제공합니다.",
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
    )
    
    # 5. 태스크 정의
    route_task = Task(
        description=f"사용자 요청 '{user_request}'을 분석하여 최적의 이동 경로를 계획하라.",
        expected_output="출발지-목적지 경로 분석과 추천 교통수단 목록",
        agent=route_planner,
    )

    hybrid_search_task = Task(
        description=f"""
        다음 정보를 참고하여 실시간 교통편 검색을 실행하라:
        
        [웹 검색 기반 교통편 정보]
        {web_search_info}
        
        [실시간 검색 대상]
        {realtime_search}
        
        위 정보를 바탕으로 웹 검색을 실행하여 최신 시간표와 요금 정보를 수집하라.
        """,
        expected_output="웹 검색 결과를 통합한 상세 교통편 정보",
        agent=hybrid_searcher,
        context=[route_task],
    )

    cost_task = Task(
        description="수집된 모든 교통편 정보를 종합 분석하여 예산에 맞는 최적의 교통수단을 추천하라.",
        expected_output="비용 분석 결과와 예산별 추천 교통수단 Top 3 (시간, 비용, 편의성, 예약 방법 포함)",
        agent=cost_analyzer,
        context=[hybrid_search_task],
    )

    # 6. 크루 실행
    hybrid_crew = Crew(
        agents=[route_planner, hybrid_searcher, cost_analyzer],
        tasks=[route_task, hybrid_search_task, cost_task],
        process=Process.sequential,
        verbose=2,
    )

    result = hybrid_crew.kickoff()
    return {'이동수단': str(result)}
