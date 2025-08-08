#!/usr/bin/env python3
"""
Good Travel Agent - Frontend 실행 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def run_streamlit():
    """Streamlit 프론트엔드 실행"""
    frontend_path = Path(__file__).parent / "frontend" / "app.py"
    
    # 로컬 실행을 위한 환경 변수 설정
    server_address = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
    server_port = os.getenv("STREAMLIT_SERVER_PORT", "8501")
    backend_url = os.getenv("BACKEND_URL", "http://localhost:5555")
    
    # 환경 변수 설정
    env = os.environ.copy()
    env["STREAMLIT_SERVER_ADDRESS"] = server_address
    env["STREAMLIT_SERVER_PORT"] = server_port
    env["BACKEND_URL"] = backend_url
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    try:
        print("🚀 Good Travel Agent Frontend 시작...")
        print(f"📍 웹 주소: http://{server_address}:{server_port}")
        print(f"🔗 백엔드 URL: {backend_url}")
        print("⏹️  서버 종료: Ctrl+C")
        print("-" * 50)
        
        # Streamlit 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_path),
            "--server.port", server_port,
            "--server.address", server_address,
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ], env=env)
        
    except KeyboardInterrupt:
        print("\n✅ 프론트엔드 서버가 종료되었습니다.")
    except FileNotFoundError:
        print("❌ Streamlit이 설치되지 않았습니다.")
        print("💡 다음 명령어로 설치해주세요: pip install streamlit")
    except Exception as e:
        print(f"❌ 프론트엔드 시작 오류: {e}")

if __name__ == '__main__':
    run_streamlit()