import streamlit as st
from datetime import date, timedelta
import requests
import json

# 페이지 설정
st.set_page_config(
    page_title="Good Travel Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title('✈️ Good Travel Agent - 맞춤형 여행 계획')
st.subheader('여행지, 예산, 선호도를 고려한 통합 여행 추천 시스템')

# 사이드바에 안내 메시지
with st.sidebar:
    st.header("📋 이용 안내")
    st.write("""
    **Good Travel Agent**는 다음 정보를 통합적으로 제공합니다:
    
    🌤️ **날씨 정보**
    - 여행 기간 날씨 예보
    - 옷차림 및 준비물 추천
    
    🚗 **교통 정보**
    - 최적 이동수단 추천
    - 예상 비용 및 소요시간
    
    🏨 **숙박 정보**
    - 위치별 숙소 추천
    - 가격대 및 편의시설
    
    📅 **일정 계획**
    - 효율적인 동선 계획
    - 관광지 및 체험 추천
    
    🍽️ **맛집 정보**
    - 현지 맛집 추천
    - 예산별 식당 정보
    """)

# 메인 폼
with st.form('travel_form'):
    col1, col2 = st.columns(2)
    
    with col1:
        departure = st.text_input('🛫 출발지', placeholder='예: 서울, 부산')
        destination = st.text_input('🎯 목적지', placeholder='예: 제주도, 도쿄')
        start_date = st.date_input('📅 여행 시작일', value=date.today())
        end_date = st.date_input('📅 여행 종료일', value=date.today() + timedelta(days=2))
    
    with col2:
        people = st.number_input('👥 인원수', min_value=1, max_value=20, value=2)
        budget = st.number_input('💰 예산(만원)', min_value=0, max_value=1000, value=50)
        purpose = st.selectbox('🎯 여행 목적', 
                              ['가족여행', '커플여행', '친구여행', '혼자여행', '출장', '휴양', '맛집탐방', '액티비티', '문화체험', '기타'])
        special_notes = st.text_area('📝 특이사항 (선택)', placeholder='특별한 요청사항이나 선호도를 입력해주세요')
    
    submitted = st.form_submit_button('🔍 여행 계획 생성', use_container_width=True)

if submitted:
    # 입력 검증
    if not departure or not destination:
        st.error('출발지와 목적지는 필수 입력 항목입니다.')
    elif start_date >= end_date:
        st.error('여행 종료일은 시작일보다 늦어야 합니다.')
    else:
        # 여행 정보 요약 표시
        with st.expander("📋 입력된 여행 정보", expanded=True):
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.write(f"**출발지:** {departure}")
                st.write(f"**목적지:** {destination}")
            with info_col2:
                st.write(f"**여행 기간:** {start_date} ~ {end_date}")
                st.write(f"**인원수:** {people}명")
            with info_col3:
                st.write(f"**예산:** {budget}만원")
                st.write(f"**여행 목적:** {purpose}")
            if special_notes:
                st.write(f"**특이사항:** {special_notes}")

        # API 요청 데이터 준비
        data = {
            'departure': departure,
            'destination': destination,
            'start_date': str(start_date),
            'end_date': str(end_date),
            'people': people,
            'budget': budget,
            'purpose': f"{purpose}. {special_notes}" if special_notes else purpose
        }
        
        # 안내 메시지 표시
        st.info("""
        🤖 **AI 에이전트들이 협업하여 여행 계획을 생성하고 있습니다...**
        
        다음 전문가들이 순차적으로 작업합니다:
        - 🌤️ 날씨 에이전트: 날씨 분석 및 준비물 추천
        - 🚗 교통 에이전트: 최적 이동수단 검색
        - 🏨 숙박 에이전트: 숙소 추천 및 분석
        - 📅 일정 에이전트: 효율적인 동선 계획
        - 🍽️ 맛집 에이전트: 현지 맛집 추천
        
        ⏱️ **소요 시간: 약 2-3분** (복잡한 요청일수록 시간이 더 걸릴 수 있습니다)
        """)
        
        # 로딩 표시
        with st.spinner('🔄 AI 에이전트들이 작업 중입니다... 잠시만 기다려주세요!'):
            try:
                response = requests.post('http://localhost:5555/plan', json=data, timeout=300)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('success'):
                        travel_data = result.get('data', {})
                        
                        st.success('✅ 여행 계획이 성공적으로 생성되었습니다!')
                        
                        # 탭으로 결과 구성
                        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌤️ 날씨 & 준비물", "🚗 교통편", "🏨 숙소", "📅 일정", "🍽️ 맛집"])
                        
                        with tab1:
                            st.header("🌤️ 날씨 정보 및 준비물")
                            if 'weather' in travel_data:
                                st.markdown(travel_data['weather'])
                            else:
                                st.info("날씨 정보를 불러오지 못했습니다.")
                        
                        with tab2:
                            st.header("🚗 교통편 추천")
                            if 'transport' in travel_data:
                                st.markdown(travel_data['transport'])
                            else:
                                st.info("교통편 정보를 불러오지 못했습니다.")
                        
                        with tab3:
                            st.header("🏨 숙소 추천")
                            if 'hotel' in travel_data:
                                st.markdown(travel_data['hotel'])
                            else:
                                st.info("숙소 정보를 불러오지 못했습니다.")
                        
                        with tab4:
                            st.header("📅 여행 일정")
                            if 'plan' in travel_data:
                                st.markdown(travel_data['plan'])
                            else:
                                st.info("일정 정보를 불러오지 못했습니다.")
                        
                        with tab5:
                            st.header("🍽️ 맛집 추천")
                            if 'food' in travel_data:
                                st.markdown(travel_data['food'])
                            else:
                                st.info("맛집 정보를 불러오지 못했습니다.")
                                
                    else:
                        st.error(f"❌ {result.get('message', '알 수 없는 오류가 발생했습니다.')}")
                        if result.get('error'):
                            st.error(f"오류 상세: {result['error']}")
                else:
                    st.error(f'❌ 서버 오류 (상태 코드: {response.status_code})')
                    
            except requests.exceptions.Timeout:
                st.error("""
                ⏰ **요청 시간이 초과되었습니다.**
                
                AI 에이전트들이 매우 복잡한 분석을 수행하느라 예상보다 시간이 걸렸습니다.
                
                **해결 방법:**
                1. 잠시 후 다시 시도해주세요
                2. 목적지를 더 구체적으로 입력해보세요
                3. 특이사항을 간단히 줄여보세요
                
                💡 일반적으로 2-3분 내에 완료되지만, 복잡한 요청의 경우 더 오래 걸릴 수 있습니다.
                """)
            except requests.exceptions.ConnectionError:
                st.error('❌ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.')
            except Exception as e:
                st.error(f'❌ API 요청 실패: {str(e)}')

# 하단 정보
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🤖 Powered by AI Agents | Made with ❤️ for Better Travel Planning</p>
    <p>각 분야 전문 에이전트들이 협업하여 최적의 여행 계획을 제공합니다.</p>
</div>
""", unsafe_allow_html=True)
