import streamlit as st
from datetime import date
import requests

st.title('Good Travel Agent - 여행 정보 입력')

with st.form('travel_form'):
    departure = st.text_input('출발지', placeholder='예: 서울')
    destination = st.text_input('목적지', placeholder='예: 도쿄')
    start_date = st.date_input('여행 시작일', value=date.today())
    end_date = st.date_input('여행 종료일', value=date.today())
    people = st.number_input('인원수', min_value=1, value=1)
    budget = st.number_input('예산(만원)', min_value=0, value=0)
    purpose = st.text_input('여행 목적/특이사항', placeholder='예: 가족여행, 맛집탐방 등')
    submitted = st.form_submit_button('제출')

if submitted:
    st.success('입력 완료!')
    st.write('출발지:', departure)
    st.write('목적지:', destination)
    st.write('여행 기간:', start_date, '~', end_date)
    st.write('인원수:', people)
    st.write('예산:', budget, '만원')
    st.write('여행 목적/특이사항:', purpose)

    # Flask API로 데이터 전송
    data = {
        'departure': departure,
        'destination': destination,
        'start_date': str(start_date),
        'end_date': str(end_date),
        'people': people,
        'budget': budget,
        'purpose': purpose
    }
    try:
        response = requests.post('http://localhost:5000/plan', json=data)
        if response.status_code == 200:
            result = response.json()
            st.header('여행 추천 결과')
            st.subheader('숙소')
            st.write(result['hotel'])
            st.subheader('일정')
            st.write(result['plan'])
            st.subheader('맛집')
            st.write(result['food'])
            st.subheader('이동수단')
            st.write(result['transport'])
        else:
            st.error('서버 오류!')
    except Exception as e:
        st.error(f'API 요청 실패: {e}')
