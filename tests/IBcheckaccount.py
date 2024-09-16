from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper
from ibapi.common import *  # @UnusedWildImport
from ibapi.contract import Contract

import threading
import time


class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    @iswrapper
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        """Handles account summary responses"""
        if tag == "AccountType":
            print(f"Account ID: {account}")
            print(f"Account Type: {value}")

    def accountSummaryEnd(self, reqId: int):
        print("Account summary request finished.")
        self.disconnect()


def run_loop():
    app.run()


if __name__ == "__main__":
    app = IBApi()

    # Connect to TWS or IB Gateway (localhost:7497 for TWS, 4002 for IB Gateway)
    app.connect("127.0.0.1", 7497, clientId=1)

    # Start the socket thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Give it some time to connect
    time.sleep(1)

    # Request account summary. 9001 is a random request ID
    app.reqAccountSummary(9001, "All", "AccountType")

    # Let the API request finish
    time.sleep(5)