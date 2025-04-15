import smtplib
from email.mime.text import MIMEText
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


def send_alerts_email():
    conn = psycopg2.connect(
        host="postgres", dbname="crypto_db", user="airflow", password="airflow"
    )
    df = pd.read_sql("SELECT * FROM price_alerts_temp", conn)

    # df = pd.DataFrame(
    #     {
    #         "symbol": ["BTC-USD", "ETH-USD"],
    #         "date": ["2025-04-12", "2025-04-12"],
    #         "price": [62000.0, 3000.0],
    #         "avg_price_3mo": [65000.0, 3200.0],
    #         "drop_percent": [4.62, 6.25],
    #     }
    # )

    if not df.empty:
        # body = df.to_string(index=False)
        body = " mic 2 1 test"
        msg = MIMEText(f"🔻 Cryptos dropped more than 2%:\n\n{body}")
        msg["Subject"] = "Crypto Price Alert 🚨"
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = "mutwirifranco@gmail.com"  # or pull from env too

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.send_message(msg)

    with conn.cursor() as cur:
        cur.execute("TRUNCATE price_alerts_temp;")
        conn.commit()
    conn.close()


# send_alerts_email()
