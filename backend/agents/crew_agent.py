from crewai import Task, Crew
import logging
from datetime import datetime
from .weather_agent import weather_agent, get_weather_data
from .transport_agent import transport_agent, route_planner, transport_searcher, cost_analyzer, get_web_transport_search, get_real_time_transport_search
from .hotel_agent import hotel_agent, get_hotel_recommendations
from .plan_agent import plan_agent
from .food_agent import food_agent, planner, searcher, analyst, get_real_time_food_data

# 로깅 설정

def setup_crew_logging():
    logger = logging.getLogger('crewai_llm_responses')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler('crew_llm_responses.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger

crew_logger = setup_crew_logging()

def log_agent_interaction(agent_name, task_name, prompt, response, execution_time=None):
    log_message = f"""
{'='*80}
🤖 AGENT: {agent_name}
📋 TASK: {task_name}
⏰ TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{f'⚡ EXECUTION_TIME: {execution_time:.2f}초' if execution_time else ''}

📤 PROMPT:
{prompt}

📥 RESPONSE:
{response}
{'='*80}
"""
    crew_logger.info(log_message)

def get_travel_plan_with_crew(data):
    crew_logger.info(f"🚀 여행 계획 생성 시작 - 목적지: {data.get('destination', '')}")
    import time
    results = {}

    # 1. 날씨 정보
    start_time = time.time()
    weather_info = get_weather_data(
        data.get('destination', ''),
        data.get('start_date', ''),
        data.get('end_date', '')
    )
    weather_prompt = f"""
목적지: {data.get('destination', '')}
여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
인원수: {data.get('people', '')}
여행 목적/특이사항: {data.get('purpose', '')}

아래 조건을 모두 반영해서 현실적으로 추천해줘.
- 실시간 날씨 예보(아래 참고)를 바탕으로 여행 기간 동안의 날씨 분석
- 날씨에 맞는 옷차림 추천 (상의, 하의, 아우터, 신발, 악세서리 등)
- 필수 준비물 (우산, 선크림, 모자, 선글라스, 보온용품 등)
- 날씨로 인한 여행 시 주의사항 및 팁
- 실내/실외 활동 비율 조정 제안
- 표 형태로 정리 (날짜별 날씨, 추천 옷차림, 준비물)

[실시간 날씨 예보]
{weather_info}
"""
    weather_task = Task(
        name="weather",
        description=weather_prompt,
        agent=weather_agent,
        expected_output="날짜별 날씨 예보, 추천 옷차림, 필수 준비물이 표로 정리된 결과"
    )
    weather_crew = Crew(tasks=[weather_task])
    weather_result = weather_crew.kickoff()
    weather_time = time.time() - start_time
    log_agent_interaction("WeatherAgent", "weather_analysis", weather_prompt, str(weather_result), weather_time)
    results['weather'] = str(weather_result)

    # 2. 교통 정보
    start_time = time.time()
    transport_prompt = f"""
출발지: {data.get('departure', '')}
목적지: {data.get('destination', '')}
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
- 각 교통수단별로 예약 가능한 웹사이트 URL 포함
- 참고한 정보 출처 URL 반드시 포함 (검색 도구로 찾은 실제 URL)
"""
    transport_task = Task(
        name="transport",
        description=transport_prompt,
        agent=transport_agent,
        expected_output="추천 교통수단, 예상 소요 시간, 비용, 장단점이 표로 정리된 결과"
    )
    transport_crew = Crew(tasks=[transport_task])
    transport_result = transport_crew.kickoff()
    transport_time = time.time() - start_time
    log_agent_interaction("TransportAgent", "transport_recommendation", transport_prompt, str(transport_result), transport_time)
    results['transport'] = str(transport_result)

    # 3. 숙소 정보
    start_time = time.time()
    hotel_data = get_hotel_recommendations(
        data.get('destination', ''),
        checkin=data.get('start_date', None),
        checkout=data.get('end_date', None),
        people=data.get('people', None),
        budget=data.get('budget', None),
        purpose=data.get('purpose', None)
    )
    hotel_prompt = f"""
목적지: {data.get('destination', '')}
여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
인원수: {data.get('people', '')}
예산: {data.get('budget', '')}만원
여행 목적/특이사항: {data.get('purpose', '')}

아래 조건을 모두 반영해서 현실적으로 추천해줘.
- 실시간 숙소 검색 결과(아래 참고)를 반영해서 추천
- 여행 목적(휴양, 관광, 액티비티, 가족, 커플 등)에 맞는 숙소 유형(호텔, 리조트, 게스트하우스, 에어비앤비 등) 추천
- 위치(중심가, 관광지 근처, 교통편리 등), 가격대, 편의시설(수영장, 조식, 주차 등)도 함께 안내
- 예산과 인원수에 맞는 객실 타입(싱글, 더블, 패밀리룸 등) 추천
- 추천 숙소별로 표 형태로 정리

[검색엔진 기반 실시간 숙소 검색 결과]
{hotel_data}
"""
    hotel_task = Task(
        name="hotel",
        description=hotel_prompt,
        agent=hotel_agent,
        expected_output="추천 숙소 리스트, 위치, 가격대, 편의시설, 객실 타입이 표로 정리된 결과"
    )
    hotel_crew = Crew(tasks=[hotel_task])
    hotel_result = hotel_crew.kickoff()
    hotel_time = time.time() - start_time
    log_agent_interaction("HotelAgent", "hotel_recommendation", hotel_prompt, str(hotel_result), hotel_time)
    results['hotel'] = str(hotel_result)

    # 4. 일정 정보
    start_time = time.time()
    plan_prompt = f"""
목적지: {data.get('destination', '')}
여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
인원수: {data.get('people', '')}
여행 목적/특이사항: {data.get('purpose', '')}

아래 조건을 모두 반영해서 현실적으로 추천해줘.
- 여행 기간에 맞춰 1일 단위로 아침, 점심, 저녁, 야간 일정까지 구체적으로 제안
- 주요 관광지, 체험, 휴식, 쇼핑, 액티비티 등 다양한 일정 포함
- 이동 동선이 효율적이도록(동선 낭비 최소화)
- 각 일정별 예상 소요 시간, 추천 이유, 참고 팁(예: 입장권, 예약 필요 등)도 안내
- 표 형태로 정리
"""
    plan_task = Task(
        name="plan",
        description=plan_prompt,
        agent=plan_agent,
        expected_output="1일 단위 여행 일정, 각 일정별 소요 시간, 추천 이유, 참고 팁이 표로 정리된 결과"
    )
    plan_crew = Crew(tasks=[plan_task])
    plan_result = plan_crew.kickoff()
    plan_time = time.time() - start_time
    log_agent_interaction("PlanAgent", "itinerary_planning", plan_prompt, str(plan_result), plan_time)
    results['plan'] = str(plan_result)

    # 5. 맛집 정보
    start_time = time.time()
    real_time_food = get_real_time_food_data(data.get('destination', ''))
    food_prompt = f"""
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
- 각 맛집별로 예약 가능한 웹사이트나 전화번호 포함
- 참고한 정보 출처 URL 반드시 포함 (검색 도구로 찾은 실제 URL)

[네이버 실시간 검색 결과]
{real_time_food}
"""
    food_task = Task(
        name="food",
        description=food_prompt,
        agent=food_agent,
        expected_output="아침/점심/저녁별 추천 맛집, 위치, 가격대, 대표 메뉴, 평점이 표로 정리된 결과"
    )
    food_crew = Crew(tasks=[food_task])
    food_result = food_crew.kickoff()
    food_time = time.time() - start_time
    log_agent_interaction("FoodAgent", "restaurant_recommendation", food_prompt, str(food_result), food_time)
    results['food'] = str(food_result)

    total_time = weather_time + transport_time + hotel_time + plan_time + food_time
    crew_logger.info(f"✅ 모든 에이전트 작업 완료 - 총 소요시간: {total_time:.2f}초")
    return results
