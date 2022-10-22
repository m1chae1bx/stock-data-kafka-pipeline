"""Consumes messages from the given Kafka topic and prints them"""

import os

from kafka import KafkaConsumer

TOPIC = os.environ.get("TOPIC")
SERVER_ADDR = os.environ.get("SERVER_ADDR")

print("Topic:", TOPIC)
print("Server:", SERVER_ADDR)
print("Connecting to Kafka...")

try:
    consumer = KafkaConsumer(
        TOPIC, bootstrap_servers=SERVER_ADDR, api_version=(7, 1, 3)
    )
except Exception:
    print("Error connecting to Kafka")
    raise

print("Connected! Listening for stock updates ...\n")

while True:
    for message in consumer:
        print("Received a message")
        consumed_message = message.value.decode()
        print(consumed_message + "\n")
