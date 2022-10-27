"""Consumes messages from the given Kafka topic and prints them"""

import os

from kafka3 import KafkaConsumer
from kafka3.consumer.fetcher import ConsumerRecord

TOPIC = os.environ.get("TOPIC")
SERVER_ADDR = os.environ.get("SERVER_ADDR")

print("Topic:", TOPIC)
print("Server:", SERVER_ADDR, "\n")
print("Connecting to Kafka...")

try:
    consumer = KafkaConsumer(
        TOPIC, bootstrap_servers=SERVER_ADDR, api_version=(7, 1, 3)
    )
    print("Connected to Kafka\n")
except Exception:
    print("Error connecting to Kafka")
    raise

print("Listening for stock updates ...\n")
while True:
    message: ConsumerRecord
    for message in consumer:
        print("Received a message")
        consumed_message: str = message.value.decode()
        print(consumed_message, "\n")
