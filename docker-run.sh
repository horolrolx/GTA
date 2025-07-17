#!/bin/bash

# Good Travel Agent Docker 실행 스크립트

echo "🐳 Good Travel Agent Docker 환경 구축 및 실행"
echo "================================================"

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다."
    echo "💡 .env.example을 참고하여 .env 파일을 생성해주세요:"
    echo "   cp .env.example .env"
    echo "   # .env 파일을 편집하여 API 키들을 입력하세요"
    exit 1
fi

echo "✅ .env 파일 확인됨"

# Docker와 Docker Compose 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    echo "💡 https://docs.docker.com/get-docker/ 에서 Docker를 설치해주세요."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다."
    echo "💡 https://docs.docker.com/compose/install/ 에서 Docker Compose를 설치해주세요."
    exit 1
fi

echo "✅ Docker 및 Docker Compose 확인됨"

# 이전 컨테이너 정리 (선택사항)
read -p "🗑️  이전 컨테이너를 정리하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 이전 컨테이너 정리 중..."
    docker-compose down --volumes --remove-orphans
    docker system prune -f
fi

# Docker 이미지 빌드 및 컨테이너 실행
echo "🏗️  Docker 이미지 빌드 및 컨테이너 실행 중..."
docker-compose up --build -d

# 실행 상태 확인
echo "⏳ 서비스 시작 대기 중..."
sleep 10

echo "🔍 컨테이너 상태 확인:"
docker-compose ps

# 헬스체크 확인
echo "🏥 서비스 헬스체크 중..."
echo "  - Backend API: http://localhost:5555/health"
echo "  - Frontend: http://localhost:8501"

# 백엔드 헬스체크
if curl -s -f http://localhost:5555/health > /dev/null; then
    echo "✅ Backend 서비스 정상 동작"
else
    echo "❌ Backend 서비스 헬스체크 실패"
fi

# 프론트엔드 헬스체크
if curl -s -f http://localhost:8501 > /dev/null; then
    echo "✅ Frontend 서비스 정상 동작"
else
    echo "❌ Frontend 서비스 헬스체크 실패"
fi

echo ""
echo "🎉 Good Travel Agent가 성공적으로 실행되었습니다!"
echo "================================================"
echo "📱 웹 애플리케이션: http://localhost:8501"
echo "🔌 API 서버: http://localhost:5555"
echo "📋 API 문서:"
echo "   - GET  /health  : 서버 상태 확인"
echo "   - POST /plan    : 여행 계획 생성"
echo "   - POST /weather : 날씨 정보 조회"
echo ""
echo "⏹️  서비스 중지: docker-compose down"
echo "📊 로그 확인: docker-compose logs -f"
echo "🔧 컨테이너 접속: docker exec -it gta-backend bash"