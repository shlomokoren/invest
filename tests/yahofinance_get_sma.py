import os

import yfinance as yf
from datetime import datetime, timedelta
import os
import sys

def yahoo_finance_get_stock_values(ticker):
    try:

        # Fetch historical data for the last 1 year
        stock_data = yf.download(ticker, period="1y",progress=False)

        # Check if data is fetched successfully
        if stock_data.empty:
            retcode = 1
            funcmessage = f"No data returned for {ticker}. Please check the ticker symbol."
            return {"retcode": retcode, "funcmessage": funcmessage}

        # Calculate the 150-day moving average
        stock_data['150_SMA'] = stock_data['Close'].rolling(window=150).mean()

        # Get the latest value of the 150-day moving average (current)
        currentsma150 = stock_data['150_SMA'].iloc[-1]

        # Get the value of the 150-day moving average a week ago
        week_ago_date = datetime.now() - timedelta(days=7)
        weekagosma150 = stock_data['150_SMA'].loc[stock_data.index <= week_ago_date].iloc[-1]

        # Get the value of the 150-day moving average two weeks ago
        two_weeks_ago_date = datetime.now() - timedelta(days=14)
        twoweekagosma150 = stock_data['150_SMA'].loc[stock_data.index <= two_weeks_ago_date].iloc[-1]

        # Get the latest closing price
        closedPrice = stock_data['Close'].iloc[-1]
        openPrice = stock_data['Open'].iloc[-1]
        highPrice = stock_data['High'].iloc[-1]
        lowPrice = stock_data['Low'].iloc[-1]
        volume = stock_data['Volume'].iloc[-1]

        # Return the results in a dictionary with success code and message
        retcode = 0
        funcmessage = "success"
        return {
            "retcode": retcode,
            "funcmessage": funcmessage,
            "currentsma150": currentsma150,
            "weekagosma150": weekagosma150,
            "twoweekagosma150": twoweekagosma150,
            "closedPrice": closedPrice,
            "openPrice": openPrice,
            "highPrice": highPrice,
            "lowPrice": lowPrice,
            "volume": volume

        }

    except Exception as e:
        # Handle errors and return an error code and message
        retcode = 2
        funcmessage = f"Error fetching data for {ticker}: {e}"
        return {"retcode": retcode, "funcmessage": funcmessage}

# Example usage:
yahoostockobj = yahoo_finance_get_stock_values("MSI")
print(yahoostockobj)
