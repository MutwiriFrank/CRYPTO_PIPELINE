from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
from pendulum import datetime, duration

default_args = {
    "owner": "franklin",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": duration(seconds=2),
}

with DAG(
    dag_id="crypto_pipeline_daily",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["crypto"],
) as dag:

    fetch_prices = BashOperator(
        task_id="fetch_crypto_prices",
        bash_command="python /opt/airflow/scripts/fetch_prices.py",
    )

    spark_analysis = BashOperator(
        task_id="analyze_prices_with_spark",
        bash_command="/opt/spark/bin/spark-submit /opt/airflow/spark/analyze_prices.py",
    )

    send_email = BashOperator(
        task_id="send_alerts_email",
        bash_command="python /opt/airflow/scripts/send_email.py",
    )

    # Task dependencies
    fetch_prices >> spark_analysis >> send_email
