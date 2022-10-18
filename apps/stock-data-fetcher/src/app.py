import json
import os
from kafka import KafkaProducer
from datetime import date
from scraper import scrape_stock_data

TOPIC = os.environ.get("TOPIC")
SERVER_ADDR = os.environ.get("SERVER_ADDR")

print("Topic:", TOPIC)
print("Server:", SERVER_ADDR)

producer = KafkaProducer(
    bootstrap_servers=SERVER_ADDR, api_version=(7, 1, 3))

stocks = ["JFC", "ALI", "BDO", "BPI", "GLO", "MER", "SM", "TEL", "URC"]

for stock in stocks:
    try:
        stock_data = scrape_stock_data(stock)
        producer.send(TOPIC, json.dumps(stock_data).encode("utf-8"))
        print(f"Done sending {stock}")
    except Exception as e:
        print(f"Error fetching stock data for {stock}", e)

producer.flush()
print(f"Done sending all stocks for {date.today()}")
producer.close()