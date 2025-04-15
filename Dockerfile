FROM apache/airflow:2.7.3-python3.10

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install Flask-Session==0.4.0

