import os
from crewai import Agent
from langchain_naver_community.utils import NaverSearchAPIWrapper

# 네이버 API 환경변수는 시스템 또는 .env에서 미리 설정되어야 함
# os.environ["NAVER_CLIENT_ID"] = "여기에_네이버_CLIENT_ID"
# os.environ["NAVER_CLIENT_SECRET"] = "여기에_네이버_CLIENT_SECRET"

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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
