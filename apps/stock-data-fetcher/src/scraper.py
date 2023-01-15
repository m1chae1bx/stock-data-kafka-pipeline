"""Provides functions to scrape stock data from PSE website."""

import logging

import requests
from bs4 import BeautifulSoup
from requests import HTTPError, JSONDecodeError
from src.custom_types import StockData, StockDataFetchingError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_stock_data_point(soup: BeautifulSoup, label: str) -> str:
    """
    Get stock data point from soup object with the following format:
    <th>label</th><td>value</td>
    """
    th_element = soup.find("th", string=label)
    if th_element is None:
        logging.error("Label %s not found", label)
        raise StockDataFetchingError()

    td_element = th_element.find_next_sibling("td")
    if td_element is None:
        logging.error("Value for label %s not found", label)
        raise StockDataFetchingError()

    value = td_element.text.strip()

    return value


def fetch_company_id(stock_symbol: str) -> int:
    """Fetch company ID from PSE website based on stock symbol"""
    try:
        search_url = (
            "https://edge.pse.com.ph/autoComplete/"
            + f"searchCompanyNameSymbol.ax?term={stock_symbol}"
        )
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        company_id = int(response.json()[0]["cmpyId"])

        return company_id
    except (HTTPError, JSONDecodeError) as exc:
        logging.exception("Error fetching company ID of %s", stock_symbol)
        raise StockDataFetchingError(f"Error fetching company ID of {stock_symbol}") from exc


def fetch_stock_data_soup(company_id: int) -> BeautifulSoup:
    """Fetch stock data from PSE website"""
    stock_data_url = f"https://edge.pse.com.ph/companyPage/stockData.do?cmpy_id={company_id}"
    try:
        response = requests.get(stock_data_url, timeout=10)
        response.raise_for_status()

        return BeautifulSoup(response.text, "html.parser")
    except HTTPError as exc:
        logging.exception("Error fetching stock data of company ID %s", company_id)
        raise StockDataFetchingError(
            f"Error fetching stock data of company ID {company_id}"
        ) from exc


def scrape_stock_data(stock_symbol: str) -> StockData:
    """Scrape stock data from PSE website"""
    logging.debug("Scraping stock data for %s...", stock_symbol)
    try:
        company_id = fetch_company_id(stock_symbol)
        soup = fetch_stock_data_soup(company_id)
        stock_data: StockData = {
            "stock": stock_symbol,
            "close": get_stock_data_point(soup, "Last Traded Price"),
            "open": get_stock_data_point(soup, "Open"),
            "high": get_stock_data_point(soup, "High"),
            "low": get_stock_data_point(soup, "Low"),
            "volume": get_stock_data_point(soup, "Volume"),
        }

        return stock_data
    except StockDataFetchingError as exc:
        logging.exception("Error scraping stock data of %s", stock_symbol)
        raise exc
