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
    role="여행 숙소 추천 전문가",
    goal="여행 목적지에 맞는 최적의 숙소를 추천한다.",
    backstory="여행 숙소에 대한 다양한 정보를 알고 있으며, 사용자의 여행 목적과 예산에 맞는 숙소를 추천한다.",
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
