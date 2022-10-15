import requests
import json
import os
import time
from kafka import KafkaProducer
from datetime import date

TOPIC = os.environ.get("TOPIC")
SERVER_ADDR = os.environ.get("SERVER_ADDR")

print("Topic:", TOPIC)
print("Server:", SERVER_ADDR)

producer = KafkaProducer(
    bootstrap_servers=SERVER_ADDR, api_version=(7, 1, 3))

stocks = ["JFC", "ALI", "BDO", "BPI", "GLO", "MER", "SM", "TEL", "URC"]

for stock in stocks:
    url = f"http://phisix-api3.appspot.com/stocks/{stock}.json"
    response = requests.get(url)
    if response.ok:
        producer.send(TOPIC, json.dumps(response.json()).encode("utf-8"))
        print(f"Done sending {stock}")
    else:
        print(f"Error getting stock data for {stock}", response.status_code)
    time.sleep(1)

producer.flush()
print(f"Done sending all stocks for {date.today()}")
producer.close()