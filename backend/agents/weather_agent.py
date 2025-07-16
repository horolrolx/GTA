from crewai import Agent
import os
import requests

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

weather_agent = Agent(
    name="WeatherAgent",
    role="여행 날씨 정보 제공 전문가",
    goal="여행 목적지와 기간의 날씨 정보를 분석하여 여행 준비물과 옷차림을 추천한다.",
    backstory="기상 정보에 대한 전문 지식을 바탕으로, 여행자가 날씨에 맞는 최적의 준비를 할 수 있도록 도움을 준다.",
    llm_config={
        "provider": "openai",
        "config": {
            "model": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY
        }
    }
)

def get_weather_data(destination, start_date, end_date):
    """OpenWeatherMap API를 사용하여 날씨 정보 조회"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "날씨 API 키가 설정되지 않았습니다."
    
    # 도시 이름을 좌표로 변환
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={destination}&limit=1&appid={api_key}"
    
    try:
        geo_response = requests.get(geocoding_url)
        if geo_response.status_code != 200:
            return "도시 정보를 찾을 수 없습니다."
        
        geo_data = geo_response.json()
        if not geo_data:
            return f"{destination}에 대한 지리 정보를 찾을 수 없습니다."
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
        # 현재 날씨 API 사용 (무료 플랜)
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
        current_response = requests.get(current_url)
        
        # 5일 예보 API 사용 (무료 플랜)
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
        forecast_response = requests.get(forecast_url)
        
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

def get_weather_plan(data):
    """날씨 정보를 바탕으로 여행 준비 사항 추천"""
    weather_info = get_weather_data(
        data.get('destination', ''),
        data.get('start_date', ''),
        data.get('end_date', '')
    )
    
    prompt = f"""
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
    # CrewAI Agent는 Task와 Crew를 통해 실행해야 함
    from crewai import Task, Crew
    
    weather_task = Task(
        name="weather_with_api",
        description=prompt,
        agent=weather_agent,
        expected_output="날씨 정보와 여행 준비 사항이 포함된 상세 분석"
    )
    
    weather_crew = Crew(tasks=[weather_task])
    result = weather_crew.kickoff()
    
    return {'날씨': str(result)}