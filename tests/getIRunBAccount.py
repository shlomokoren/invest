from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time


class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        """Handles account summary responses"""
        if tag == "AccountType":
            print(f"Account ID: {account}")
            print(f"Account Type: {value}")

    def accountSummaryEnd(self, reqId: int):
        print("Account summary request finished.")
        self.disconnect()

    def tickPrice(self, reqId: int, tickType: int, price: float, attrib):
        """Handles market data responses for price"""
        if tickType == 4:  # TickType 4 corresponds to LAST price
            print(f"Current market price of MSFT: {price}")
            self.disconnect()


def run_loop():
    app.run()


def create_stock_contract(symbol: str):
    """Creates a contract object for the stock symbol (MSFT in this case)"""
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    return contract


if __name__ == "__main__":
    app = IBApi()

    # Connect to TWS or IB Gateway
    app.connect("127.0.0.1", 7497, clientId=1)

    # Start the socket thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Give it some time to connect
    time.sleep(1)

    # Request account summary
    app.reqAccountSummary(9001, "All", "AccountType")

    # Request market data for MSFT
    msft_contract = create_stock_contract("MSFT")
    app.reqMktData(9002, msft_contract, "", False, False, [])

    # Allow time for market data to be returned
    time.sleep(5)
