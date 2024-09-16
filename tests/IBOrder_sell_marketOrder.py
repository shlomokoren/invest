from ib_insync import *

# Connect to IBKR API
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Use 7496 for IB Gateway, 7497 for TWS
# Define the stock you want to buy
stock = Stock('AAPL', 'SMART', 'USD')
# Create a market order
order = MarketOrder('SELL', 10)  # SELL 10 shares of AAPL

# Place the order
trade = ib.placeOrder(stock, order)

# Wait until the order is filled
ib.sleep(2)
print(f"Order Status: {trade.orderStatus.status}")

# Disconnect from IBKR
ib.disconnect()

