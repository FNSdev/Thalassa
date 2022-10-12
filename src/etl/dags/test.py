import time
from random import randint

import pendulum
from airflow import DAG
from airflow.decorators import task

with DAG(
    dag_id='test_python_operator',
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
) as dag:
    @task(task_id="dummy_task")
    def dummy_task() -> str:
        time.sleep(randint(20, 30))
        return "Enough!"

    dummy_task()
