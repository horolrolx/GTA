import os
from crewai import Agent
from crewai_tools import SerperDevTool
from langchain_naver_community.utils import NaverSearchAPIWrapper
from langchain_openai import ChatOpenAI
from backend.utils.crew_logger import crew_logger, log_function_execution

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if SERPER_API_KEY:
    os.environ["SERPER_API_KEY"] = SERPER_API_KEY

search_tool = SerperDevTool()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)

food_agent = Agent(
    role="여행지 맛집 분석 및 미식 여행 큐레이션 전문가",
    goal="""
    여행 목적지의 음식문화를 체계적으로 분석하여 다음을 제공:
    1. 지역 특색 음식 및 대표 요리 발굴
    2. 가격대별, 분위기별 맛집 카테고리 분류
    3. 현지인 추천 vs 관광객 인기 맛집 구분
    4. 예약 필요성, 운영시간, 접근성 정보 제공
    5. 식이제한 (할랄, 비건, 알레르기) 대응 옵션 조사
    6. 계절별/시간대별 메뉴 특화 정보 수집
    7. 실시간 리뷰 및 평점 동향 분석
    
    **필수 검색 도구 사용**: 모든 맛집 정보는 실시간 검색을 통해 수집하며, 현재 운영상태와 정확한 정보만 제공
    """,
    backstory="""
    당신은 15년 경력의 푸드 크리틱이자 미식 여행 전문가입니다.
    
    **전문 분야:**
    - 지역 음식문화: 향토음식, 지역특산물, 계절별 별미, 전통 조리법
    - 맛집 평가: 맛, 분위기, 서비스, 가성비의 종합적 평가 시스템
    - 트렌드 분석: SNS 인기 맛집, 미디어 소개 맛집, 입소문 맛집 구분
    - 다이닝 문화: 예약 관습, 팁 문화, 드레스코드, 식사 예절
    
    **정보 수집 및 검증 방법:**
    1. 다양한 플랫폼의 실시간 리뷰 크로스체킹
    2. 공식 홈페이지/SNS를 통한 운영정보 확인
    3. 최근 방문 후기를 통한 현재 상태 파악
    4. 예약 가능성 및 대기시간 정보 수집
    
    **추천 기준:**
    - 정통성: 지역 고유의 맛과 조리법 유지도
    - 신선도: 재료의 신선함과 요리 품질
    - 독창성: 특별한 메뉴나 차별화된 요소
    - 접근성: 찾아가기 편한 위치와 교통편
    - 가치: 가격 대비 만족도와 경험의 가치
    
    **세심한 배려:**
    - 연령대별 선호도 고려 (어린이, 어르신 친화적 메뉴)
    - 단체/개인 용도에 따른 적합성 평가
    - 사진 촬영 가능 여부 및 인스타그램 친화도
    - 주차 가능성 및 대중교통 접근성
    """,
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
    try:
        search = NaverSearchAPIWrapper()
        results = search.results(query)
        return results
    except Exception as e:
        crew_logger.log_error("naver_search_error", str(e))
        return []

@log_function_execution("네이버_맛집_검색")
def get_real_time_food_data(destination):
    destination = (destination or '').strip()
    if not destination:
        return "목적지가 없어 맛집 검색을 수행할 수 없습니다."
    query = f"{destination} 맛집 추천"
    results = naver_search(query)
    if not results:
        return "실시간 맛집 데이터를 가져오지 못했습니다."
    summary_lines = []
    for i, item in enumerate(results[:3], 1):
        title = item.get('title', 'N/A')
        desc = item.get('description', '')
        link = item.get('link', '')
        summary_lines.append(f"{i}. {title} - {desc} (링크: {link})")
    return "\n".join(summary_lines)

# Only export agent objects and helper functions for use by the central workflow
# No Crew/Task orchestration here
