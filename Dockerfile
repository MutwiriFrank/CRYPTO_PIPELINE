FROM apache/airflow:2.7.3-python3.10

USER root

# Install Java and procps (for `ps` command)
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk curl procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Apache Spark
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"

RUN curl -L "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | \
    tar -xz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME}

# Add PostgreSQL JDBC driver to Spark jars directory
RUN curl -o ${SPARK_HOME}/jars/postgresql-jdbc.jar \
    https://jdbc.postgresql.org/download/postgresql-42.6.0.jar

# Add any other required JDBC drivers (uncomment if needed)
# RUN curl -o ${SPARK_HOME}/jars/mssql-jdbc.jar \
#     https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.2.0.jre11/mssql-jdbc-12.2.0.jre11.jar

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install Flask-Session==0.4.0