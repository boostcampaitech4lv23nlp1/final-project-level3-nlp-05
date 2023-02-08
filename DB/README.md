## 개요
DB 서버를 운영하는데 필요한 사항들 정리 입니다

## directory
```
├── Database
│   ├── Dataset # 원천 News data들이 저장되는 경로
│   ├── airflow
│   │   ├── airflow.cfg
│   │   ├── airflow.db
│   │   ├── dags
│   │   │   └── hello_world.py # 1일 단위 작업 배치화 
│   │   └── webserver_config.py
│   ├── config
│   │   └── setting.json # elastic_serach config file
│   ├── context.py
│   ├── crawl.py
│   ├── elastic_db.py
│   └── preprocess.py
├── NaverCrawl # deprecated
├── README.md
├── elastic_search_install.sh
├── kibana_install.sh
├── main.py # fastapi server file
├── requirements.txt
└── utils.py
```

## virtualenv install
```
python -m venv db_env
source ./db_env/bin/activate
pip install -r requirements.txt
```

## elastic search install
```
bash ./elastic_search_install.sh
```

## kibana install and setting
```
bash ./kibana_insatll.sh
sudo systemctl start kibana.service
sudo systemctl enable kibana.service
```

edit kibana.yml
```
sudo vi /etc/kibana/kibana.yml
------------------------------
server.port: 30002

server.hostname: 0.0.0.0

elasticsearch.hosts: ["http://localhost:9200"]
```

## run fastapi
```
uvicorn main:app --reload --host=0.0.0.0 --port=30001
```

## run airflow
```
cd Database
export AIRFLOW_HOME=.
airflow webserver --port 30003
airflow scheduler
````
