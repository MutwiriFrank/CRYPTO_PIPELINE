from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
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

    spark_analysis = SparkSubmitOperator(
        task_id="run_spark_job",
        application="/opt/airflow/spark/analyze_prices.py",
        conn_id="spark_default",
        verbose=True,
        jars="/opt/spark/jars/postgresql-jdbc.jar",
        conf={
            "spark.master": "spark://spark:7077",
            # "spark.master": "spark://spark:7077",
            "spark.submit.deployMode": "client",
            "spark.driver.host": "airflow-scheduler",
            "spark.driver.port": "7078",
            "spark.driver.blockManager.port": "7080",
            "spark.executor.memory": "2g",
            "spark.driver.memory": "1g",
            "spark.port.maxRetries": "50",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            "spark.kryo.registrator": "org.apache.spark.serializer.KryoRegistrator",
            "spark.kryo.registrationRequired": "true",  # Catches serialization issues early
            "spark.kryo.classesToRegister": "org.apache.spark.rdd.RDD",  # Explicit registration
            "spark.cleaner.referenceTracking.cleanCheckpoints": "true",
        },
    )

    send_email = BashOperator(
        task_id="send_alerts_email",
        bash_command="python /opt/airflow/scripts/send_email.py",
    )

    # Task dependencies
    fetch_prices >> spark_analysis >> send_email
