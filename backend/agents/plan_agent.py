from crewai import Agent
import os

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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

def get_travel_plan(data):
    prompt = f"""
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
    result = plan_agent.run(prompt)
    return {'일정': result}
