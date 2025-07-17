from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.crew_agent import get_travel_plan_with_crew
import logging

app = Flask(__name__)
CORS(app)  # CORS 허용

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def root():
    """API 정보 엔드포인트"""
    return jsonify({
        "name": "Good Travel Agent API",
        "version": "1.0.0",
        "description": "여행 계획 생성을 위한 API 서비스",
        "endpoints": {
            "/health": "서버 상태 확인",
            "/plan": "여행 플랜 생성 (POST)",
            "/weather": "날씨 정보 조회 (POST)"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인 엔드포인트"""
    return jsonify({"status": "healthy", "message": "Good Travel Agent API is running"})

@app.route('/plan', methods=['POST'])
def plan():
    """통합 여행 플랜 생성 엔드포인트"""
    try:
        data = request.json
        
        # 필수 필드 검증
        required_fields = ['destination', 'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400
        
        logger.info(f"여행 플랜 요청: {data.get('destination')} ({data.get('start_date')} ~ {data.get('end_date')})")
        
        # Crew AI 협업 구조로 여행 플랜 생성
        result = get_travel_plan_with_crew(data)
        
        logger.info("여행 플랜 생성 완료")
        return jsonify({
            "success": True,
            "data": result,
            "message": "여행 플랜이 성공적으로 생성되었습니다."
        })
        
    except Exception as e:
        logger.error(f"여행 플랜 생성 중 오류 발생: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "여행 플랜 생성 중 오류가 발생했습니다."
        }), 500

@app.route('/weather', methods=['POST'])
def weather_info():
    """날씨 정보만 조회하는 엔드포인트"""
    try:
        from agents.weather_agent import get_weather_plan
        
        data = request.json
        result = get_weather_plan(data)
        
        return jsonify({
            "success": True,
            "data": result,
            "message": "날씨 정보를 성공적으로 조회했습니다."
        })
        
    except Exception as e:
        logger.error(f"날씨 정보 조회 중 오류 발생: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "날씨 정보 조회 중 오류가 발생했습니다."
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
