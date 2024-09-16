from ib_insync import *
import pytz
import datetime

# Set time zone explicitly
timezone = pytz.timezone('Asia/Jerusalem')
current_time = datetime.datetime.now(timezone)
print(f"Current time: {current_time}")



# Connect to IBKR API
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Use 7497 for TWS, 7496 for Gateway

# Define the stock you want to sell
stock = Stock('AAPL', 'SMART', 'USD')

# Fetch the current market data for the stock
ib.qualifyContracts(stock)
market_data = ib.reqMktData(stock)

# Wait for the market data to be populated
ib.sleep(1)

# Get the current price (using the midpoint or last price as an example)
current_price = (market_data.bid + market_data.ask) / 2 if market_data.bid and market_data.ask else market_data.last
print(f"Current Price: {current_price}")

# Calculate the limit price (1% above the current price)
limit_price = current_price * 1.02
print(f"Limit Price (1% above current price): {limit_price}")

# Create a limit sell order
order = LimitOrder('SELL', 10, limit_price)  # Sell 10 shares with 1% limit above current price

# Place the sell order
trade = ib.placeOrder(stock, order)

# Wait until the order is placed
ib.sleep(2)
print(f"Order Status: {trade.orderStatus.status}")

# Disconnect from IBKR
ib.disconnect()
