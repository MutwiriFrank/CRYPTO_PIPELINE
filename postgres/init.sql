CREATE DATABASE airflow;
\c airflow;

CREATE TABLE IF NOT EXISTS crypto_prices (
    symbol VARCHAR(10),
    date DATE,
    price DECIMAL,
    PRIMARY KEY (symbol, date)
);

CREATE TABLE IF NOT EXISTS price_anomalies (
    symbol VARCHAR(10),
    date DATE,
    price DECIMAL,
    avg_price_3mo DECIMAL,
    drop_percent DECIMAL
);


--last fetch per symbol
CREATE TABLE IF NOT EXISTS fetch_tracker (
    symbol VARCHAR(10) PRIMARY KEY,
    last_fetched_date DATE
);


CREATE TABLE IF NOT EXISTS price_alerts_temp (
    symbol TEXT,
    date DATE,
    price FLOAT,
    avg_price_3mo FLOAT,
    drop_percent FLOAT
);