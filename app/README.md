# Frontend 실행
final-project-level3-nlp-05 폴더 내에서 `streamlit run frontend/main.py --server.port=30001` 실행

# Backend 실행
final-project-level3-nlp-05 폴더 내에서 `python -m app` 실행

# KoBert 사용
```
pip install git+https://git@github.com/SKTBrain/KoBERT.git@master
```

# 버토픽 gpu에서 실행하기
```
pip install cupy-cuda11x
pip install cuml-cu11 --extra-index-url=https://pypi.ngc.nvidia.com
pip install cupy-cuda110
```

# KorBertSum setting
- `app/utils/KorBertSum` 에서 001_bert_morp_pytorch.zip 앞축해제
```
📁app/utils/KorBertSum
│   └──📁001_bert_morp_pytorch
```
- `app/utils/KorBertSum/bert_models/bert_classifier2` 에서 model_step_35000.zip 앞축해제
```
📁app/utils/KorBertSum/bert_models/bert_classifier2
│   └──model_step_35000.pt
```

# SentimentAnalysis setting
- `app/utils/KorBertSum` 에서 pytorch_model_10.zip 앞축해제
```
📁app/utils/SentimentAnalysis
│   └──pytorch_model_10.bin
```

# 프로젝트 전체 파일 구성
```
📁app
│   └── utils
│   |    └── 📁BERTopic # 토픽 분류
│   |    └── 📁One_sent_summary # 한 줄 요약
│   |    └── 📁SentimentAnalysis  # 감성 분석
│   |    └── 📁KorBertSum # 토픽 내 뉴스 요약
│   └── __main__.py # Backend 실행 파일
│   └── main.py #Backend
│
📁frontend
│   |    └── 📁assets
│   |    └── 📁utils 
|   │    |    └── BringNews.py # DB에서 뉴스 가져오기
│   └── main.py #Frontend
│
📁DB
│   └── 📁Database
│   └── utils.py 
│   └── main.py 
│
📁sentiment_analysis_train # 감성 분석 학습 코드
```
