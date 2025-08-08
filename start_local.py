#!/usr/bin/env python3
"""
Good Travel Agent - 로컬 실행 스크립트
Docker 없이 Python으로 직접 실행
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def run_backend():
    """백엔드 서버 실행"""
    try:
        print("🔧 백엔드 서버 시작 중...")
        subprocess.run([sys.executable, "run_backend.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 백엔드 서버 오류: {e}")
    except KeyboardInterrupt:
        print("✅ 백엔드 서버 종료")

def run_frontend():
    """프론트엔드 서버 실행"""
    try:
        print("🎨 프론트엔드 서버 시작 중...")
        subprocess.run([sys.executable, "run_frontend.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 프론트엔드 서버 오류: {e}")
    except KeyboardInterrupt:
        print("✅ 프론트엔드 서버 종료")

def main():
    """메인 실행 함수"""
    print("🚀 Good Travel Agent - 로컬 실행")
    print("=" * 50)
    
    # 환경변수 설정
    os.environ.setdefault('HOST', 'localhost')
    os.environ.setdefault('PORT', '5555')
    os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', 'localhost')
    os.environ.setdefault('STREAMLIT_SERVER_PORT', '8501')
    os.environ.setdefault('BACKEND_URL', 'http://localhost:5555')
    
    print("📍 접속 주소:")
    print("   - 프론트엔드: http://localhost:8501")
    print("   - 백엔드 API: http://localhost:5555")
    print("⏹️  종료: Ctrl+C")
    print("-" * 50)
    
    # 백엔드와 프론트엔드를 별도 스레드에서 실행
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    
    try:
        # 백엔드 먼저 시작
        backend_thread.start()
        time.sleep(3)  # 백엔드 시작 대기
        
        # 프론트엔드 시작
        frontend_thread.start()
        
        # 메인 스레드 대기
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 서버 종료 중...")
        print("✅ 모든 서버가 종료되었습니다.")

if __name__ == '__main__':
    main()
