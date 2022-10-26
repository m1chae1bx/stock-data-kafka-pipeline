"""Provides functions to scrape stock data from PSE website."""

import locale

import requests
from bs4 import BeautifulSoup

from model import StockData


def get_close(soup: BeautifulSoup) -> float | str:
    """Get close price of stock from soup object"""
    try:
        close_price_th = soup.find("th", text="Last Traded Price")
        if close_price_th is None:
            raise RuntimeError("Element th not found")

        close_price_td = close_price_th.find_next_sibling("td")
        if close_price_td is None:
            raise RuntimeError("Sibling element td not found")

        close_price_text = close_price_td.text.strip()
        if close_price_text == "":
            return "N/A"

        close_price = float(locale.atof(close_price_text))

        return close_price
    except Exception as exc:
        print(exc)
        raise RuntimeError("Error parsing closing price") from exc


def get_open(soup: BeautifulSoup) -> float | str:
    """Get open price of stock from soup object"""
    try:
        open_price_th = soup.find("th", text="Open")
        if open_price_th is None:
            raise RuntimeError("Element th not found")

        open_price_td = open_price_th.find_next_sibling("td")
        if open_price_td is None:
            raise RuntimeError("Sibling element td not found")

        open_price_text = open_price_td.text.strip()
        if open_price_text == "":
            return "N/A"

        open_price = float(locale.atof(open_price_text))

        return open_price
    except Exception as exc:
        print(exc)
        raise RuntimeError("Error parsing opening price") from exc


def get_high(soup: BeautifulSoup) -> float | str:
    """Get high price of stock from soup object"""
    try:
        high_price_th = soup.find("th", text="High")
        if high_price_th is None:
            raise RuntimeError("Element th not found")

        high_price_td = high_price_th.find_next_sibling("td")
        if high_price_td is None:
            raise RuntimeError("Sibling element td not found")

        high_price_text = high_price_td.text.strip()
        if high_price_text == "":
            return "N/A"

        high_price = float(locale.atof(high_price_text))

        return high_price
    except Exception as exc:
        print(exc)
        raise RuntimeError("Error parsing highest price") from exc


def get_low(soup: BeautifulSoup) -> float | str:
    """Get low price of stock from soup object"""
    try:
        low_price_th = soup.find("th", text="Low")
        if low_price_th is None:
            raise RuntimeError("Element th not found")

        low_price_td = low_price_th.find_next_sibling("td")
        if low_price_td is None:
            raise RuntimeError("Sibling element td not found")

        low_price_text = low_price_td.text.strip()
        if low_price_text == "":
            return "N/A"

        low_price = float(locale.atof(low_price_text))

        return low_price
    except Exception as exc:
        print(exc)
        raise RuntimeError("Error parsing lowest price") from exc


def get_volume(soup: BeautifulSoup) -> int | str:
    """Get volume of stock from soup object"""
    try:
        volume_th = soup.find("th", text="Volume")
        if volume_th is None:
            raise RuntimeError("Element th not found")

        volume_td = volume_th.find_next_sibling("td")
        if volume_td is None:
            raise RuntimeError("Sibling element td not found")

        volume_text = volume_td.text.strip()
        if volume_text == "":
            return "N/A"

        volume = int(locale.atoi(volume_text))

        return volume
    except Exception as exc:
        print(exc)
        raise RuntimeError("Error parsing volume") from exc


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
    except Exception as exc:
        print(exc)
        raise RuntimeError(
            f"Error fetching company ID from stock symbol {stock_symbol}"
        ) from exc


def fetch_stock_data_soup(company_id: int) -> BeautifulSoup:
    """Fetch stock data from PSE website"""
    stock_data_url = (
        f"https://edge.pse.com.ph/companyPage/stockData.do?cmpy_id={company_id}"
    )
    try:
        response = requests.get(stock_data_url, timeout=10)
        response.raise_for_status()

        return BeautifulSoup(response.text, "html.parser")
    except Exception as exc:
        print(exc)
        raise RuntimeError(f"Request to {stock_data_url} failed") from exc


def scrape_stock_data(stock_symbol: str) -> StockData:
    """Scrape stock data from PSE website"""
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    try:
        company_id = fetch_company_id(stock_symbol)
        soup = fetch_stock_data_soup(company_id)
        stock_data: StockData = {
            "stock": stock_symbol,
            "close": get_close(soup),
            "open": get_open(soup),
            "high": get_high(soup),
            "low": get_low(soup),
            "volume": get_volume(soup),
        }

        return stock_data
    except Exception as exc:
        print(exc)
        raise RuntimeError(
            f"Error scraping stock data for {stock_symbol}"
        ) from exc
