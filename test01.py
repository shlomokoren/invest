import yfinance as yf
try:
   # Fetch historical data for the last 1 year
   ticker = 'GOOG'
   stock_data = yf.download(ticker, period="1y",progress=False)
   print(len(stock_data))
   if stock_data.empty:
        print("stock_data is empty")
except Exception as e:
     print(e)
