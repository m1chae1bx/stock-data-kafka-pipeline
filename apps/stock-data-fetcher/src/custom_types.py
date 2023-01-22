"""Provides class to represent stock data."""

from typing import TypedDict


class StockData(TypedDict):
    """Represents stock data"""

    stock: str
    close: float | str
    open: float | str
    high: float | str
    low: float | str
    volume: int | str


class StockDataFetchingError(Exception):
    """Custom exception class for stock data fetching error"""
