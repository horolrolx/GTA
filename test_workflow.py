#!/usr/bin/env python3
"""
CrewAI Workflow 테스트 스크립트
conda activate gta 환경에서 실행
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append('/Users/songchangseok/Desktop/GTA/backend')

from agents.transport_agent import get_transport_plan, get_enhanced_transport_plan, get_hybrid_transport_plan
from agents.food_agent import get_food_plan, get_enhanced_food_plan, get_hybrid_food_plan
from utils.crew_logger import crew_logger

def test_transport_workflow():
    """교통편 워크플로우 테스트"""
    
    # 테스트 데이터
    test_data = {
        'departure': '서울',
        'destination': '부산',
        'start_date': '2024-01-15',
        'end_date': '2024-01-17',
        'people': '2',
        'budget': '50',
        'purpose': '가족 여행'
    }
    
    print("="*80)
    print("🧪 CrewAI Workflow 테스트 시작")
    print("="*80)
    
    try:
        # 1. 기본 교통편 계획 테스트
        print("\n1️⃣ 기본 교통편 계획 테스트")
        result1 = get_transport_plan(test_data)
        print(f"✅ 기본 교통편 계획 완료: {len(str(result1))} 문자")
        
        # 2. 고도화 교통편 계획 테스트
        print("\n2️⃣ 고도화 교통편 계획 테스트")
        user_request = f"{test_data['departure']}에서 {test_data['destination']}까지 {test_data['people']}명이 {test_data['budget']}만원 예산으로 여행"
        result2 = get_enhanced_transport_plan(user_request)
        print(f"✅ 고도화 교통편 계획 완료: {len(str(result2))} 문자")
        
        # 3. 하이브리드 교통편 계획 테스트
        print("\n3️⃣ 하이브리드 교통편 계획 테스트")
        result3 = get_hybrid_transport_plan(test_data)
        print(f"✅ 하이브리드 교통편 계획 완료: {len(str(result3))} 문자")
        
        # 4-6. 맛집 추천 테스트
        print("\n4️⃣ 기본 맛집 추천 테스트")
        result4 = get_food_plan(test_data)
        print(f"✅ 기본 맛집 추천 완료: {len(str(result4))} 문자")
        
        print("\n5️⃣ 고도화 맛집 추천 테스트")
        food_user_request = f"{test_data['destination']}에서 {test_data['people']}명이 먹을 수 있는 맛집 추천"
        result5 = get_enhanced_food_plan(food_user_request)
        print(f"✅ 고도화 맛집 추천 완료: {len(str(result5))} 문자")
        
        print("\n6️⃣ 하이브리드 맛집 추천 테스트")
        result6 = get_hybrid_food_plan(test_data)
        print(f"✅ 하이브리드 맛집 추천 완료: {len(str(result6))} 문자")
        
        print("\n" + "="*80)
        print("🎉 모든 워크플로우 테스트 완료!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ 워크플로우 테스트 실패: {e}")
        crew_logger.log_error("workflow_test_error", str(e))
        return False

def test_logger_functionality():
    """로거 기능 테스트"""
    print("\n📋 로거 기능 테스트")
    
    try:
        # 로거 테스트
        crew_logger.logger.info("🧪 테스트 로그 메시지")
        crew_logger.log_tool_execution("test_tool", "test_input", "test_output", 1.23)
        crew_logger.log_search_activity("test_search", "test query", "test results", 0.56)
        
        print("✅ 로거 기능 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 로거 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 gta 환경에서 CrewAI 워크플로우 테스트 시작")
    
    # 로거 기능 테스트
    logger_ok = test_logger_functionality()
    
    # 워크플로우 테스트
    workflow_ok = test_transport_workflow()
    
    # 결과 출력
    print("\n📊 테스트 결과:")
    print(f"   로거 기능: {'✅ 성공' if logger_ok else '❌ 실패'}")
    print(f"   워크플로우: {'✅ 성공' if workflow_ok else '❌ 실패'}")
    
    if logger_ok and workflow_ok:
        print("\n🎉 모든 테스트 성공!")
        print("📁 로그 파일 확인: crewai_workflow.log")
    else:
        print("\n⚠️ 일부 테스트 실패")
        sys.exit(1)