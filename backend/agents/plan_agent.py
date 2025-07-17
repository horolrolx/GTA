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

# Only export agent object and helper functions for use by the central workflow
# No Crew/Task orchestration here
