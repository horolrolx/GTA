from crewai import Agent
import os
import airbnb

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

hotel_agent = Agent(
    name="HotelAgent",
    role="여행 숙소 추천 전문가",
    goal="여행 목적지에 맞는 최적의 숙소를 추천한다.",
    backstory="여행 숙소에 대한 다양한 정보를 알고 있으며, 사용자의 여행 목적과 예산에 맞는 숙소를 추천한다.",
    llm_config={
        "provider": "openai",
        "config": {
            "model": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY
        }
    }
)

def get_airbnb_listings(city, checkin=None, checkout=None):
    api = airbnb.Api()
    params = {}
    if checkin and checkout:
        params['checkin'] = checkin
        params['checkout'] = checkout
    results = api.get_homes(city, **params)
    summary = ""
    for i, item in enumerate(results['results'][:3], 1):
        summary += (
            f"{i}. {item.get('name', '이름없음')} - "
            f"가격: {item.get('price', {}).get('rate_with_service_fee', 'N/A')} {item.get('price', {}).get('currency', '')}, "
            f"위치: {item.get('city', '')}, "
            f"링크: https://airbnb.com/rooms/{item.get('id', '')}\n"
        )
    return summary

def get_hotel_plan(data):
    airbnb_data = get_airbnb_listings(
        data.get('destination', ''),
        checkin=data.get('start_date', None),
        checkout=data.get('end_date', None)
    )
    prompt = f"""
목적지: {data.get('destination', '')}
여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
인원수: {data.get('people', '')}
예산: {data.get('budget', '')}만원
여행 목적/특이사항: {data.get('purpose', '')}

아래 조건을 모두 반영해서 현실적으로 추천해줘.
- Airbnb 실시간 숙소 검색 결과(아래 참고)를 반영해서 추천
- 여행 목적(휴양, 관광, 액티비티, 가족, 커플 등)에 맞는 숙소 유형(호텔, 리조트, 게스트하우스, 에어비앤비 등) 추천
- 위치(중심가, 관광지 근처, 교통편리 등), 가격대, 편의시설(수영장, 조식, 주차 등)도 함께 안내
- 예산과 인원수에 맞는 객실 타입(싱글, 더블, 패밀리룸 등) 추천
- 추천 숙소별로 표 형태로 정리

[Airbnb 실시간 숙소 검색 결과]
{airbnb_data}
"""
    result = hotel_agent.run(prompt)
    return {'숙소': str(result)}
