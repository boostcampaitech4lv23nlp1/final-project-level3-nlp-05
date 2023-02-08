from datetime import timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

def print_world() -> None:
    print("hello hello I'm testing now")

with DAG(
    dag_id="hello_world",
    description="My First DAG",
    start_date=days_ago(0),
    schedule_interval="*/30 * * * *",
    tags=['my_dags'],
) as dag:

    t1 = BashOperator(
        task_id="data_insert_in_elastic",
        bash_command="python /opt/ml/final-project-level3-nlp-05/DB/Database/elastic_db.py",
        owner='sangmun',
        retries=3,
        retry_delay=timedelta(minutes=5),
    )

    # t2 = PythonOperator(
    #     task_id="print_world",
    #     python_callable=print_world,
    #     depends_on_past=True,
    #     owner='sanmun',
    #     retries=3,
    #     retry_delay=timedelta(minutes=5)
    # )

    t1