from ib_insync import *
from datetime import datetime


def is_nasdaq_open():
    # Connect to IBKR API
    ib = IB()

    try:
        print("Connecting to TWS...")
        ib.connect('127.0.0.1', 7497, clientId=1)  # TWS port

        # Define a NASDAQ stock (e.g., AAPL is a NASDAQ-listed stock)
        stock = Stock('AAPL', 'SMART', 'USD')

        # Request market data for the stock
        market_data = ib.reqMktData(stock, '', False, False)

        # Sleep for a short time to allow data retrieval
        ib.sleep(2)

        # Get current time and last updated time
        last_time = market_data.time

        if last_time:
            # Get the current system time
            current_time = datetime.now()

            # If the last update was today, market is likely open
            if last_time.date() == current_time.date():
                print(f"NASDAQ is open. Last data update: {last_time}")
                return True
            else:
                print(f"NASDAQ is closed. Last data update: {last_time}")
                return False
        else:
            print("Market data not available. Assuming NASDAQ is closed.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

    finally:
        # Disconnect from IBKR
        ib.disconnect()
        print("Disconnected from TWS.")


# Check if NASDAQ is open
if is_nasdaq_open():
    print("NASDAQ is currently open.")
else:
    print("NASDAQ is currently closed.")
