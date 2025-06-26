from crewai import Agent
import os
import requests

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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

def get_area_code(destination):
    # 실제 서비스에서는 더 많은 지역/도시를 매핑해야 함
    area_codes = {
        '서울': '1', '부산': '6', '대구': '4', '인천': '2', '광주': '5', '대전': '3', '울산': '7',
        '세종': '8', '경기': '31', '강원': '32', '충북': '33', '충남': '34', '전북': '35',
        '전남': '36', '경북': '37', '경남': '38', '제주': '39'
    }
    return area_codes.get(destination, '1')  # 기본값: 서울

def get_visitkorea_transport(destination):
    service_key = os.getenv("VISITKOREA_API_KEY")
    area_code = get_area_code(destination)
    url = f"http://apis.data.go.kr/B551011/TransportService1/areaBasedList?serviceKey={service_key}&numOfRows=5&pageNo=1&MobileOS=ETC&MobileApp=AppTest&areaCode={area_code}&_type=json"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
        summary = ""
        for i, item in enumerate(items, 1):
            summary += f"{i}. {item.get('title', '')} - {item.get('addr1', '')} ({item.get('tel', '')})\n"
        return summary if summary else "실시간 교통 정보가 없습니다."
    else:
        return "교통 정보 API 호출 실패"

def get_transport_plan(data):
    real_time_transport = get_visitkorea_transport(data.get('destination', ''))
    prompt = f"""
출발지: {data.get('departure', '')}
목적지: {data.get('destination', '')}
여행 기간: {data.get('start_date', '')} ~ {data.get('end_date', '')}
인원수: {data.get('people', '')}
예산: {data.get('budget', '')}만원
여행 목적/특이사항: {data.get('purpose', '')}

아래 조건을 모두 반영해서 현실적으로 추천해줘.
- Visit Korea 실시간 교통 정보(아래 참고)를 반영해서 추천
- 출발지에서 목적지까지 이동 가능한 실제 교통수단(항공, 기차, 버스, 배 등)을 구체적으로 제시
- 예상 소요 시간, 대략적인 비용, 장단점(예: 빠름/저렴함/경유 필요 등)도 함께 안내
- 예산과 인원수, 여행 목적(예: 가족, 커플, 액티비티 등)에 따라 추천 우선순위가 달라지도록
- 추천 교통수단별로 표 형태로 정리

[Visit Korea 실시간 교통 정보]
{real_time_transport}
"""
    result = transport_agent.run(prompt)
    return {'이동수단': str(result)}
