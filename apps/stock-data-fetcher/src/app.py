"""Fetches stock data from PSE website and sends it to the given Kafka topic"""

import json
import os
from datetime import date

from kafka3 import KafkaProducer

from scraper import scrape_stock_data

TOPIC = os.environ.get("TOPIC")
SERVER_ADDR = os.environ.get("SERVER_ADDR")

print("Topic:", TOPIC)
print("Server:", SERVER_ADDR, "\n")
print("Connecting to Kafka...")

try:
    producer = KafkaProducer(
        bootstrap_servers=SERVER_ADDR,
        api_version=(7, 1, 3)
        # value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    )
    print("Connected to Kafka\n")
except Exception:
    print("Error connecting to Kafka")
    raise

stocks = ["JFC", "ALI", "BDO", "BPI", "GLO", "MER", "SM", "TEL", "URC"]

for stock in stocks:
    try:
        print("Fetching data for", stock, "...")
        stock_data = scrape_stock_data(stock)
        producer.send(TOPIC, json.dumps(stock_data).encode("utf-8"))
        print(stock_data)
        print("Done sending", stock, "\n")
    except RuntimeError as exc:
        print(exc)

producer.flush()
producer.close()
print("Done sending all stocks for", date.today())
