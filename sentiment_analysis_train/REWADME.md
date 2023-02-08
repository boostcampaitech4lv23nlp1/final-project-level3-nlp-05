# Sentiment Analysis
Sentiment Analysis 학습 코드 입니다.

## train 및 inference 방법
```
# train
python main.py --config config명 -mt
# inference
python main.py --config config명 -mi
```

## 파일 구성
```
📁sentiment_analysis_train
│   └── 📁best_model
│   └── 📁step_saved_model
│   └── 📁prediction
│   └── 📁data_loaders
│   └── 📁trainer
│   └── 📁utils
│   └── 📁dataset
│   └── 📁config   # 학습 시 사용할config
│   └── inference.py
│   └── train.py
│   └── main.py
```

## Dataset
Train/vaild dataset​
Finance Phrase Bank 번역 데이터(https://github.com/ukairia777/finance_sentiment_corpus)
Positive, Netural, Negative 3개의 카테고리로 분류​

Train/vaild 구성​
- Train dataset : 4361개​
- Valid dataset : 485개​

Test dataset​
2022.12.01 ~ 2022.12.31 삼성전자, 하이닉스, 네이버, 카카오 한 줄 요약 93개의 문장에 대해 라벨링​
Test dataset level : 학습데이터와 실제 데이터와의 비교를 위해 다음과 같이 난이도를 부과함​
- 난이도 하(0) - 상승, 하락 등 쉬운단어 또는 데이터셋에 비슷한 문장이 존재 ​
- 난이도 중(1) - 데이터셋과 비슷한 듯 하면서 다른 문장 ​
                   혹은 데이터셋에는 등장하지 않지만 라벨을 유추할 수 있는 경우​
- 난이도 상(2) - 데이터셋에 비슷한 문장이 않거나 금융관련 문장이 아닌 경우​

* 난이도의 경우 완전하지 않으므로 학습데이터와 실제 데이터가 얼마나 다른지(즉 난이도 하와 난이도 중/상의 차이가 어떤지)만 확인하는데 사용한다.

## 결과

klue-roberta-large 10epoch

eval loss:  0.4667905271053314
eval auprc:  88.17139458623839
eval micro f1 score:  82.79569892473118

inference time : 0.7371985912322998

-------------------------------------------------------------
klue/roberta-base 10epoch

eval loss:  0.9074585437774658
eval auprc:  87.41267282773485
eval micro f1 score:  76.34408602150536

inference time : 0.2793910503387451

--------------------------------------------------------------
klue/roberta-base 7epoch

eval loss:  0.5078420042991638
eval auprc:  88.62080755826946
eval micro f1 score:  78.49462365591397

inference time : 0.26684069633483887

--------------------------------------------------------------
amphora/KorFinASC-XLM-RoBERTa

eval loss:  4.326679706573486
eval auprc:  29.805084576881054
eval micro f1 score:  32.25806451612903

inference time : 0.8201456069946289

--------------------------------------------------------------