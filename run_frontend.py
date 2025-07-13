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
    
    try:
        print("🚀 Good Travel Agent Frontend 시작...")
        print("📍 웹 주소: http://localhost:8501")
        print("⏹️  서버 종료: Ctrl+C")
        print("-" * 50)
        
        # Streamlit 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_path),
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
        
    except KeyboardInterrupt:
        print("\n✅ 프론트엔드 서버가 종료되었습니다.")
    except FileNotFoundError:
        print("❌ Streamlit이 설치되지 않았습니다.")
        print("💡 다음 명령어로 설치해주세요: pip install streamlit")
    except Exception as e:
        print(f"❌ 프론트엔드 시작 오류: {e}")

if __name__ == '__main__':
    run_streamlit()