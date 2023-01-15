"""Tests for scraper module"""
from unittest import TestCase
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup
from requests import HTTPError, JSONDecodeError, Response
from src.scraper import (
    StockDataFetchingError,
    fetch_company_id,
    fetch_stock_data_soup,
    get_stock_data_point,
    scrape_stock_data,
)


class TestGetStockDataPoint(TestCase):
    """Tests for get_stock_data_point function"""

    def setUp(self):
        self.mock_soup = Mock(name="soup", spec=BeautifulSoup)
        self.mock_soup.find.return_value = self.mock_soup
        self.mock_soup.find_next_sibling.return_value = self.mock_soup
        self.mock_soup.text = "1,000.00"
        self.test_label = "Test label"

    def test_return_stock_data_point(self):
        """Test get_stock_data_point function correctly parses the stock data point"""
        # Act
        stock_data_point = get_stock_data_point(self.mock_soup, self.test_label)

        # Assert
        self.assertEqual(stock_data_point, "1,000.00")

    def test_soup_find_returns_none(self):
        """Test get_stock_data_point function raises StockDataParsingError when soup.find returns
        None"""
        # Arrange
        self.mock_soup.find.return_value = None

        # Act
        # Assert
        with self.assertRaises(StockDataFetchingError), self.assertLogs(level="ERROR") as logs:
            get_stock_data_point(self.mock_soup, self.test_label)

        for log in logs.output:
            self.assertIn("Label Test label not found", log)

    def test_soup_find_next_sibling_returns_none(self):
        """Test get_stock_data_point function raises StockDataParsingError when
        soup.find_next_sibling returns None"""
        # Arrange
        self.mock_soup.find_next_sibling.return_value = None

        # Act
        # Assert
        with self.assertRaises(StockDataFetchingError), self.assertLogs(level="ERROR") as logs:
            get_stock_data_point(self.mock_soup, "Test label")

        for log in logs.output:
            self.assertIn("Value for label Test label not found", log)


class TestFetchCompanyId(TestCase):
    """Tests for fetch_company_id function"""

    def setUp(self):
        self.test_stock_symbol = "AAPL"
        self.mock_response = Mock(name="response", spec=Response)
        self.mock_response.raise_for_status.return_value = None
        self.mock_response.json.return_value = [{"cmpyId": 1234}]

    @patch("src.scraper.requests")
    def test_return_company_id(self, mock_requests: Mock):
        """Test fetch_company_id function returns company id"""
        # Arrange
        mock_requests.get.return_value = self.mock_response

        # Act
        company_id = fetch_company_id("AAPL")

        # Assert
        assert company_id == 1234

    @patch("src.scraper.requests")
    def test_raise_for_status_raises_http_error(self, mock_requests: Mock):
        """Test fetch_company_id function raises StockDataFetchingError when
        response.raise_for_status() raises an HTTPError"""
        # Arrange
        self.mock_response.raise_for_status.side_effect = HTTPError()
        mock_requests.get.return_value = self.mock_response

        # Act
        # Assert
        with self.assertRaises(StockDataFetchingError), self.assertLogs(level="ERROR") as logs:
            fetch_company_id("AAPL")

        for log in logs.output:
            self.assertIn("Error fetching company ID of AAPL", log)

    @patch("src.scraper.requests")
    def test_json_raises_json_decode_error(self, mock_requests: Mock):
        """Test fetch_company_id function raises StockDataFetchingError when
        response.json()[0]["cmpyId"] raises a JSONDecodeError"""
        # Arrange
        self.mock_response.json.side_effect = JSONDecodeError("", "", 0)
        mock_requests.get.return_value = self.mock_response

        # Act
        # Assert
        with self.assertRaises(StockDataFetchingError), self.assertLogs(level="ERROR") as logs:
            fetch_company_id("AAPL")

        for log in logs.output:
            self.assertIn("Error fetching company ID of AAPL", log)


class TestFetchStockDataSoup(TestCase):
    """Tests for fetch_stock_data_soup function"""

    def setUp(self):
        self.mock_response = Mock(name="response", spec=Response)
        self.mock_response.raise_for_status.return_value = None
        self.mock_response.text = "John 3:16"

    @patch("src.scraper.BeautifulSoup")
    @patch("src.scraper.requests")
    def test_return_beautiful_soup_object(self, mock_requests: Mock, mock_beautiful_soup: Mock):
        """Test fetch_stock_data_soup function returns BeautifulSoup object"""
        # Arrange
        mock_requests.get.return_value = self.mock_response

        # Act
        soup = fetch_stock_data_soup(1234)

        # Assert
        assert soup == mock_beautiful_soup.return_value

    @patch("src.scraper.requests")
    def test_raise_for_status_raises_http_error(self, mock_requests: Mock):
        """Test fetch_stock_data_soup function raises StockDataFetchingError when
        response.raise_for_status() raises an HTTPError"""
        # Arrange
        self.mock_response.raise_for_status.side_effect = HTTPError()
        mock_requests.get.return_value = self.mock_response

        # Act
        # Assert
        with self.assertRaises(StockDataFetchingError), self.assertLogs(level="ERROR") as logs:
            fetch_stock_data_soup(1234)

        for log in logs.output:
            self.assertIn("Error fetching stock data of company ID 1234", log)


class TestScrapeStockData(TestCase):
    """Tests for scrape_stock_data function"""

    @patch("src.scraper.get_stock_data_point")
    @patch("src.scraper.fetch_stock_data_soup")
    @patch("src.scraper.fetch_company_id")
    def test_return_stock_data_object(
        self,
        mock_fetch_company_id: Mock,
        mock_fetch_stock_data_soup: Mock,
        mock_get_stock_data_point: Mock,
    ):
        """Test scrape_stock_data function returns StockData object"""
        # Arrange
        mock_fetch_company_id.return_value = 1234
        mock_fetch_stock_data_soup.return_value = "soup"
        mock_get_stock_data_point.side_effect = ["1.00", "2.00", "3.00", "4.00", "5"]

        # Act
        stock_data = scrape_stock_data("AAPL")

        # Assert
        assert stock_data == {
            "stock": "AAPL",
            "close": "1.00",
            "open": "2.00",
            "high": "3.00",
            "low": "4.00",
            "volume": "5",
        }

    @patch("src.scraper.fetch_company_id")
    def test_fetch_company_id_raises_error(self, mock_fetch_company_id: Mock):
        """Test scrape_stock_data function raises StockDataFetchingError when
        fetch_company_id(stock_symbol) raises an error"""
        # Arrange
        mock_fetch_company_id.side_effect = StockDataFetchingError()

        # Act
        # Assert
        with self.assertRaises(StockDataFetchingError), self.assertLogs(level="ERROR") as logs:
            scrape_stock_data("AAPL")

        for log in logs.output:
            self.assertIn("Error scraping stock data of AAPL", log)
