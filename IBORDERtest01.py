from ib_insync import *


def TWSMarketorder(ib, symbol, Orderaction, totalQuatity):
    returnResult = {"retStatus": "", "message": ""}
    msg = "IBTWS action="+Orderaction + " symbol="+symbol + " quatity="+str(totalQuatity)+", "
    try:
        stock = Stock(symbol, 'SMART', 'USD')
        # Create a market order
        order = MarketOrder(Orderaction, totalQuatity)

        # Place the order
        print("Placing order...")
        trade = ib.placeOrder(stock, order)

        # Wait until the order is placed or updated
        ib.sleep(5)
        # Check if the order is filled or failed
        if trade.orderStatus.status == 'Filled':
            msg = msg+"Order {Orderaction} successfully filled. portfolio is automatic updated"
            print(msg)
            returnResult = {"retStatus": 'Filled', "message": msg}
        else:
            msg = f"Order Status is {trade.orderStatus.status} you have to update portfolio manual."
            print(msg)
            returnResult = {"retStatus": trade.orderStatus.status, "message": msg}
    except Exception as order_error:
        msg = msg + f"Error during order placement: {order_error}"
        print(msg)
        returnResult = {"retStatus": "error", "message": msg}
    return returnResult

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Use 7496 for IB Gateway, 7497 for TWS
# Define the stock you want to buy
stock = Stock('AAPL', 'SMART', 'USD')
# Create a market order
order = MarketOrder('SELL', 10)  # SELL 10 shares of AAPL
symbol = "LULU"
Orderaction = "BUY"
totalQuatity = 10
TWSMarketorder(ib, symbol, Orderaction, totalQuatity)
ib.disconnect()
