import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_naver_community.utils import NaverSearchAPIWrapper
from langchain_openai import ChatOpenAI
import sys
sys.path.append('/Users/songchangseok/Desktop/GTA/backend')
from utils.crew_logger import crew_logger, log_function_execution, log_crew_workflow

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if SERPER_API_KEY:
    os.environ["SERPER_API_KEY"] = SERPER_API_KEY

search_tool = SerperDevTool()
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)

food_agent = Agent(
    role="여행 맛집 추천 전문가",
    goal="여행 목적지의 대표 맛집을 추천한다.",
    backstory="여행지의 다양한 맛집 정보를 알고 있으며, 사용자의 취향에 맞는 맛집을 추천한다.",
    llm=llm,
    verbose=True
)

planner = Agent(
    role="맛집 탐색 기획 전문가",
    goal="사용자의 모호한 맛집 요청을 분석하여 구체적인 검색 키워드와 실행 계획으로 변환",
    backstory="당신은 고객의 숨은 니즈까지 파악하는 베테랑 기획자로, "
              "어떤 요청이든 명확한 분석을 통해 실행 가능한 계획을 수립합니다.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

searcher = Agent(
    role="정보 검색의 달인",
    goal="수립된 계획에 따라 웹에서 가장 정확하고 연관성 높은 맛집 후보 리스트를 수집",
    backstory="당신은 최신 정보를 가장 빠르게 찾아내는 디지털 탐정입니다. "
              "광고와 실제 정보를 구분하는 날카로운 눈을 가지고 있습니다.",
    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

analyst = Agent(
    role="데이터 기반 맛집 비평가",
    goal="수집된 맛집 후보들의 리뷰, 평점 등을 심층 분석하여 최종 추천 리스트와 근거를 제시",
    backstory="당신은 수많은 리뷰 속에서 진짜 정보를 꿰뚫어 보는 데이터 분석가입니다. "
              "객관적인 데이터에 기반하여 최적의 맛집을 가려냅니다.",
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

@log_function_execution("기본_맛집_계획_생성")
def get_food_plan(data):
    real_time_food = get_real_time_food_data(data.get('destination', ''))
    destination = data.get('destination', '')
    
    prompt = f"""
목적지: {destination}
여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
인원수: {data.get('people', '')}
여행 목적/특이사항: {data.get('purpose', '')}

아래 조건을 모두 반영해서 현실적으로 추천해줘.
- 네이버 실시간 검색 결과(아래 참고)를 반영해서 추천
- 여행 일정과 동선을 고려해 방문하기 좋은 맛집 추천(아침, 점심, 저녁 구분)
- 지역별 대표 음식, 현지 인기 맛집, 숨은 맛집 등 다양하게 제안
- 가격대, 위치, 대표 메뉴, 예약 필요 여부, 현지인/관광객 평점 등도 안내
- 표 형태로 정리

**답변 형식 요구사항:**
- 답변은 반드시 표 형태로 정리
- 일관된 구조: 맛집명 | 메뉴 | 가격대 | 위치 | 예약방법 | 추천이유 | 참고링크
- 추천 우선순위 명시 (1순위, 2순위, 3순위)
- 각 맛집별로 예약 가능한 웹사이트나 전화번호 포함
- 참고한 정보 출처 URL 반드시 포함

[네이버 실시간 검색 결과]
{real_time_food}
"""
    
    crew_logger.logger.info(f"🤖 기본 맛집 에이전트 실행: {destination}")
    
    # CrewAI Task와 Crew를 사용한 올바른 실행 방식
    food_task = Task(
        description=prompt,
        expected_output="맛집 추천 결과 (표 형태로 정리)",
        agent=food_agent,
    )
    
    food_crew = Crew(
        agents=[food_agent],
        tasks=[food_task],
        process=Process.sequential,
        verbose=True,
    )
    
    result = food_crew.kickoff()
    crew_logger.logger.info(f"✅ 기본 맛집 에이전트 완료")
    return {'맛집': str(result)}

@log_crew_workflow("고도화_맛집_크루")
def get_enhanced_food_plan(user_request):
    plan_task = Task(
        description=f"사용자 요청 '{user_request}'을 분석하여, 검색에 사용할 핵심 조건(지역, 메뉴, 분위기, 인원)을 명확히 정리하고, 검색할 키워드 목록을 생성하라.",
        expected_output="검색에 사용할 구체적인 키워드 목록과 검색 조건이 담긴 보고서",
        agent=planner,
    )

    search_task = Task(
        description="""생성된 키워드를 사용하여 웹 검색을 실행하고, 조건에 부합하는 맛집 후보 5곳의 이름, 대표 메뉴, 특징, 리뷰 요약을 수집하라.
        
        **검색 시 반드시 포함해야 할 정보:**
        - 각 맛집별 예약 가능한 웹사이트 URL
        - 맛집 정보가 있는 공식 사이트 링크
        - 예약 및 주문 가능한 사이트 주소
        - 참고한 정보 출처 URL
        """,
        expected_output="각 맛집 후보에 대한 기본 정보(이름, 메뉴, 특징)와 온라인 리뷰 요약, 공식 웹사이트 URL이 포함된 리스트",
        agent=searcher,
        context=[plan_task],
    )

    analysis_task = Task(
        description="""수집된 맛집 리스트를 최종 분석하여, 사용자의 요청에 가장 적합한 Top 3를 선정하고, 각 맛집을 추천하는 이유와 고려할 점을 상세히 정리하여 최종 보고서를 작성하라.
        
        **답변 형식 요구사항:**
        - 답변은 반드시 표 형태로 정리
        - 일관된 구조: 맛집명 | 메뉴 | 가격대 | 위치 | 예약방법 | 추천이유 | 참고링크
        - 추천 우선순위 명시 (1순위, 2순위, 3순위)
        - 각 맛집별로 예약 가능한 웹사이트나 전화번호 포함
        - 참고한 정보 출처 URL 반드시 포함
        """,
        expected_output="최종 추천 맛집 3곳의 이름, 주소, 추천 이유, 대표 메뉴, 가격대, 분위기, 예약 필요 여부, 참고 URL 등 상세 정보가 담긴 완결된 보고서",
        agent=analyst,
        context=[search_task],
    )

    matjip_crew = Crew(
        agents=[planner, searcher, analyst],
        tasks=[plan_task, search_task, analysis_task],
        process=Process.sequential,
        verbose=True,
    )

    crew_logger.logger.info(f"🚀 고도화 맛집 크루 시작: {user_request}")
    result = matjip_crew.kickoff()
    crew_logger.logger.info(f"✅ 고도화 맛집 크루 완료")
    return {'맛집': str(result)}

@log_crew_workflow("하이브리드_맛집_크루")
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
        llm=llm,
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
        
        **검색 시 반드시 포함해야 할 정보:**
        - 각 맛집별 예약 가능한 웹사이트 URL
        - 맛집 정보가 있는 공식 사이트 링크
        - 예약 및 주문 가능한 사이트 주소
        - 참고한 정보 출처 URL
        """,
        expected_output="네이버 검색 결과를 포함한 각 맛집 후보에 대한 기본 정보(이름, 메뉴, 특징)와 온라인 리뷰 요약, 공식 웹사이트 URL이 포함된 리스트",
        agent=enhanced_searcher,
        context=[plan_task],
    )

    analysis_task = Task(
        description="""수집된 맛집 리스트를 최종 분석하여, 사용자의 요청에 가장 적합한 Top 3를 선정하고, 각 맛집을 추천하는 이유와 고려할 점을 상세히 정리하여 최종 보고서를 작성하라.
        
        **답변 형식 요구사항:**
        - 답변은 반드시 표 형태로 정리
        - 일관된 구조: 맛집명 | 메뉴 | 가격대 | 위치 | 예약방법 | 추천이유 | 참고링크
        - 추천 우선순위 명시 (1순위, 2순위, 3순위)
        - 각 맛집별로 예약 가능한 웹사이트나 전화번호 포함
        - 참고한 정보 출처 URL 반드시 포함
        """,
        expected_output="최종 추천 맛집 3곳의 이름, 주소, 추천 이유, 대표 메뉴, 가격대, 분위기, 예약 필요 여부, 참고 URL 등 상세 정보가 담긴 완결된 보고서",
        agent=analyst,
        context=[hybrid_search_task],
    )

    # 5. 크루 실행
    hybrid_crew = Crew(
        agents=[planner, enhanced_searcher, analyst],
        tasks=[plan_task, hybrid_search_task, analysis_task],
        process=Process.sequential,
        verbose=True,
    )

    crew_logger.logger.info(f"🚀 하이브리드 맛집 크루 시작: {destination}")
    result = hybrid_crew.kickoff()
    crew_logger.logger.info(f"✅하이브리드 맛집 크루 완료")
    return {'맛집': str(result)}
