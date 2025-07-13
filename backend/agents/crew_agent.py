from crewai import Agent, Task, Crew
import os
from .weather_agent import weather_agent

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 각 에이전트 정의
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
plan_agent = Agent(
    name="PlanAgent",
    role="여행 일정 플래너",
    goal="여행 목적지와 기간에 맞는 일정을 계획한다.",
    backstory="여행 일정에 대한 풍부한 경험을 바탕으로, 사용자의 취향에 맞는 여행 일정을 제안한다.",
    llm_config={
        "provider": "openai",
        "config": {
            "model": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY
        }
    }
)
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

def get_travel_plan_with_crew(data):
    # 1. 날씨 정보 분석 (최우선)
    weather_task = Task(
        name="weather",
        description=f"목적지: {data.get('destination', '')}, 여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}, 인원수: {data.get('people', '')}, 여행 목적/특이사항: {data.get('purpose', '')}\n여행 기간 동안의 날씨를 분석하고 옷차림 및 준비물을 추천해줘.",
        agent=weather_agent,
        expected_output="날짜별 날씨 예보, 추천 옷차림, 필수 준비물이 표로 정리된 결과"
    )
    
    # 2. 이동수단 추천
    transport_task = Task(
        name="transport",
        description=f"출발지: {data.get('departure', '')}, 목적지: {data.get('destination', '')}, 예산: {data.get('budget', '')}만원, 인원수: {data.get('people', '')}, 여행 목적/특이사항: {data.get('purpose', '')}\n이 정보를 바탕으로 추천 이동수단(항공, 기차, 버스 등)을 간단히 안내해줘.",
        agent=transport_agent,
        expected_output="추천 교통수단, 예상 소요 시간, 비용, 장단점이 표로 정리된 결과"
    )
    # 3. 숙소 추천 (날씨, 이동수단 결과 참고)
    hotel_task = Task(
        name="hotel",
        description=f"목적지: {data.get('destination', '')}, 예산: {data.get('budget', '')}만원, 인원수: {data.get('people', '')}, 여행 목적/특이사항: {data.get('purpose', '')}\n날씨 정보와 이동수단 정보도 참고해서 추천 숙소 2~3곳을 안내해줘.",
        agent=hotel_agent,
        expected_output="추천 숙소 리스트, 위치, 가격대, 편의시설, 객실 타입이 표로 정리된 결과",
        depends_on=[weather_task, transport_task]
    )
    # 4. 일정 생성 (날씨, 숙소, 이동수단 결과 참고)
    plan_task = Task(
        name="plan",
        description=f"목적지: {data.get('destination', '')}, 여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}, 인원수: {data.get('people', '')}, 여행 목적/특이사항: {data.get('purpose', '')}\n날씨, 이동수단, 숙소 정보를 참고해서 1일 단위로 여행 일정을 안내해줘.",
        agent=plan_agent,
        expected_output="1일 단위 여행 일정, 각 일정별 소요 시간, 추천 이유, 참고 팁이 표로 정리된 결과",
        depends_on=[weather_task, hotel_task, transport_task]
    )
    # 5. 맛집 추천 (일정 결과 참고)
    food_task = Task(
        name="food",
        description=f"목적지: {data.get('destination', '')}, 여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}, 인원수: {data.get('people', '')}, 여행 목적/특이사항: {data.get('purpose', '')}\n여행 일정 정보를 참고해서 추천 맛집 2~3곳을 안내해줘.",
        agent=food_agent,
        expected_output="아침/점심/저녁별 추천 맛집, 위치, 가격대, 대표 메뉴, 평점이 표로 정리된 결과",
        depends_on=[plan_task]
    )
    # Crew 생성 및 실행
    # 각 Task를 별도의 Crew로 실행하여 결과를 모두 반환
    weather_crew = Crew(tasks=[weather_task])
    transport_crew = Crew(tasks=[transport_task])
    hotel_crew = Crew(tasks=[hotel_task])
    plan_crew = Crew(tasks=[plan_task])
    food_crew = Crew(tasks=[food_task])

    weather_result = weather_crew.kickoff()
    transport_result = transport_crew.kickoff()
    hotel_result = hotel_crew.kickoff()
    plan_result = plan_crew.kickoff()
    food_result = food_crew.kickoff()

    return {
        'weather': str(weather_result),
        'transport': str(transport_result),
        'hotel': str(hotel_result),
        'plan': str(plan_result),
        'food': str(food_result)
    }
