"""Consumes messages from the given Kafka topic and prints them"""

import logging
import os
import sys

from kafka3 import KafkaConsumer
from kafka3.consumer.fetcher import ConsumerRecord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# TOPIC = os.environ.get("TOPIC")
# SERVER_ADDR = os.environ.get("SERVER_ADDR")

# print("Topic:", TOPIC)
# print("Server:", SERVER_ADDR, "\n")
# print("Connecting to Kafka...")

# try:
#     consumer = KafkaConsumer(
#         TOPIC, bootstrap_servers=SERVER_ADDR, api_version=(7, 1, 3)
#     )
#     print("Connected to Kafka\n")
# except Exception:
#     print("Error connecting to Kafka")
#     raise

# print("Listening for stock updates ...\n")
# while True:
#     message: ConsumerRecord
#     for message in consumer:
#         print("Received a message")
#         consumed_message: str = message.value.decode()
#         print(consumed_message, "\n")


def create_consumer(server_addr: str, topic: str) -> KafkaConsumer:
    """Create Kafka consumer client"""
    try:
        logging.info("Connecting to Kafka server at %s on topic %s...", server_addr, topic)
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=server_addr,
            api_version=(7, 1, 3),
        )
        logging.info("Connected to Kafka server")
        return consumer
    except Exception as exc:
        logging.warning("Error connecting to Kafka server at %s", server_addr)
        raise ConnectionError("Error connecting to Kafka server") from exc


def main():
    """Main function"""
    topic = os.environ.get("TOPIC")
    if topic is None:
        logging.critical("Required TOPIC environment variable not set")
        sys.exit(1)

    server_addr = os.environ.get("SERVER_ADDR")
    if server_addr is None:
        logging.critical("Required SERVER_ADDR environment variable not set")
        sys.exit(1)

    try:
        consumer = create_consumer(server_addr, topic)
    except ConnectionError:
        logging.critical("Unable to continue without Kafka consumer")
        sys.exit(1)

    logging.info("Listening for stock data updates ...")

    while True:
        message: ConsumerRecord
        try:
            for message in consumer:
                logging.info("Received a message")
                consumed_message: str = message.value.decode()
                logging.info(consumed_message)
        except KeyboardInterrupt:
            logging.warning("Exiting due to keyboard interrupt...")
            break

    consumer.close()
