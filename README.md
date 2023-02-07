# 📰 NEWS.tar

## Table of content

* Intro : 팀 소개/ 프로젝스 소개(문제 정의) / 개발 목표
* Model/ Reasearch: 데이터셋 / 모델 / 연구 / 최종 적용 모델
* Product Serving: 아키텍쳐/ 구현/ 데모
* Result / Conclusion: 시연 영상 / 후속 개발 및 연구 / 결과 및 고찰
* Appendix: 도전적인 실험 / 레슨런 / 예상 Q&A / 팀원 개별 소개 등

## Intro

### “한눈에 파악하는 기업뉴스 NEWS.tar"
###### NEWs.tar는 뉴스 데이터를 주제 별로 분류하고 기사 내용을 요약하여 보여줌으로써 사용자들이 짧은 시간에 주요 뉴스 내용을 파악할 수 있도록 도와줍니다.*
<br>

### Motivation and Objective
✔️ 뉴스데이터는 양이 방대하고 쉽게 구할 수가 있음<br>
✔️ 하지만 투자를 하고 싶어 기업 관련 뉴스를 검색하면 너무나 많은 정보들이 제공이됨<br>
✔️ 이러한 뉴스데이터를 클러스터링 & 요약해서 **특정 기업에 대한 주제를 빠르게 파악하고 싶음**

- 비슷한 주제의 뉴스를 모아서 제공
- 각 주제의 기사들을 하나의 문장으로 요약
- 해당 주제에 대한 감정 분석 제공
- 같은 주제로 묶인 기사들의 전반적인 요약 문단 제공
<br>

### Team member
김진호                       |  신혜진                   |  이효정                    |  이상문                    |  정지훈                    |
:-------------------------:|:------------------------:|:------------------------:|:------------------------:|:-------------------------:
<img src="./asset/kjh_image.png" width=50% height=50%>    | <img src="./asset/shj_image.png" width=40% height=40%>  | <img src="./asset/lhj_image.png" width=50% height=50%>  |<img src="./asset/lsm_image.png" width=40% height=40%>|<img src="./asset/jjh_image.png" width=50% height=50%> 
| 토픽 모델링  | 본문 추출 요약 <br> 한줄 생성 요약| 프론트, 백엔드 <br> 한줄 요약 감성 분석|뉴스 데이터 수집 <br> DB 구축| 한줄 요약 모델링

## Dataset & Model

### flow chart
<img src="./asset/flow_chart.png" width=80% height=50%>

### dataset
- Naver developer api와 bigkinds의 뉴스데이터를 활용해서 뉴스 본문 데이터 수집
- 20221101 ~ 20230203 기간의 총 66만건의 데이터 수집
- 수집한 데이터는 전처리 과정을 거쳐 ElasticSeach에 Insert

### Model

#### 토픽모델링
| Embedding Model            | Shilhoutte Score                    | Speed(sec)    |
| ------------------ | ----------------------- |-------|
| Paraphrase mpnet | **0.7585** | 7.34 |
| KR-SBERT | 0.7439 | 6.68 |
| DistillBERT | 0.7012| 7.88 |
| Paraphrase MiniLM | 0.6994 | **5.81** |
| QA mpnet | 0.6927 |11.16|

#### 토픽 한 줄 요약
| Embedding Model            | Rouge-1(F1)     | Rouge-2(F1)    | Rouge-3(F1)     | Length    | Speed(sec)    |
| ------------------ | ----------------------- |-------|------------------ | ----------------------- |-------|
| kobart-summarization |  **0.495** | **0.339** | **0.413** | 115.83 | **0.46** |
| KR-SBERT |  **0.495** | 0.329 | 0.385 | 201.49 | 3.19 |
| DistillBERT |  0.488 | 0.324 | 0.394 | 180.29 | 0.64 |

#### 감성  분석
|Model | Loss |AUPRC |Micro F1 |Speed(sec) |Easy data (#48) | Medium data(#22) |Hard data (#23) |Total data (#93)|
| ------------------ | ----------------------- |-------|---------- | ---------------- |-------|------------- | ------------- |-------|
|roberta-large | **0.4667** | **88.1713** | **82.7956** | 0.7371 | **43** | **18** | **16** | **77** |
|roberta-base 1 | 0.9074 | 87.4126 | 76.3440 | 0.2793 | 42 | 17 | 12 | 71 | 
|roberta-base 2 | 0.5078 | 88.6208 | 78.4946 | **0.2668** | 42 | 14 | 17 | 73 |
|KorFinASC-XLM-RoBERTa | 4.3266 | 29.8050 | 32.2580 | 0.8201 | 14 | 7 | 7 | 28 |

#### 토픽 내 뉴스  요약
| Model | Rouge-1(F1) | Rouge-2(F1) | Rouge-3(F1) | Rouge-1(Recall) | Rouge-2(Recall) | Rouge-3(Recall) |

| ------------------ | ----------------------- |-------|
| Paraphrase mpnet | **0.7585** | 7.34 |
| KR-SBERT | 0.7439 | 6.68 |
| DistillBERT | 0.7012| 7.88 |
| Paraphrase MiniLM | 0.6994 | **5.81** |
| QA mpnet | 0.6927 |11.16|
## Product Serving

### Architecture

## Result

### 구현

### Demo

```
conda create -n final_project
pip install -r requirements.txt
bash ./install.sh # hanspell은 pip에 없음
```

새로운 패키지를 설치 했을때
```
pip list --format=freeze > ./requirements.txt
```

## streamlit run
```
streamlit run main.py --server.port 30001
```

## Result / Conclusion

### 시연영상
![](./asset/extractive_summary.gif)
## Appendix

### bla bla

