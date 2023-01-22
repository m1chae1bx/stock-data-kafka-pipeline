"""Tests for app module"""
from unittest import TestCase
from unittest.mock import Mock, patch

# from kafka3 import KafkaConsumer
from src.app import create_consumer, main


class TestCreateConsumer(TestCase):
    """Tests for create_consumer function"""

    @patch("src.app.KafkaConsumer")
    def test_create_consumer(self, mock_kafka_consumer: Mock):
        """Successfully creates consumer"""
        # Act
        consumer = create_consumer("server_addr", "topic")

        # Assert
        self.assertEqual(consumer, mock_kafka_consumer.return_value)
        mock_kafka_consumer.assert_called_once_with(
            "topic",
            bootstrap_servers="server_addr",
            api_version=(7, 1, 3),
        )

    @patch("src.app.KafkaConsumer")
    def test_create_consumer_raises_exception(self, mock_kafka_consumer: Mock):
        """Creating KafkaConsumer raises exception"""
        # Arrange
        mock_kafka_consumer.side_effect = Exception("Error")

        # Act
        # Assert
        with self.assertRaises(ConnectionError), self.assertLogs(level="WARNING") as logs:
            create_consumer("server_addr", "topic")

        self.assertTrue(any("Error connecting to Kafka server" in log for log in logs.output))


class TestMain(TestCase):
    """Tests for main function"""

    @patch.dict("os.environ", {}, clear=True)
    def test_topic_not_set(self):
        """TOPIC environment variable not set"""
        # Act
        # Assert
        with self.assertRaises(SystemExit) as exc, self.assertLogs(level="CRITICAL") as logs:
            main()

        self.assertEqual(exc.exception.code, 1)
        self.assertTrue(
            any("Required TOPIC environment variable not set" in log for log in logs.output)
        )

    @patch.dict("os.environ", {"TOPIC": "topic"}, clear=True)
    def test_server_addr_not_set(self):
        """SERVER_ADDR environment variable not set"""
        # Act
        # Assert
        with self.assertRaises(SystemExit) as exc, self.assertLogs(level="CRITICAL") as logs:
            main()

        self.assertEqual(exc.exception.code, 1)
        self.assertTrue(
            any("Required SERVER_ADDR environment variable not set" in log for log in logs.output)
        )

    @patch.dict("os.environ", {"TOPIC": "topic", "SERVER_ADDR": "server_addr"})
    @patch("src.app.create_consumer")
    def test_create_consumer_raises_connection_error(self, mock_create_consumer: Mock):
        """create_consumer raises ConnectionError"""
        mock_create_consumer.side_effect = ConnectionError("Error")

        # Act
        # Assert
        with self.assertRaises(SystemExit) as exc, self.assertLogs(level="CRITICAL") as logs:
            main()

        self.assertEqual(exc.exception.code, 1)
        self.assertTrue(
            any("Unable to continue without Kafka consumer" in log for log in logs.output)
        )

    @patch.dict("os.environ", {"TOPIC": "topic", "SERVER_ADDR": "server_addr"})
    @patch("src.app.create_consumer")
    def test_successfully_receive_messages(self, mock_create_consumer: Mock):
        """Successfully receives messages"""
        # Arrange
        mock_consumer = mock_create_consumer.return_value
        mock_consumer.__iter__.side_effect = [
            iter([Mock(value=b"message1"), Mock(value=b"message2")]),
            KeyboardInterrupt(),
        ]

        # Act
        # Assert
        with self.assertLogs(level="INFO") as logs:
            main()

        self.assertTrue(any("message1" in log for log in logs.output))
        self.assertTrue(any("message2" in log for log in logs.output))
        mock_consumer.close.assert_called_once()
