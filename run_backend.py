#!/usr/bin/env python3
"""
Good Travel Agent - Backend Server 실행 스크립트
"""

import os
import sys
from pathlib import Path
from langchain_teddynote import logging
from dotenv import load_dotenv

load_dotenv()

logging.langsmith("Travel_Agent")
# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root / "backend"))

try:
    from backend.app import app
    
    if __name__ == '__main__':
        print("🚀 Good Travel Agent Backend Server 시작...")
        print("📍 서버 주소: http://localhost:5555")
        print("📖 API 문서:")
        print("   - GET  /               : API 정보")
        print("   - GET  /health          : 서버 상태 확인")
        print("   - POST /plan            : 통합 여행 계획 생성")
        print("   - POST /weather         : 날씨 정보만 조회")
        print("⏹️  서버 종료: Ctrl+C")
        print("-" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5555)
        
except ImportError as e:
    print(f"❌ 모듈 임포트 오류: {e}")
    print("💡 다음을 확인해주세요:")
    print("   1. requirements.txt의 모든 패키지가 설치되었는지")
    print("   2. .env 파일에 필요한 API 키들이 설정되었는지")
    print("   3. Python 경로가 올바른지")
except Exception as e:
    print(f"❌ 서버 시작 오류: {e}")
    print("💡 로그를 확인하고 문제를 해결해주세요.")