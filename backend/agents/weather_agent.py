from crewai import Agent
import os
import requests
from typing import Optional

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

weather_agent = Agent(
    name="WeatherAgent",
    role="여행 날씨 정보 분석 및 준비물 추천 전문가",
    goal="""
    여행 목적지와 기간의 실시간 날씨 데이터를 단계별로 분석하여 다음을 제공:
    1. 날씨 패턴 분석 및 해석
    2. 날씨별 최적 옷차림 조합 추천 
    3. 필수 준비물 및 액세서리 목록 작성
    4. 날씨 기반 여행 주의사항 및 실용적 팁 제공
    5. 실내/실외 활동 비율 최적화 제안
    """,
    backstory="""
    당신은 10년 이상의 기상 분석 경험을 가진 전문 기상 컨설턴트입니다.
    
    **전문 분야:**
    - 기상 데이터 해석 및 패턴 분석
    - 지역별 기후 특성 및 계절별 변화 이해  
    - 여행자 안전을 위한 날씨 기반 위험 평가
    - 활동별 최적 날씨 조건 매칭
    
    **작업 원칙:**
    - 제공된 실시간 날씨 데이터만을 근거로 분석 수행
    - 모든 추천은 구체적인 근거와 함께 제시
    - 여행자의 안전과 편의를 최우선으로 고려
    - 예상치 못한 날씨 변화에 대한 대비책 포함
    """,
    llm_config={
        "provider": "openai",
        "config": {
            "model": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY
        }
    }
)

def get_weather_data(destination: Optional[str], start_date: Optional[str], end_date: Optional[str]) -> str:
    """OpenWeatherMap API를 사용하여 날씨 정보 조회"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "날씨 API 키가 설정되지 않았습니다."
    destination = (destination or "").strip()
    if not destination:
        return "목적지가 없어 날씨 정보를 조회할 수 없습니다."
    
    # 도시 이름을 좌표로 변환
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={destination}&limit=1&appid={api_key}"
    
    try:
        geo_response = requests.get(geocoding_url, timeout=10)
        if geo_response.status_code != 200:
            return "도시 정보를 찾을 수 없습니다."
        
        geo_data = geo_response.json()
        if not geo_data:
            return f"{destination}에 대한 지리 정보를 찾을 수 없습니다."
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
        # 현재 날씨 API 사용 (무료 플랜)
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
        current_response = requests.get(current_url, timeout=10)
        
        # 5일 예보 API 사용 (무료 플랜)
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
        forecast_response = requests.get(forecast_url, timeout=10)
        
        if current_response.status_code != 200 or forecast_response.status_code != 200:
            return f"날씨 정보를 가져올 수 없습니다. Current: {current_response.status_code}, Forecast: {forecast_response.status_code}"
        
        current_data = current_response.json()
        forecast_data = forecast_response.json()
        
        # 현재 날씨
        forecast_summary = f"📍 {destination} 현재 날씨\n"
        forecast_summary += f"기온: {current_data['main']['temp']:.1f}°C (체감: {current_data['main']['feels_like']:.1f}°C)\n"
        forecast_summary += f"습도: {current_data['main']['humidity']}%, 날씨: {current_data['weather'][0]['description']}\n"
        forecast_summary += f"바람: {current_data.get('wind', {}).get('speed', 0):.1f}m/s\n\n"
        
        # 5일 예보 (3시간 간격)
        forecast_summary += "📅 5일 예보 (3시간 간격):\n"
        from datetime import datetime
        for i, forecast in enumerate(forecast_data['list'][:12], 1):  # 첫 12개 (36시간)
            dt = datetime.fromtimestamp(forecast['dt'])
            date_time = dt.strftime('%m/%d %H시')
            temp = forecast['main']['temp']
            description = forecast['weather'][0]['description']
            humidity = forecast['main']['humidity']
            
            forecast_summary += f"{i}. {date_time} - 기온: {temp:.1f}°C, {description}, 습도: {humidity}%\n"
        
        # 일별 요약 (첫 번째 예보에서 최고/최저 추출)
        forecast_summary += "\n📊 일별 날씨 요약:\n"
        daily_data = {}
        for forecast in forecast_data['list'][:40]:  # 5일치
            dt = datetime.fromtimestamp(forecast['dt'])
            date_key = dt.strftime('%m/%d')
            temp = forecast['main']['temp']
            
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'temps': [temp],
                    'descriptions': [forecast['weather'][0]['description']]
                }
            else:
                daily_data[date_key]['temps'].append(temp)
                daily_data[date_key]['descriptions'].append(forecast['weather'][0]['description'])
        
        for i, (date, data) in enumerate(daily_data.items(), 1):
            min_temp = min(data['temps'])
            max_temp = max(data['temps'])
            # 가장 많이 나온 날씨 설명 사용
            main_desc = max(set(data['descriptions']), key=data['descriptions'].count)
            forecast_summary += f"{i}. {date} - 최저: {min_temp:.1f}°C, 최고: {max_temp:.1f}°C, {main_desc}\n"
        
        return forecast_summary
        
    except Exception as e:
        return f"날씨 정보 조회 중 오류 발생: {str(e)}"

# Only export agent object and helper functions for use by the central workflow
# No Crew/Task orchestration here