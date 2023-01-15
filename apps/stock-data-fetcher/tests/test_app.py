"""Tests for app module"""
from datetime import date
from unittest import TestCase
from unittest.mock import Mock, call, patch

from kafka3 import KafkaProducer
from kafka3.errors import KafkaTimeoutError
from src.app import create_producer, main
from src.types import StockDataFetchingError

mock_stock_codes = ["XYZ"]


class TestCreateProducer(TestCase):
    """Tests for create_producer function"""

    @patch("src.app.KafkaProducer")
    def test_create_producer(self, mock_kafka_producer: Mock):
        """Successfully creates producer"""
        # Act
        producer = create_producer("server_addr")

        # Assert
        self.assertEqual(producer, mock_kafka_producer.return_value)
        mock_kafka_producer.assert_called_once_with(
            bootstrap_servers="server_addr", api_version=(7, 1, 3)
        )

    @patch("src.app.KafkaProducer")
    def test_create_producer_raises_exception(self, mock_kafka_producer: Mock):
        """Creating KafkaProducer raises exception"""
        # Arrange
        mock_kafka_producer.side_effect = Exception("Error")

        # Act
        # Assert
        with self.assertRaises(ConnectionError), self.assertLogs(level="WARNING") as logs:
            create_producer("server_addr")

        self.assertTrue(any("Error connecting to Kafka server" in log for log in logs.output))


@patch("src.app.STOCK_CODES", mock_stock_codes)
class TestMain(TestCase):
    """Tests for main function"""

    @patch("src.app.json")
    @patch("src.app.scrape_stock_data")
    @patch("src.app.create_producer")
    @patch("src.app.os")
    def test_successful_send(
        self,
        mock_os: Mock,
        mock_create_producer: Mock,
        mock_scrape_stock_data: Mock,
        mock_json: Mock,
    ):
        """Test data is sent successfully data via producer.send"""
        # Arrange
        mock_os.environ = {"TOPIC": "topic", "SERVER_ADDR": "server_addr"}
        mock_producer = Mock(spec=KafkaProducer)
        mock_producer.send.return_value = None
        mock_create_producer.return_value = mock_producer
        mock_scrape_stock_data.return_value = "stock_data"
        mock_json.dumps.return_value = mock_json
        mock_json.encode.return_value = "encoded_json"

        with patch("src.app.date") as mock_date:
            mock_date.today.return_value = date(2022, 1, 1)

            # Act
            main()

            # Assert
            expected_calls = [call("topic", "encoded_json")] * len(mock_stock_codes)
            mock_producer.send.assert_has_calls(expected_calls)

    @patch("src.app.os")
    def test_no_topic_env_var_raises_runtime_error(self, mock_os: Mock):
        """Test no TOPIC environment variable raises RuntimeError"""
        # Arrange
        mock_os.environ = {"SERVER_ADDR": "server_addr"}

        # Act
        # Assert
        with self.assertRaises(SystemExit), self.assertLogs(level="ERROR") as logs:
            main()

        self.assertTrue(
            any("Required TOPIC environment variable not set" in log for log in logs.output)
        )

    @patch("src.app.os")
    def test_no_server_addr_env_var_raises_runtime_error(self, mock_os: Mock):
        """Test no SERVER_ADDR environment variable raises RuntimeError"""
        # Arrange
        mock_os.environ = {"TOPIC": "topic"}

        # Act
        # Assert
        with self.assertRaises(SystemExit), self.assertLogs(level="ERROR") as logs:
            main()

        self.assertTrue(
            any("Required SERVER_ADDR environment variable not set" in log for log in logs.output)
        )

    @patch("src.app.date")
    @patch("src.app.os")
    @patch("src.app.create_producer")
    @patch("src.app.scrape_stock_data")
    def test_scrape_stock_data_raises_runtime_error(
        self,
        mock_scrape_stock_data: Mock,
        mock_create_producer: Mock,
        mock_os: Mock,
        mock_date: Mock,
    ):
        """Test scrape_stock_data raises RuntimeError"""
        # Arrange
        mock_os.environ = {"TOPIC": "topic", "SERVER_ADDR": "server_addr"}
        mock_create_producer.return_value = Mock(spec=KafkaProducer)
        mock_scrape_stock_data.side_effect = StockDataFetchingError()
        mock_date.today.return_value = date(2022, 1, 1)

        # Act
        with self.assertLogs(level="ERROR") as logs:
            main()

        # Assert
        self.assertTrue(any("Error fetching stock data for XYZ" in log for log in logs.output))

    @patch("src.app.date")
    @patch("src.app.os")
    @patch("src.app.create_producer")
    @patch("src.app.scrape_stock_data")
    def test_producer_send_raises_kafka_timeout_error(
        self,
        mock_scrape_stock_data: Mock,
        mock_create_producer: Mock,
        mock_os: Mock,
        mock_date: Mock,
    ):
        """Test producer.send raises KafkaTimeoutError"""

        # Arrange
        mock_os.environ = {"TOPIC": "topic", "SERVER_ADDR": "server_addr"}
        mock_producer = Mock(spec=KafkaProducer)
        mock_producer.send.side_effect = KafkaTimeoutError("Error")
        mock_create_producer.return_value = mock_producer
        mock_scrape_stock_data.return_value = "stock_data"
        mock_date.today.return_value = date(2022, 1, 1)

        # Act
        with self.assertLogs(level="ERROR") as logs:
            main()

        # Assert
        self.assertTrue(any("Error sending stock data for XYZ" in log for log in logs.output))

    @patch("src.app.date")
    @patch("src.app.os")
    @patch("src.app.create_producer")
    @patch("src.app.scrape_stock_data")
    def test_producer_flush_raises_exception(
        self,
        mock_scrape_stock_data: Mock,
        mock_create_producer: Mock,
        mock_os: Mock,
        mock_date: Mock,
    ):
        """Test producer.flush raises Exception"""

        # Arrange
        mock_os.environ = {"TOPIC": "topic", "SERVER_ADDR": "server_addr"}
        mock_producer = Mock(spec=KafkaProducer)
        mock_producer.flush.side_effect = KafkaTimeoutError("Error")
        mock_create_producer.return_value = mock_producer
        mock_scrape_stock_data.return_value = "stock_data"
        mock_date.today.return_value = date(2022, 1, 1)

        # Act
        with self.assertLogs(level="ERROR") as logs:
            main()

        # Assert
        self.assertTrue(
            any("Failed to flush buffered records within timeout" in log for log in logs.output)
        )
