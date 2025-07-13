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
        
        # 현재 날씨 및 예보 조회
        weather_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
        weather_response = requests.get(weather_url)
        
        if weather_response.status_code != 200:
            return "날씨 정보를 가져올 수 없습니다."
        
        weather_data = weather_response.json()
        
        # 날씨 정보 요약
        forecast_summary = ""
        for i, forecast in enumerate(weather_data['list'][:10], 1):  # 5일간 예보 (3시간 간격)
            temp = forecast['main']['temp']
            feels_like = forecast['main']['feels_like']
            humidity = forecast['main']['humidity']
            description = forecast['weather'][0]['description']
            date_time = forecast['dt_txt']
            
            forecast_summary += f"{i}. {date_time} - 기온: {temp}°C (체감: {feels_like}°C), 습도: {humidity}%, 날씨: {description}\n"
        
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
    result = weather_agent.run(prompt)
    return {'날씨': str(result)}