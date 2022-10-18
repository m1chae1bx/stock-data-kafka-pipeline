from bs4 import BeautifulSoup
import requests
import locale

def get_close(soup):
    close_th = soup.find("th", text="Last Traded Price")
    close_td = close_th.find_next_sibling("td") if close_th else None
    return float(locale.atof(close_td.text.strip())) if close_td else None

def get_open(soup):
    open_th = soup.find("th", text="Open")
    open_td = open_th.find_next_sibling("td") if open_th else None
    return float(locale.atof(open_td.text.strip())) if open_td else None

def get_high(soup):
    high_th = soup.find("th", text="High")
    high_td = high_th.find_next_sibling("td") if high_th else None
    return float(locale.atof(high_td.text.strip())) if high_td else None

def get_low(soup):
    low_th = soup.find("th", text="Low")
    low_td = low_th.find_next_sibling("td") if low_th else None
    return float(locale.atof(low_td.text.strip())) if low_td else None

def get_volume(soup):
    volume_th = soup.find("th", text="Volume")
    volume_td = volume_th.find_next_sibling("td") if volume_th else None
    return int(locale.atoi(volume_td.text.strip())) if volume_td else None

def scrape_stock_data(stock):
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    search_url = f"https://edge.pse.com.ph/autoComplete/searchCompanyNameSymbol.ax?term={stock}"
    response = requests.get(search_url)

    if response.ok:
        cmpy_id = response.json()[0]["cmpyId"]
        stock_data_url = f"https://edge.pse.com.ph/companyPage/stockData.do?cmpy_id={cmpy_id}"
        response = requests.get(stock_data_url)

        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            close = get_close(soup)
            if not close:
                raise Exception(f"Error parsing closing price")
            open = get_open(soup)
            if not open:
                raise Exception(f"Error parsing opening price")
            high = get_high(soup)
            if not high:
                raise Exception(f"Error parsing high price")
            low = get_low(soup)
            if not low:
                raise Exception(f"Error parsing low price")
            volume = get_volume(soup)
            if not volume:
                raise Exception(f"Error parsing volume")

            stock = {
                "stock": stock,
                "close": close,
                "open": open,
                "high": high,
                "low": low,
                "volume": volume
            }
            return stock
        else:
            raise Exception(f"Error getting stock data for {stock} from PSE", response.status_code)
    else:
        raise Exception(f"Stock symbol {stock} not found")




