from flask import Flask, request, jsonify
from agents.crew_agent import get_travel_plan_with_crew

app = Flask(__name__)

@app.route('/plan', methods=['POST'])
def plan():
    data = request.json
    # Crew AI 협업 구조로 여행 플랜 생성
    result = get_travel_plan_with_crew(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
