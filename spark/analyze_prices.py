from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg
from datetime import date
import psycopg2

from pyspark import SparkContext

sc = SparkContext.getOrCreate()
sc.setCheckpointDir("/tmp/checkpoints")  # Fresh checkpoint dir
sc.setLogLevel("DEBUG")  # For detailed serialization logs

spark = (
    SparkSession.builder.appName("CryptoAnomalies")
    .master("spark://spark:7077")
    .getOrCreate()
)

df = (
    spark.read.format("jdbc")
    .option("url", "jdbc:postgresql://postgres:5432/crypto_db")
    .option("driver", "org.postgresql.Driver")
    .option("dbtable", "crypto_prices")
    .option("user", "airflow")
    .option("password", "airflow")
    .load()
)


latest_date = df.agg({"date": "max"}).collect()[0][0]
latest_df = df.filter(col("date") == latest_date)
avg_df = df.groupBy("symbol").agg(avg("price").alias("avg_price_3mo"))
joined = latest_df.join(avg_df, "symbol")
result = joined.withColumn(
    "drop_percent", (col("avg_price_3mo") - col("price")) / col("avg_price_3mo") * 100
)

result.write.format("jdbc").option(
    "url", "jdbc:postgresql://postgres:5432/crypto_db"
).option("dbtable", "price_anomalies").option("user", "airflow").option(
    "password", "airflow"
).mode(
    "append"
).save()

# Save alerts (only drops > 2%) to temp table
if result.count() > 0:
    result.filter(col("drop_percent") > 2).write.format("jdbc").option(
        "url", "jdbc:postgresql://postgres:5432/crypto_db"
    ).option("dbtable", "price_alerts_temp").option("user", "airflow").option(
        "password", "airflow"
    ).mode(
        "overwrite"
    ).save()

    spark.stop()
