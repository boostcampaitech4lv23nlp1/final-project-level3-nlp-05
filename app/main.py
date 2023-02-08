import requests
from fastapi import FastAPI, Response, Request
from fastapi.encoders import jsonable_encoder

import time
import json
import pandas as pd
from typing import Dict, Union, List
from collections import defaultdict

from app.utils.BERTopic.bertopic_model import DevideTopic
from app.utils.One_sent_summary.one_sent_summarization import SummaryGenerater
from app.utils.KorBertSum.src.extract_topk_summarization import ExtractTopKSummary
from app.utils.KorBertSum.src.topic_summary import TopicSummary
from app.utils.SentimentAnalysis.SentimentAnalysis import TopicSentimentAnalysis

app = FastAPI()
# 토픽 분류
DT = DevideTopic()
# 한 줄 요약
SG = SummaryGenerater()
# 감성분석
TSA = TopicSentimentAnalysis()
# 토픽 내 요약 - 추출요약
openapi_key = '9318dc23-24ac-4b59-a99e-a29ec170bf02'    #추출요약 시 사용하는 openai key
ETKS = ExtractTopKSummary(openapi_key)
# 토픽 내 요약 - 생성요약
TS = TopicSummary()

#크롤링부터 한줄요약까지
@app.post("/company_name/")
async def request_crawl_news(request:Request) -> Response:
    '''
    검색하면 뉴스 크롤링부터 감성분석까지 진행
    input:
        request(Request) : 뉴스 크롤링 결과 DataFrame # news_df.columns = [title,titleNdescription,context,URL,date,category1,category2,concat_text]
    output:
        Dict{news_df(json) : 뉴스 dataframe_tojson # news_df.columns = [title,titleNdescription,context,URL,date,category1,category2,topic,concat_text]
             topic_df(json) : 토픽 dataframe_tojson # topic_df.columns =  [topic,one_sent,hard_category1,hard_category2,keywords,sentiment]
            }
    '''
    # 1. 크롤링 결과 가져오기
    body_bytes = await request.body()
    news_df = None
    if body_bytes:
        news_json = await request.json()
        news_df = pd.read_json(news_json,orient="columns")

    # 2. 토픽 분류
    news_df = DT.bertopic_modeling(news_df)
    # 3. 한 줄 요약
    topic_df = SG.summary(news_df)
    # 4. 감성분석
    topic_df = TSA.sentiment_analysis(topic_df)
    
    result = json.dumps({"news_df": news_df.to_json(orient = "records",force_ascii=False) ,"topic_df": topic_df.to_json(orient = "records",force_ascii=False)})   
    return Response(result, media_type="application/json")
    
# 토픽 내 뉴스 요약
@app.post("/summary/")
async def request_summary_news(request:Request):
    '''
    토픽 내 뉴스 요약 진행
    input 
        request(Request) : 토픽 내 뉴스 dataframe
    output
        Dict{
            summarization(str) : 토픽 내 뉴스 요약문
        }
    '''
    body_bytes = await request.body()
    summary_text = ""
    if body_bytes:
        news_json = await request.json()
        now_news_df = pd.read_json(news_json,orient="columns")
        #추출요약
        summary_df = ETKS.add_topk_to_df(now_news_df)
        #생성요약
        summary_text = TS.make_summary_paragraph(summary_df)
    return {"summarization":summary_text}
    