import json
from pickle import FALSE
import logging
import inspect
import requests
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from ib_insync import *
import yfinance as yf
from datetime import datetime, timedelta


def yahoo_finance_get_stock_values(ticker,range):
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    try:
        # Fetch historical data for the last 1 year
        stock_data = yf.download(ticker, period="1y",progress=False)

        # Check if data is fetched successfully
        if stock_data.empty:
            retcode = 1
            retmessage = f"No data returned for {ticker}. Please check the ticker symbol."
            return {"retcode": retcode, "retmessage": retmessage}

        # Calculate the range-day moving average
        stock_data['SMA'] = stock_data['Close'].rolling(window=range).mean()

        # Get the latest value of the range-day moving average (current)
        currentsma = stock_data['SMA'].iloc[-1]

        # Get the value of the range-day moving average a week ago
        week_ago_date = datetime.now() - timedelta(days=7)
        weekagosma = stock_data['SMA'].loc[stock_data.index <= week_ago_date].iloc[-1]

        # Get the value of the range-day moving average two weeks ago
        two_weeks_ago_date = datetime.now() - timedelta(days=14)
        twoweekagosma = stock_data['SMA'].loc[stock_data.index <= two_weeks_ago_date].iloc[-1]

        # Get the latest closing price
        closePrice = stock_data['Close'].iloc[-1]
        openPrice = stock_data['Open'].iloc[-1]
        highPrice = stock_data['High'].iloc[-1]
        lowPrice = stock_data['Low'].iloc[-1]
        volume = stock_data['Volume'].iloc[-1]

        # Return the results in a dictionary with success code and message
        retcode = 0
        retmessage = "success"
        return {
            "retcode": retcode,
            "retcmessage": retmessage,
            "currentsma": round(currentsma,2),
            "weekagosma": round(weekagosma,2),
            "twoweekagosma": round(twoweekagosma,2),
            "closePrice": round(closePrice,2),
            "openPrice": round(openPrice,2),
            "highPrice": round(highPrice,2),
            "lowPrice": round(lowPrice,2),
            "volume": round(volume,2)

        }

    except Exception as e:
        # Handle errors and return an error code and message
        retcode = 2
        funcmessage = f"Error fetching data for {ticker}: {e}"
        return {"retcode": retcode, "funcmessage": funcmessage}

ticker = 'MSI'
tickerobj = yahoo_finance_get_stock_values(ticker,200)
print(tickerobj)