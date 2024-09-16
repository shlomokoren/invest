from ib_insync import *
import sys

def TWSMarketorder(symbol,Orderaction,totaQuatity):
    returnResult ={"functionStatus": True,"message": ""}
    try:
        # Connect to IBKR API
        ib = IB()
        print("Connecting to TWS...")
        ib.connect('127.0.0.1', 7497, clientId=1)  # Use 7497 for TWS, 7496 for IB Gateway
        print("Connected to TWS successfully.")

    except ConnectionRefusedError:
        msg = "Error: Could not connect to TWS. Make sure it's running and the API is enabled."
        print(msg)
        returnResult = {"functionStatus": False, "message": msg}
        return returnResult
    except Exception as e:
        msg = f"Unexpected error: {e}"
        print(msg)
        returnResult = {"functionStatus": False, "message": msg}
        return returnResult
        # Define the stock you want to buy
    try:
        stock = Stock(symbol, 'SMART', 'USD')
        # Create a market order
        order = MarketOrder(Orderaction, totaQuatity)

        # Place the order
        print("Placing order...")
        trade = ib.placeOrder(stock, order)

        # Wait until the order is placed or updated
        ib.sleep(5)
        # Check if the order is filled or failed
        if trade.orderStatus.status == 'Filled':
            msg = "Order {Orderaction} successfully filled."
            print(msg)
            returnResult = {"functionStatus": True, "message": msg}
        else:
            msg = f"Order Status: {trade.orderStatus.status}"
            print(msg)
            returnResult = {"functionStatus": False, "message": msg}
    except Exception as order_error:
            msg = f"Error during order placement: {order_error}"
            print(msg)
            returnResult = {"functionStatus": False, "message": msg}

    # Disconnect from IBKR
    ib.disconnect()
    print("Disconnected from TWS.")
    return returnResult


result = TWSMarketorder('AAPL','BUY',10)
print(result["functionStatus"])
print(result["message"])
