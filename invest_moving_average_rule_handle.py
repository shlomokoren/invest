import json
import logging
import inspect
import time

import requests
import os
import gspread
from google.oauth2.service_account import Credentials
from ib_insync import *
import yfinance as yf
from datetime import datetime, timedelta
import socket

from playhouse.sqlite_udf import hostname

#from datetime import datetime
#from datetime import datetime
#from pandas.core.computation.common import result_type_many

debug = False
__version__ = "0.0.8beta"
print("script version: " + __version__)


def get_general_parameters():
    ''' reade global parameters from general_parameters.json '''
    global enableLogFile, enableSendTelgram, enableGoogleSheetUpdate
    global smapercentagedifference, updateBuySellInInputFile, fixedInvestmentBuyAmount
    global TWSaccount,TWSEnable
    global isNeedToCheckTakeProfit
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    filename = "general_parameters.json"
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        for item in data:
            if 'enableLogFile' in item:
                enableLogFile = item['enableLogFile']
                print("send to log is " + str(enableLogFile))
            elif 'enableSendTelgram' in item:
                enableSendTelgram = item['enableSendTelgram']
                print("send alerts to telegram  is " + str(enableSendTelgram))
            elif 'enableGoogleSheetUpdate' in item:
                enableGoogleSheetUpdate = item['enableGoogleSheetUpdate']
                print("send info to googesheet is "+str(enableGoogleSheetUpdate))
            elif 'smapercentagedifference' in item:
                smapercentagedifference = item['smapercentagedifference']
                print("range from sma that allow actions in % is " + str(smapercentagedifference))
            elif 'updateBuySellInInputFile' in item:
                updateBuySellInInputFile = item['updateBuySellInInputFile']
                print("enable change values automatic in input file is "+str(updateBuySellInInputFile))
            elif 'fixedInvestmentBuyAmount' in item:
                fixedInvestmentBuyAmount = item['fixedInvestmentBuyAmount']
                print("total price for buy command is " + str(fixedInvestmentBuyAmount))
            elif 'TWSaccount' in item:
                TWSaccount = item['TWSaccount']
                print("IB Broker Account is "+ TWSaccount)
            elif 'TWSEnable' in item:
                TWSEnable = item['TWSEnable']
                print("use IBbroker to buy or sell in market is "+ str(TWSEnable))
            elif 'isNeedToCheckTakeProfit' in item:
                isNeedToCheckTakeProfit = item['isNeedToCheckTakeProfit']
                print("Is Need To Check Take Profit  is  "+str(isNeedToCheckTakeProfit))

    except FileNotFoundError:
        print(f"Error: The file '{investDataFile}' was not found.")

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


def TWSMarketorder(ib, symbol, Orderaction, totalQuantity):
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    returnResult = {"retStatus": "", "message": ""}
    msg = "IBTWS action=" + Orderaction + " symbol=" + symbol + " quatity=" + str(totalQuantity) + ", "
    try:
        stock = Stock(symbol, 'SMART', 'USD')
        # Create a market order
        order = MarketOrder(Orderaction, totalQuantity)

        # Place the order
        print(f"Placing order {symbol} {Orderaction} {totalQuantity}")
        trade = ib.placeOrder(stock, order)

        # Wait until the order is placed or updated
        ib.sleep(5)
        # Check if the order is filled or failed
        if (trade.orderStatus.status == 'Filled') :
            sellPrice = trade.orderStatus.avgFillPrice
            msg = msg + "Order {Orderaction} successfully filled. average sell price is "+str(sellPrice)+" , portfolio is automatic updated"
            returnResult = {"retStatus": 'Filled', "message": msg}
        else:
            msg =  msg +  f"Order Status is {trade.orderStatus.status} you have to update portfolio manual."
            returnResult = {"retStatus": trade.orderStatus.status, "message": msg}
    except Exception as order_error:
        msg = msg + f"Error during order placement: {order_error}"
        returnResult = {"retStatus": "error", "message": msg}
    return returnResult
def notifyCenter(message, googleSheetsRaw, sheetColnotes, color_flag_bool):
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")
    print(message)
    sendtelegrammsg(message)
    writeToLogfile(message)
    googleSheetsRaw.append(sheetColnotes)
    googlesheets_add_history([googleSheetsRaw], color_flag=color_flag_bool)


def update_stocks_input_list(portfolioChangesList):
    ''' after all checks all recommendations are in replaceValueList
      this function sell/buy  use IBTWS and  update input stocks file after the transaction
      '''
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    global fixedInvestmentBuyAmount,enableTakeProfit
    ##//check if nasdaq is open
    ## if nasdaq is open connect tws
    ib = None
    try:
        # Connect to IBKR API
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1)  # Use 7497 for TWS, 7496 for IB Gateway
        print("Connected to TWS successfully.")

    except ConnectionRefusedError:
        msg = "Could not update portfolio .Error: Could not connect to TWS. Make sure it's running and the API is enabled."
        print(msg)
        returnResult = {"retStatus": False, "message": msg}
        return returnResult
    except Exception as e:
        msg = f"ib.connect Unexpected error: {e}"
        print(msg)
        returnResult = {"retStatus": False, "message": msg}
        return returnResult

        # Request account summary
    account_summary = ib.accountSummary()
    isTradeAllowed = False
    currentTWSAccount = account_summary[0].account
    for summary in account_summary:
        if summary.account == TWSaccount:
            isTradeAllowed = True
    if isTradeAllowed == False:
        msg = "Failed to run in IB TWS software. TWS use account "+ currentTWSAccount +" allowed account  " + TWSaccount
        print(msg)
        returnResult = {"retStatus": False, "message": msg}
        return returnResult

    
        # Define the stock you want to buy
    with open(investDataFile, 'r') as file:
        symbols_input_list = json.load(file)
        for item in portfolioChangesList:
            for record in symbols_input_list:
                symbol = record["symbol"]
                action = record['action']
                range = int(record['range'])
                account = record['account']
           ##     account = record['account']
                sma = item['smObj']['sma']
                closedPrice = item['smObj']['closed']
                if symbol == item['stock']['symbol']:
                    googleSheetsRaw = [symbol, action, 'sma' + str(range), int(sma),closedPrice, "",account]
                    if account == TWSaccount:
                        if (item['change_action'] == 'sellToBuy') and (record['action'] == 'sell'):
                            if 'isNeedToCheckTakeProfit' in record:
                                record['isNeedToCheckTakeProfit'] = False
                            quantity = int(record["quantity"])
                            result = TWSMarketorder(ib,record["symbol"], "SELL", quantity)
                            if result["retStatus"] == 'Filled':
                                record['action'] = 'buy'
                                notifyCenter(result["message"],googleSheetsRaw,result["message"],True)
                            else:
                                notifyCenter(result["message"],googleSheetsRaw, result["message"],True)
                        elif (item['change_action'] == 'buyToSell') and (record['action'] == 'buy'):
                            quantity = int(fixedInvestmentBuyAmount / closedPrice)
                            result = TWSMarketorder(ib,record["symbol"], "BUY", quantity)
                            notifyCenter(result["message"], googleSheetsRaw, result["message"], True)
                            if result["retStatus"] == 'Filled':
                                record['action'] = 'sell'
                                record["quantity"] = quantity
                        elif (item['change_action'] == 'disableTakeProfit') and (record['action'] == 'sell'):
                            record['isNeedToCheckTakeProfit'] = False
                            quantity = int(record["quantity"] / 3)
                            result = TWSMarketorder(ib,record["symbol"], "SELL", quantity)
                            notifyCenter(result["message"], googleSheetsRaw, result["message"], True)
                            if (result["retStatus"] == 'Filled') :              #or(result["retStatus"] == 'PreSubmitted')
                                record["quantity"] = int(record["quantity"]) - quantity
                                notifyCenter(result["message"],googleSheetsRaw,result["message"],True)

    if ib.isConnected():
        ib.disconnect()

    with open(investDataFile, 'w') as file:
        json.dump(symbols_input_list, file, indent=4)  # Write the updated symbols to the file
    msg = "portfolio file was update . please take attention for manual update."
    result = {"retStatus": False, "message": msg}
    return(result)

def percentage_difference(closedvalue, smavalue):
    # Calculate the percentage difference
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    percentage_difference = ((closedvalue - smavalue) / closedvalue) * 100
    formatted_percentage_difference = "{:.2f}".format(percentage_difference)
    # Print the result
    return (formatted_percentage_difference)

def is_need_buy(smaValue, closedValue, percentagedifference):
    ''' check if need to buy
     check if stock moving average  trand is up
     check if price is above average and it is not far from average
    '''
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")


    global smapercentagedifference
    result = False
    if (smaValue < closedValue):
        if abs(float(percentagedifference)) <= smapercentagedifference:
            result = True
            return result
    return result

def is_need_sell(closedValue, smaValue):
    '''
    check if need to sell and stoploss is moving average value
    :param closedValue:
    :param smaValue:
    :return:
    '''
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")


    result = False
    if (smaValue >= closedValue):
        result = True
        return result
    return result

def sendtelegrammsg(message):
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    global enableSendTelgram
    if enableSendTelgram is True:
        # Replace 'your_bot_token' with your bot's token
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        # Replace 'your_chat_id' with the chat ID or the recipient's user ID
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # The message you want to send

        # Telegram API URL for sending messages
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

        # Parameters for the API request
        params = {
            'chat_id': chat_id,
            'text': message
        }

        # Send the message
        response = requests.get(url, params=params)

        # Check if the message was sent successfully
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print("Failed to send message.")

def writeToLogfile(line):
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    global enableLogFile
    if enableLogFile is True:
        # Get the current date and time
        now = datetime.now()
        # Format it as a string
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        logfile_path = str(os.getenv("INVEST_LOGFILE"))
        # Open the file in append mode ('a')
        with open(logfile_path, "a") as logfile:
            # Write a line to the log file
            logfile.write(current_time + "," + line + " \n")

def googlesheets_add_history(symbolsList, color_flag=False):
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    global enableGoogleSheetUpdate

    if enableGoogleSheetUpdate is True:
        spreadsheet = None
        try:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            credentials = Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"]
            )
            # Authorize and create a client
            client = gspread.authorize(credentials)
            # Open the Google Sheet by name
            spreadsheet = client.open("invest_portfolio")
            # Check if the "history" sheet exists, if not create it
        except Exception as e:
            print("fail to open sheet invest_portfolio")
            print(f"An error exception is: {e}")
            return

        try:
            worksheet = spreadsheet.worksheet("investHistoryCommands")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="investHistoryCommands", rows="500", cols="30")

        attempt = 1
        max_attempts = 3  # Retry a few times if needed
        success = False
        while attempt <= max_attempts and not success:
            try:
                # Check if the first row is empty (i.e., if the sheet is new)
                if not worksheet.cell(1, 1).value:
                    # Add title row
                    title_row = ["Date", "Symbol", "Action", "Indecator", "Indicator Value", "Closed", "difference %", "account","host" ,"Notes"]
                    worksheet.update(range_name='A1:J1', values=[title_row])
            except gspread.exceptions.APIError as e:
                logging.error(f"APIError during if not worksheet.cell on attempt {attempt}: {e}")
                if attempt < max_attempts:
                   logging.info("Retrying after 60 seconds...")
                   time.sleep(60)
                   attempt += 1
                else:
                   logging.error("Max retry attempts reached. Failed to if not worksheet.cell.")
                   print("Max retry attempts reached. Failed to if not worksheet.cell.")
                   return


        # Get the current date
        current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        hostname = socket.gethostname()
        # Append the current date to each row and add to the "history" sheet
        for row in symbolsList:
            row.insert(0, current_date)
            row.append(hostname)
            attempt = 1
            max_attempts = 3  # Retry a few times if needed
            success = False

            while attempt <= max_attempts and not success:
                try:
                    logging.debug(f"Attempt {attempt}: {row}")
                    result = worksheet.append_row(row)
                    success = True  # If no exception is raised, set success to True
                except gspread.exceptions.APIError as e:
                    logging.error(f"APIError during append_row on attempt {attempt}: {e}")
                    if attempt < max_attempts:
                        logging.info("Retrying after 60 seconds...")
                        time.sleep(60)
                        attempt += 1
                    else:
                        logging.error("Max retry attempts reached. Failed to append row.")
                        print("Max retry attempts reached. Failed to append row.")
                        return
                except Exception as e:
                    logging.error(f"An unexpected error occurred: {e}")
                    print(f"An unexpected error occurred: {e}")
                    return  # Exit on any other exception

            if color_flag:
                range = str(result['updates']['updatedRange']).split("!")[1]
                # Apply background color to the newly added rows
                worksheet.format(ranges=range, format={
                    "backgroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 0.0
                    }
                })
        try:
            worksheet.sort((1, 'des'))
        except gspread.exceptions.APIError as e:
            logging.debug(f"An unexpected error occurred  worksheet.sort: {e}")
            print(f"An unexpected error occurred  worksheet.sort : {e}")
            time.sleep(60)
            logging.debug("retry google  worksheet.sort")
            worksheet.sort((1, 'des'))

def maRule(stockObj):
    '''
    The `maRule` function handles the logic for the moving average rule.
    It evaluates whether a buy or sell action is required, and if so, generates a result object containing the necessary details to manage the operation.
    Input parameters: stock object
        The stock object includes properties such as symbol, range, account, and other relevant parameters defined in the `data_invest.json` file.
    :input stock object as configured in list input json file
    :return: mapkey symbol : buyToSell/SellToBuy
    '''

    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_code.co_name
    logging.debug(f"Running function: {current_function}()")

    symbol = stockObj["symbol"]
    smarange  = int(stockObj["range"])
    action = stockObj["action"]
    account = stockObj["account"]
    disableTakeProfit = False
    takeProfitPercentage = 1000
    if "isNeedToCheckTakeProfit" in stockObj:
        disableTakeProfit = stockObj["isNeedToCheckTakeProfit"]
        takeProfitPercentage = stockObj["takeProfitPercentage"]

    sma = 0
    result = None
    # get market data for stock symbol
    yahoostockobj = yahoo_finance_get_stock_values(symbol,smarange)
    if yahoostockobj["retcode"] != 0 :
        print("failed to pull data from yahoo finance")
        print(yahoostockobj["retmessage"])
        return None
    ma = yahoostockobj["currentsma"]
    maInicatorDaysBeforeNear = yahoostockobj["weekagosma"]
    maInicatorDaysBeforeFar = yahoostockobj["twoweekagosma"]
    isMaTrandUp = False
    if (ma > maInicatorDaysBeforeNear) and (maInicatorDaysBeforeNear > maInicatorDaysBeforeFar):
        isMaTrandUp = True
    closePrice = yahoostockobj["closePrice"]
    percentageDifference = percentage_difference(closePrice, ma)
    hostname = socket.gethostname()

    msg = symbol + ', action ' + action + \
          ", rang " + str(smarange) + ",sma " + \
          str(ma) + ",close " + \
          str(closePrice) + \
          ", percentage difference " + str(percentageDifference) + "%" +", account "+account
    msg = msg + " , " + hostname
    googleSheetsRaw = [symbol, action, 'sma' + str(smarange), ma, closePrice,
                       str(percentageDifference) + "%" ,account]
    smObj={"symbol":symbol,"action":action,"sma":ma,"closed":closePrice}
    if action == "sell":
        if (disableTakeProfit) and (float(percentageDifference) > takeProfitPercentage):
            result = {"stock": stockObj, 'change_action': 'disableTakeProfit',"smObj":smObj}
            msg = msg + ", You have to take profit"
            notifyCenter(msg, googleSheetsRaw, "You have to sell", True)
        else:
            isSell = is_need_sell(closedValue=closePrice, smaValue=ma)
            if isSell:
                result = {"stock": stockObj, 'change_action': 'sellToBuy',"smObj":smObj}
                msg = msg + ", You have to sell"
                notifyCenter(msg,googleSheetsRaw, "You have to sell",True)
            else:
                print(msg)
                writeToLogfile(msg)
                googlesheets_add_history([googleSheetsRaw])
    elif action == "buy":
        isBuy = is_need_buy(smaValue=ma, closedValue=closePrice, percentagedifference=percentageDifference)
        if (isBuy == True) and (isMaTrandUp == True):
            result = {"stock": stockObj, 'change_action': 'buyToSell',"smObj":smObj}
            msg = msg + ", You have to buy"
            notifyCenter(msg, googleSheetsRaw, "You have to sell", True)
        else:
            print(msg)
            writeToLogfile(msg)
            googlesheets_add_history([googleSheetsRaw])
    elif action == "trace":
        print(msg)
        writeToLogfile(msg)
        if abs(float(percentageDifference)) <= smapercentagedifference:
            color_flag = True
        else:
            color_flag = False
        googlesheets_add_history([googleSheetsRaw], color_flag=color_flag)
    return result



'''
--------------------------------------------------------------
this section
read input stocks records file
for each records check if need and notify 
it also create stocks order list  portfolioChangesList
latter we use portfolioChangesList to connect to IBTWS to do sell/buy and update the input file data_invest
'''
enableLogFile = False
enableSendTelgram = False
enableGoogleSheetUpdate = False
updateBuySellInInputFile = False
smapercentagedifference = 0

# Configure the logging level, format, and output
logging.basicConfig(
    level=logging.DEBUG,  # Set the lowest level (DEBUG) to capture all messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("application.log"),  # Logs to a file
        logging.StreamHandler()          # Logs to console
    ]
)

def main():
    '''
    This function performs the following tasks:
        • Retrieves general software parameters from the configuration file.
        • Processes the stock trading data from the JSON file.
          o	For each stock, it evaluates whether the moving average rule is satisfied. If compatible, it triggers a notification and adds the stock to the `portfolioChangesList` for further actions, such as executing buy/sell orders via TWS.
          o	Checks whether trading is enabled, and if so, processes trades for each stock in the `portfolioChangesList` using TWS.

    :return:
    '''
    get_general_parameters()
    investDataFile = "data_invest.json"
    try:
        with open(investDataFile, 'r') as file:
            stocksList = json.load(file)
        print("investDataFile has "+str(len(stocksList)) +" records ")
        portfolioChangesList = []
        # create change portfolio changes list
        for stock in stocksList:
            isNeedTakeProfit = False
            if debug == True:
                maRule_result = None
                if stock["symbol"] == "ARKW":
                    maRule_result = maRule(stock)
            else:
                maRule_result = maRule(stock)
            if maRule_result is not None:
                portfolioChangesList.append(maRule_result)
        if (updateBuySellInInputFile) and (TWSEnable) and (len(portfolioChangesList) > 0):
            result = update_stocks_input_list(portfolioChangesList)
            print(result["message"])
        else:
            print("attention: You have to update portfolio manual !! ,see value for updateBuySellInInputFile and TWSEnable ")
    except FileNotFoundError:
        print(f"Error: The file '{investDataFile}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{investDataFile}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("run is completed")


if __name__ == "__main__":
    main()