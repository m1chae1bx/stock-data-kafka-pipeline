"""Provides functions to scrape stock data from PSE website."""

import locale

import requests
from bs4 import BeautifulSoup


def get_close(soup):
    """Get close price of stock from soup object"""
    try:
        close_price = (
            soup.find("th", text="Last Traded Price")
            .find_next_sibling("td")
            .text.strip()
        )
        return float(locale.atof(close_price))
    except Exception as exc:
        raise RuntimeError("Error parsing closing price") from exc


def get_open(soup):
    """Get open price of stock from soup object"""
    try:
        open_price = (
            soup.find("th", text="Open").find_next_sibling("td").text.strip()
        )
        return float(locale.atof(open_price))
    except Exception as exc:
        raise RuntimeError("Error parsing opening price") from exc


def get_high(soup):
    """Get high price of stock from soup object"""
    try:
        high_price = (
            soup.find("th", text="High").find_next_sibling("td").text.strip()
        )
        return float(locale.atof(high_price))
    except Exception as exc:
        raise RuntimeError("Error parsing high price") from exc


def get_low(soup):
    """Get low price of stock from soup object"""
    try:
        low_price = (
            soup.find("th", text="Low").find_next_sibling("td").text.strip()
        )
        return float(locale.atof(low_price))
    except Exception as exc:
        raise RuntimeError("Error parsing low price") from exc


def get_volume(soup):
    """Get volume of stock from soup object"""
    try:
        volume = (
            soup.find("th", text="Volume").find_next_sibling("td").text.strip()
        )
        return int(locale.atoi(volume))
    except Exception as exc:
        raise RuntimeError("Error parsing volume") from exc


def fetch_company_id(stock_symbol):
    """Fetch company ID from PSE website based on stock symbol"""
    try:
        search_url = (
            "https://edge.pse.com.ph/autoComplete/"
            + f"searchCompanyNameSymbol.ax?term={stock_symbol}"
        )
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        cmpy_id = response.json()[0]["cmpyId"]
        return cmpy_id
    except Exception as exc:
        raise RuntimeError(
            f"Error fetching cmpyID from stock symbol {stock_symbol}"
        ) from exc


def fetch_stock_data_soup(cmpy_id):
    """Fetch stock data from PSE website"""
    stock_data_url = (
        f"https://edge.pse.com.ph/companyPage/stockData.do?cmpy_id={cmpy_id}"
    )
    try:
        response = requests.get(stock_data_url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as exc:
        raise RuntimeError(f"Request to {stock_data_url} failed") from exc


def scrape_stock_data(stock_symbol):
    """Scrape stock data from PSE website"""
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    try:
        cmpy_id = fetch_company_id(stock_symbol)
        soup = fetch_stock_data_soup(cmpy_id)
        stock_data = {
            "stock": stock_symbol,
            "close": get_close(soup),
            "open": get_open(soup),
            "high": get_high(soup),
            "low": get_low(soup),
            "volume": get_volume(soup),
        }
        return stock_data
    except Exception as exc:
        raise RuntimeError(
            f"Error scraping stock data for {stock_symbol}"
        ) from exc
