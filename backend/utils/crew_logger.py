import logging
import time
import json
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional
import inspect

class CrewWorkflowLogger:
    """CrewAI workflow 실시간 디버깅 및 로깅 시스템"""
    
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger('crewai_workflow')
        self.logger.setLevel(log_level)
        
        # 중복 핸들러 방지
        if not self.logger.handlers:
            # 파일 핸들러
            file_handler = logging.FileHandler('crewai_workflow.log', encoding='utf-8')
            file_handler.setLevel(log_level)
            
            # 콘솔 핸들러
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 포맷터
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_tool_execution(self, tool_name: str, input_data: Any, output_data: Any, execution_time: float):
        """툴 실행 로깅"""
        log_data = {
            'type': 'tool_execution',
            'tool_name': tool_name,
            'input': str(input_data)[:500] if input_data else None,
            'output': str(output_data)[:500] if output_data else None,
            'execution_time': f"{execution_time:.3f}초",
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"🔧 TOOL: {tool_name}")
        self.logger.info(f"   ⏱️  실행시간: {execution_time:.3f}초")
        self.logger.info(f"   📥 입력: {str(input_data)[:100]}...")
        self.logger.info(f"   📤 출력: {str(output_data)[:100]}...")
        
    def log_agent_task(self, agent_name: str, task_name: str, task_description: str, 
                      result: Any, execution_time: float):
        """에이전트 태스크 실행 로깅"""
        log_data = {
            'type': 'agent_task',
            'agent_name': agent_name,
            'task_name': task_name,
            'task_description': task_description[:200],
            'result': str(result)[:500] if result else None,
            'execution_time': f"{execution_time:.3f}초",
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"🤖 AGENT: {agent_name}")
        self.logger.info(f"   📋 TASK: {task_name}")
        self.logger.info(f"   ⏱️  실행시간: {execution_time:.3f}초")
        self.logger.info(f"   📝 설명: {task_description[:100]}...")
        self.logger.info(f"   ✅ 결과: {str(result)[:100]}...")
    
    def log_crew_execution(self, crew_name: str, agents: list, tasks: list, 
                          result: Any, total_time: float):
        """크루 전체 실행 로깅"""
        self.logger.info(f"🚀 CREW: {crew_name}")
        self.logger.info(f"   👥 에이전트: {len(agents)}개")
        self.logger.info(f"   📋 태스크: {len(tasks)}개")
        self.logger.info(f"   ⏱️  총 실행시간: {total_time:.3f}초")
        self.logger.info(f"   ✅ 최종 결과: {str(result)[:100]}...")
    
    def log_search_activity(self, search_type: str, query: str, results: Any, 
                           execution_time: float):
        """검색 활동 로깅"""
        self.logger.info(f"🔍 SEARCH: {search_type}")
        self.logger.info(f"   🔎 쿼리: {query}")
        self.logger.info(f"   ⏱️  실행시간: {execution_time:.3f}초")
        self.logger.info(f"   📊 결과: {str(results)[:100]}...")
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """에러 로깅"""
        self.logger.error(f"❌ ERROR: {error_type}")
        self.logger.error(f"   💬 메시지: {error_message}")
        if context:
            self.logger.error(f"   📍 컨텍스트: {context}")

# 전역 로거 인스턴스
crew_logger = CrewWorkflowLogger()

def log_tool_execution(tool_name: str):
    """툴 실행 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                crew_logger.logger.info(f"🔧 {tool_name} 시작...")
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                crew_logger.log_tool_execution(tool_name, args, result, execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                crew_logger.log_error(f"{tool_name}_error", str(e), {
                    'args': str(args),
                    'kwargs': str(kwargs),
                    'execution_time': execution_time
                })
                raise
        return wrapper
    return decorator

def log_function_execution(func_name: str):
    """함수 실행 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                crew_logger.logger.info(f"⚙️ {func_name} 실행 시작...")
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                crew_logger.logger.info(f"✅ {func_name} 완료 - {execution_time:.3f}초")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                crew_logger.log_error(f"{func_name}_error", str(e), {
                    'execution_time': execution_time
                })
                raise
        return wrapper
    return decorator

def log_crew_workflow(crew_name: str):
    """크루 워크플로우 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                crew_logger.logger.info(f"🚀 {crew_name} 크루 워크플로우 시작...")
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                crew_logger.logger.info(f"🎉 {crew_name} 크루 워크플로우 완료 - {execution_time:.3f}초")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                crew_logger.log_error(f"{crew_name}_workflow_error", str(e), {
                    'execution_time': execution_time
                })
                raise
        return wrapper
    return decorator