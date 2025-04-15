import yfinance as yf
import psycopg2
from datetime import datetime, timedelta


# Fetch and store prices
def fetch_and_save_crpyto_prices():
    cryptos = ["BTC-USD", "ETH-USD", "BNB-USD"]
    today = datetime.today().date()

    conn = psycopg2.connect(
        dbname="crypto_db", user="airflow", password="airflow", host="postgres"
    )
    cur = conn.cursor

    # download the crptos and price
    for symbol in cryptos:
        # Get last download date

        cur.execute("SELECT last_fetched FROM fetch_tracker WHERE symbol=%s", (symbol,))

        result = cur.fetchone()

        if result:
            start_date = result[0] + timedelta(days=1)
        else:
            start_date = today - timedelta(days=30)

        # If below condition is true, Python skips all the code below it in the current loop iteration — including the API request — and moves straight to the next symbol in the loop.
        if start_date > today:
            continue

        df = yf.download(symbol, start=start_date, end=today)

        print(df)

        try:
            conn.autocommit = False  # Start a transaction
            for index, row in df.iterrows():
                cur.execute(
                    """
                    INSERT INTO crypto_prices (symbol, date, price)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (symbol, date) DO NOTHING
                """,
                    (symbol, index.date(), row["Close"]),
                )

            # Update fetch_tracker
            cur.execute(
                """
                INSERT INTO fetch_tracker (symbol, last_fetched)
                VALUES (%s, %s)
                ON CONFLICT (symbol)
                DO UPDATE SET last_fetched = EXCLUDED.last_fetched
            """,
                (symbol, today),
            )
        except Exception as e:
            conn.rollback()  # Something went wrong — undo everything
            print(f"Transaction failed for {symbol}: {e}")

    conn.commit()
    cur.close()
    conn.close()
