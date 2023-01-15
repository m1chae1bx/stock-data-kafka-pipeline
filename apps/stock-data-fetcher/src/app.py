"""Fetches stock data from PSE website and sends it to the given Kafka topic"""

import json
import logging
import os
import sys
from datetime import date

from kafka3 import KafkaProducer
from kafka3.errors import KafkaTimeoutError
from src.config import STOCK_CODES
from src.custom_types import StockDataFetchingError
from src.scraper import scrape_stock_data

logging.basicConfig(level=logging.INFO)


def create_producer(server_addr: str) -> KafkaProducer:
    """Create Kafka producer client"""
    try:
        logging.info("Connecting to Kafka server at %s ...", server_addr)
        producer = KafkaProducer(
            bootstrap_servers=server_addr,
            api_version=(7, 1, 3),
        )
        logging.info("Connected to Kafka server")
        return producer
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
        producer = create_producer(server_addr)
    except ConnectionError:
        logging.critical("Unable to continue without Kafka producer")
        sys.exit(1)

    logging.info("Sending stock data for %s ...", date.today())

    for stock in STOCK_CODES:
        stock_data = None
        try:
            logging.info("Fetching stock data for %s ...", stock)
            stock_data = scrape_stock_data(stock)
            logging.info("Stock data fetched: %s", stock_data)
        except StockDataFetchingError:
            logging.error("Error fetching stock data for %s", stock)
            continue

        try:
            logging.info("Sending stock data for %s ...", stock)
            producer.send(topic, json.dumps(stock_data).encode("utf-8"))
            logging.info("Sent stock data for %s", stock)
        except KafkaTimeoutError:
            logging.error("Error sending stock data for %s", stock)
            continue

    try:
        producer.flush()
    except KafkaTimeoutError:
        logging.exception("Failed to flush buffered records within timeout")
    finally:
        producer.close()
        logging.info("Connection to Kafka server closed")

    logging.info("Done sending all stock data")
