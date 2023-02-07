import datetime
from collections import Counter
import json
import pandas as pd
import requests
from PIL import Image
import os, base64
import streamlit as st
from streamlit import session_state as state
from streamlit.components.v1 import html
from annotated_text import annotated_text

from utils.confirm_button_hack import cache_on_button_press
from utils.BringNews import bring_news
# 페이지 타이틀
st.set_page_config(page_title="NEWS.tar", layout="wide")

# css 세팅
with open("frontend/utils/style.css") as source_css:
    st.markdown(f"<style>{source_css.read()}</style>", unsafe_allow_html=True)

#state 세팅
if "company_name" not in state:
    state.company_name = ""
if "before_company_name" not in state:
    state.before_company_name = ""
if "before_search_date" not in state:
    state.before_search_date = (datetime.date(2023, 1, 25),datetime.datetime.now(),)
if "options_category" not in state:
    state['options_category'] = ["정치", "경제", "사회", "문화", "국제", "지역", "스포츠", "IT_과학"]
if "options_sentiment" not in state:
    state['options_sentiment'] = ["긍정", "부정", "중립"]
if 'search_list' not in state:
    search_list = pd.read_csv("frontend/assets/autocomplete.csv", index_col=0)["name"]
    search_list.loc[0] = ""
    search_list.sort_index(inplace=True)
    state['search_list'] = search_list
if 'stock_name_list' not in state:
    state['stock_name_list'] = pd.read_csv("frontend/assets/name_code.csv", index_col=0)            

# 검색페이지
def search_page():
    st.markdown(get_img_with_href('frontend/assets/logo.png'), unsafe_allow_html=True)
    search_contain = st.empty()
    news_contain = st.empty()
    
    page_buttons = []
    # 검색페이지
    with search_contain.container():
        _, center, _ = st.columns([1, 8, 1])
        # 검색창 + 자동완성 기능
        center.selectbox(
            label="회사명 혹은 종목코드를 입력하세요.",
            options=state['search_list'],
            label_visibility="collapsed",
            key = 'company_name'
        )
        
        _, sentiment_col, category_col, _ = st.columns([1, 3, 5, 1])
        _, col0, col1, col2, col3, _ = st.columns([2, 6, 3.5, 3.5, 3, 2])

        # checkbox options for article sentiment
        sentiment_col.multiselect(
            "기사 감성 선택",
            ["긍정", "부정", "중립"],
            default=state['options_sentiment'],
            on_change=None,
            key="options_sentiment"
        )

        # checkbox options for article category
        category_col.multiselect(
            "기사 카테고리 선택",
            ["정치", "경제", "사회", "문화", "국제", "지역", "스포츠", "IT_과학"],
            default=state['options_category'],
            on_change=None,
            key = 'options_category'
        )

        # 기간 검색창
        col3.date_input(
            "기간",
            value=state.before_search_date,
            label_visibility="collapsed",
            key="search_date",
        )

        _  , center, _ = st.columns([1, 8, 1])
        # 검색한 경우
        if (state.before_company_name != "" or state.company_name != "")and len(state.search_date) > 1:
            
            # 검색어나 검색기간이 바뀌면 news 데이터 새로 받기
            if state.company_name != "" and (state.before_company_name != state.company_name or state.before_search_date != state.search_date):
                state.before_company_name = state.company_name
                state.before_search_date = state.search_date
                
                # 종목코드로 되어있으면 회사명으로 변환
                if state.before_company_name.isdigit():
                    company_name = state['stock_name_list'][state['stock_name_list']["code"] == int(state.before_company_name)]['name'].values[0]
                else:
                    company_name = state.before_company_name
                
                # 기간 설정
                start_date = f"{state.search_date[0].year:0>4d}{state.search_date[0].month:0>2d}{state.search_date[0].day:0>2d}"  # 시작검색일
                end_date = f"{state.search_date[1].year:0>4d}{state.search_date[1].month:0>2d}{state.search_date[1].day:0>2d}"  # 종료검색일
                
                # 회사이름 검색 요청
                # 1. 크롤링
                news_df = bring_news(company_name, start_date ,end_date)
                # 2. 뉴스가 없으면 끝 아니면 토픽 분류에서 감성 분석까지 진행
                if len(news_df) == 0:
                    topic_df = pd.DataFrame()
                else:
                    news_json = news_df.to_json(orient="columns", force_ascii=False)
                    response = requests.post(f"http://localhost:8001/company_name/",json=news_json)
                    response = response.json()
                    news_df = pd.read_json(response["news_df"],orient="records")
                    topic_df = pd.read_json(response["topic_df"],orient="records")

                state["news_df"] = news_df
                state["topic_df"] = topic_df

            # 회사명으로 되어있으면 종목코드 저장
            if state.before_company_name.isdigit():
                stock_num = state.before_company_name
            else:
                stock_num = state['stock_name_list'][state['stock_name_list']["name"] == str(state.before_company_name)]["code"].values[0]
                stock_num = f"{int(stock_num):06}"

            # 주가 출력
            with col0:
                stock_wiget(stock_num)

            # 뉴스 요약 정보 출력
            col3.info(
                f"""
                📰 검색된 뉴스 {len(state["news_df"])}개  
                🍪 추출 토픽 수 {len(state["topic_df"])}개 
                """
            )  # 🔥
                
            # 뉴스가 없으면 결과가 없다고 반환 아니면 분류 결과 출력
            if len(state["news_df"]) == 0:
                _, col_line, _ = st.columns([1, 8, 1])
                col_line.warning("검색된 뉴스가 충분하지 않습니다. 기간을 늘려주세요", icon="⚠️")
            else:
                page_buttons = show_topic()

        # 검색하지 않았을 때는 주요 증시 지표를 보여줌
        else: 
            empty1, center, empty2 = st.columns([0.9, 8, 0.9])
            with center:
                index_wiget()

    # 요약문 누르면 해당 페이지로
    for button_key in page_buttons:
        if state[button_key]:
            search_contain.empty()
            with news_contain.container():
                news_page(button_key)


# 뉴스 요약 페이지
def news_page(topic_number:int):
    '''
    input 
        topic_number(int) : 토픽 번호
    '''
    # 한줄요약(제목)
    topics_text = state["topic_df"][state["topic_df"]['topic'] == topic_number]["one_sent"].values[0]
    empty0 = st.write("")
    empty1, center, empty2 = st.columns([1, 8, 1])
    center.subheader(topics_text)

    #뒤로가기 버튼
    empty1, _, col2, empty2 = st.columns([1, 7, 1, 1])
    back_button = col2.button("back")
    if back_button:
        page_buttons.clear()
        news_contain.empty()

    # 뉴스링크
    news_df = state["news_df"]
    news_list = news_df[news_df["topic"] == topic_number]
    news_list = news_list.reset_index(drop=True)

    empty1, center, empty2 = st.columns([1, 8, 1])
    with center.expander("뉴스 링크"):
        for _, row in news_list[:12].iterrows():
            st.caption(f"<p>{row['date']} &nbsp&nbsp&nbsp&nbsp <a href='{row['URL']}'>{row['title']}</a> </p>", unsafe_allow_html=True)

    # 요약문
    empty1, center, empty2 = st.columns([1, 8, 1])
    center.subheader("요약문")
    now_news_df = news_list[["context"]]
    now_news_json = now_news_df.to_json(orient="columns", force_ascii=False)
    summarization = requests.post(f"http://localhost:8001/summary/",json=now_news_json)
    summary_text = summarization.json()["summarization"]
    center.write(summary_text)

# 세부 기능
# 카테고리별로 토픽을 보여줌
def show_topic():
    page_buttons = []
    label_to_icon = {"negative": "😕", "neutral": "😐", "positive": "😃"}
    sentiment_color = {'positive':'#4593E7', 'negative':'#E52828', 'neutral':'#BDBDBD'}
    keyword_annotate_color = ["#B4C9C7", "#F3BFB3","#8A9BA7"]
    # 선택된 카테고리와 감성에 대해서만 토픽 가져오기
    topic_df_filtered = filter_topic()
    # 카테고리 순서 계산
    category1_sort_list_with_emoji = cal_cat_order(topic_df_filtered)

    category_tab_list = st.tabs(category1_sort_list_with_emoji)
    for tab, cat1 in zip(category_tab_list, category1_sort_list_with_emoji):
        with tab:
            #해당 카테고리의 뉴스만 가져와 정렬
            now_topic_df = topic_df_filtered[topic_df_filtered['hard_category1'] == cat1[2:-3]]
            now_topic_df = now_topic_df.sort_values(by=['sentiment'],ascending=False).reset_index(drop=False)
            
            cols = [0,0]
            cols[0], cols[1] = st.columns([4, 4])
            for idx, row in now_topic_df.iterrows():
                topic_number = int(row["topic"])
                topic_keyword = row["keywords"].split("_")
                topic_keyword = [(topic_keyword[idx],"",keyword_annotate_color[idx]) for idx in range(len(topic_keyword))]
                page_buttons.append(topic_number)
                # 카테고리, 감성분석, 상위 3개의 키워드, 한 줄 요약문 출력
                now_idx = idx % 2
                with cols[now_idx]:
                    annotated_text(
                        (row["hard_category1"], "Category", "#D1C9AC"),
                        (f"{label_to_icon[row['sentiment']]}", "Sentiment", sentiment_color[row["sentiment"]])
                    )
                    annotated_text(*topic_keyword)
                cols[now_idx].button(row["one_sent"], key=topic_number)
            st.markdown("---")
    return page_buttons

# 선택된 카테고리와 감성분석 결과만 가져오기
def filter_topic():
    sentiment_dict = {'긍정':'positive', '중립':'neutral', '부정':'negative'}
    # 선택된 카테고리만을 포함하도록 필터링
    topic_df_filtered = state['topic_df']
    topic_df_filtered = topic_df_filtered[topic_df_filtered['hard_category1'].isin(state['options_category'])]
    # 선택된 감성만 포함하도록 필터링
    options_sentiment = [sentiment_dict[i] for i in state['options_sentiment']]
    topic_df_filtered = topic_df_filtered.loc[topic_df_filtered['sentiment'].isin(options_sentiment)]
    return topic_df_filtered

# 카테고리 순서 정하기    
def cal_cat_order(topic_df_filtered:pd.DataFrame):
    emoji = {"정치":'🏛', "경제":'💰', "사회":'🤷', "문화":'🎎', "국제":'🌐', "지역":'🚞', "스포츠":'⚽', "IT_과학":'🔬'}
    category1_sort_list = list(Counter(topic_df_filtered['hard_category1']).keys())
    counter = Counter(topic_df_filtered['hard_category1'])
    #경제를 1순위로 올리기
    if '경제' in category1_sort_list: 
        category1_sort_list.remove('경제')
        category1_sort_list = ['경제'] + category1_sort_list
    category1_sort_list_with_emoji = []
    for cat in category1_sort_list:
        category1_sort_list_with_emoji.append(emoji[cat]+' '+cat+f'({counter[cat]})')
    return category1_sort_list_with_emoji

# 뉴스로고(png) 파일을 보여주기 위한 함수
@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
    
@st.cache(allow_output_mutation=True)
def get_img_with_href(local_img_path):
    img_format = os.path.splitext(local_img_path)[-1].replace(".", "")
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f"""<div style="text-align: center;"><img src="data:image/{img_format};base64,{bin_str}" style="height:100px;"/></div>"""
    return html_code
    
#주요 증시 정보 위젯
def index_wiget():
    html(
        """
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <div class="tradingview-widget-copyright"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-tickers.js" async>
        {
        "symbols": [
        {
        "description": "KOSPI",
        "proName": "KRX:KOSPI"
        },
        {
        "description": "KOSDAQ",
        "proName": "KRX:KOSDAQ"
        },
        {
        "description": "NASDAQ 100",
        "proName": "NASDAQ:NDX"
        },
        {
        "description": "S&P 500",
        "proName": "FRED:SP500"
        },
        {
        "description": "USD/KRW",
        "proName": "FX_IDC:USDKRW"
        }
        ],
        "colorTheme": "light",
        "isTransparent": false,
        "showSymbolLogo": true,
        "locale": "kr"
        }
        </script>
        </div>
        <!-- TradingView Widget END -->
        """
    )

# 회사 주식 위젯
def stock_wiget(stock_num):
    info = """
    "symbol": "KRX:{0}",
    "width": "100%",
    "height": "100%",
    "locale": "kr",
    "dateRange": "3M",
    "colorTheme": "light",
    "trendLineColor": "rgba(255, 0, 0, 1)",
    "underLineColor": "rgba(204, 0, 0, 0.3)",
    "underLineBottomColor": "rgba(41, 98, 255, 0)",
    "isTransparent": false,
    "autosize": false,
    "largeChartUrl": ""
    """.format(
        stock_num
    )
    info = "{" + info + "}"

    docstring = """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
    <div class="tradingview-widget-container__widget"></div>
    <div class="tradingview-widget-copyright"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
    {0}
    </script>
    </div>
    <!-- TradingView Widget END -->
    """.format(
        info
    )
    html(docstring)

if __name__ == "__main__":
    search_page()