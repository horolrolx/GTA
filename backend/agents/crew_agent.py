from crewai import Agent, Task, Crew
import os
import logging
from datetime import datetime
from .weather_agent import weather_agent, get_weather_plan

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 로깅 설정
def setup_crew_logging():
    """CrewAI 에이전트간 LLM 응답 로깅 설정"""
    logger = logging.getLogger('crewai_llm_responses')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # 파일 핸들러 추가
        file_handler = logging.FileHandler('crew_llm_responses.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# 로거 초기화
crew_logger = setup_crew_logging()

def log_agent_interaction(agent_name, task_name, prompt, response, execution_time=None):
    """에이전트 상호작용 로깅"""
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
    crew_logger.info(f"🚀 여행 계획 생성 시작 - 목적지: {data.get('destination', '')}")
    
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

    # 각 에이전트 실행 및 로깅
    import time
    
    # 날씨 에이전트 실행 (실제 날씨 API 사용)
    start_time = time.time()
    crew_logger.info(f"🌤️  WeatherAgent 작업 시작 (실제 날씨 API 호출)")
    weather_result = get_weather_plan(data)  # 실제 날씨 API 사용
    weather_time = time.time() - start_time
    log_agent_interaction(
        agent_name="WeatherAgent",
        task_name="weather_analysis_with_api",
        prompt=f"목적지: {data.get('destination', '')}, 여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}, OpenWeatherMap API 호출",
        response=str(weather_result),
        execution_time=weather_time
    )
    
    # 교통 에이전트 실행
    start_time = time.time()
    crew_logger.info(f"🚗 TransportAgent 작업 시작")
    transport_result = transport_crew.kickoff()
    transport_time = time.time() - start_time
    log_agent_interaction(
        agent_name="TransportAgent", 
        task_name="transport_recommendation",
        prompt=transport_task.description,
        response=str(transport_result),
        execution_time=transport_time
    )
    
    # 숙소 에이전트 실행
    start_time = time.time()
    crew_logger.info(f"🏨 HotelAgent 작업 시작")
    hotel_result = hotel_crew.kickoff()
    hotel_time = time.time() - start_time
    log_agent_interaction(
        agent_name="HotelAgent",
        task_name="hotel_recommendation", 
        prompt=hotel_task.description,
        response=str(hotel_result),
        execution_time=hotel_time
    )
    
    # 일정 에이전트 실행
    start_time = time.time()
    crew_logger.info(f"📅 PlanAgent 작업 시작")
    plan_result = plan_crew.kickoff()
    plan_time = time.time() - start_time
    log_agent_interaction(
        agent_name="PlanAgent",
        task_name="itinerary_planning",
        prompt=plan_task.description,
        response=str(plan_result),
        execution_time=plan_time
    )
    
    # 맛집 에이전트 실행
    start_time = time.time() 
    crew_logger.info(f"🍽️  FoodAgent 작업 시작")
    food_result = food_crew.kickoff()
    food_time = time.time() - start_time
    log_agent_interaction(
        agent_name="FoodAgent",
        task_name="restaurant_recommendation",
        prompt=food_task.description,
        response=str(food_result),
        execution_time=food_time
    )
    
    # 전체 실행 완료 로깅
    total_time = weather_time + transport_time + hotel_time + plan_time + food_time
    crew_logger.info(f"✅ 모든 에이전트 작업 완료 - 총 소요시간: {total_time:.2f}초")

    return {
        'weather': str(weather_result.get('날씨', weather_result)),
        'transport': str(transport_result),
        'hotel': str(hotel_result),
        'plan': str(plan_result),
        'food': str(food_result)
    }
