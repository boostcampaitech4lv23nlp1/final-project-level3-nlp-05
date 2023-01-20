import requests
import datetime 

import streamlit as st
from streamlit.components.v1 import html

from confirm_button_hack import cache_on_button_press

#페이지 타이틀
st.set_page_config(page_title="News Summarization")

def button_click(idx):
    st.wirte(idx)

#검색페이지
def search_page():
    
    #Google처럼 어플 제목으로 하는 것이 좋을듯
    st.markdown("<h1 style='text-align: center;'>NEWSUMMARY</h1>", unsafe_allow_html=True)
    search_contain = st.empty()
    news_contain = st.empty()
    with open("app/style.css") as source_css:
        st.markdown(f"<style>{source_css.read()}</style>",unsafe_allow_html=True)
    if 'company_name' not in st.session_state:
        st.session_state.company_name = ""
    page_buttons=[]
    with search_contain.container():
        #검색창
        company_name = st.text_input("검색", placeholder ="회사명 입력",label_visibility='collapsed')
        
        #기간 검색창
        col1, col2 = st.columns([5, 2])
        search_date = col2.date_input("기간",value=(datetime.date(2022,12,26), datetime.date(2022,12,30)),label_visibility='collapsed')
        start_date = f"{search_date[0].year:0>4d}{search_date[0].month:0>2d}{search_date[0].day:0>2d}"  #시작검색일
        end_date = f"{search_date[1].year:0>4d}{search_date[1].month:0>2d}{search_date[1].day:0>2d}"    #종료검색일

        if st.session_state.company_name or company_name:
            # 회사이름 검색 요청
            if st.session_state.company_name != company_name and company_name is not None:
                st.session_state.company_name = company_name
                st.text("start")
                response = requests.get(f"http://localhost:8001/company_name/?company_name={st.session_state.company_name}&date_gte={start_date}&date_lte={end_date}&news_num=999")
                st.text("end")
                response = response.json()
                st.session_state["topic_number"] = response['topic']
                st.session_state["topics_text"] = response['one_sent']
                
                '''
                st.session_state["topic_number"] = [0,1,2]
                st.session_state["topics_text"] = ["편의점 GS25가 '원스피리츠'와 협업해 선보인 원소주 스피릿이 지난해 GS25에서 판매되는 모든 상품 중 매출 순위 7위를 기록했다고 17일 밝혔다.", 
                    "원소주 스피릿은 출시 직후 2달 동안 입고 물량이 당일 완판되는 오픈런 행렬이 이어져 왔으며 최근 GS25와 원스피리츠의 공급 안정화 노력에 따라 모든 점포에서 수량제한 없이 상시 구매가 가능해졌다.", 
                    "GS25는 오는 18일 원소주 스피릿 누적 판매량 400만 병 돌파 기념으로 상시 운영되는 1개입 전용 패키지를 선보여 상품의 프리미엄을 더하기로 했다."]
                '''
            #버튼 추가   
            ''' 
            for idx in range(int(len(st.session_state["topic_number"]) / 2) + 1):                
                col1, col2 = st.columns([1,1])
                topic_number = st.session_state["topic_number"][idx * 2]
                topic_text = st.session_state["topics_text"][idx * 2]
                col1.button(topic_text,key=f"button_{topic_number}",on_click = button_click, args=(idx,))
                topic_number = st.session_state["topic_number"][idx * 2 + 1]
                topic_text = st.session_state["topics_text"][idx * 2 + 1]
                col2.button(topic_text,key=f"button_{topic_number}",on_click = button_click, args=(idx,))
                
            
            if len(st.session_state["topic_number"]) % 2 == 1:
                col1, col2 = st.columns([1,1])
                topic_number = st.session_state["topic_number"][-1]
                topic_text = st.session_state["topics_text"][-1]
                col1.button(topic_text,key=f"button_{topic_number}",on_click = button_click, args=(idx))
            '''
            st.text(len(st.session_state["topic_number"]))
            for idx, (topic_number, topic_text) in enumerate(zip(st.session_state["topic_number"],st.session_state["topics_text"])):
                page_buttons.append(st.button(topic_text,key=f"button_{topic_number}"))
            
    for idx, button in enumerate(page_buttons):
        if button:
            with news_contain.container():
                news_page(idx)
            search_contain.empty()    

#뉴스 요약 페이지
def news_page(idx):
    #한줄요약(제목)
    topics_text = st.session_state["topics_text"][idx]
    topic_number = st.session_state["topic_number"][idx]
    st.subheader(topics_text)
    
    #뉴스링크 [날짜,언론사,헤드라인,URL]
    news_list = requests.get(f"http://localhost:8001/news/{topic_number}").json()
    with st.expander("뉴스 링크"):
        for idx in range(len(news_list['date'])):
            col1, col2, col3 = st.columns([1,1,5])
            col1.text(news_list['date'][idx])
            col2.text(news_list['press'][idx])
            col3.caption(f"<a href='{news_list['URL'][idx]}'>{news_list['headline'][idx]}</a>",unsafe_allow_html=True)
        
    
    #요약문
    st.subheader("요약문")
    summarization = requests.get(f"http://localhost:8001/summary/{topic_number}")
    st.write(summarization.json()["summarization"])
    #키워드
    st.subheader("키워드")
    _, col2 = st.columns([7,1])
    back_button = col2.button("back")
    if back_button:
        page_buttons.clear()
        news_contain.empty()
    

if __name__ == '__main__':
    search_page()
        
        