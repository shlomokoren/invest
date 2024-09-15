import json
from pickle import FALSE

import requests
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from ib_insync import *

debug = False
__version__ = "0.0.3"


def get_general_parameters():
    global enableLogFile, enableSendTelgram, enableGoogleSheetUpdate
    global smapercentagedifference, updateBuySellInInputFile, fixedInvestment
    global TWSaccount,TWSEnable
    global isNeedToCheckTakeProfit
    filename = "general_parameters.json"
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        for item in data:
            if 'enableLogFile' in item:
                enableLogFile = item['enableLogFile']
            elif 'enableSendTelgram' in item:
                enableSendTelgram = item['enableSendTelgram']
            elif 'enableGoogleSheetUpdate' in item:
                enableGoogleSheetUpdate = item['enableGoogleSheetUpdate']
            elif 'smapercentagedifference' in item:
                smapercentagedifference = item['smapercentagedifference']
            elif 'updateBuySellInInputFile' in item:
                updateBuySellInInputFile = item['updateBuySellInInputFile']
            elif 'fixedInvestment' in item:
                fixedInvestment = item['fixedInvestment']
            elif 'TWSaccount' in item:
                TWSaccount = item['TWSaccount']
            elif 'TWSEnable' in item:
                TWSEnable = item['TWSEnable']
            elif 'isNeedToCheckTakeProfit' in item['isNeedToCheckTakeProfit']:
                isNeedToCheckTakeProfit = item['isNeedToCheckTakeProfit']

    except FileNotFoundError:
        print(f"Error: The file '{investDataFile}' was not found.")


def TWSMarketorder(ib, symbol, Orderaction, totalQuatity):
    returnResult = {"retStatus": "", "message": ""}
    msg = "IBTWS action="+Orderaction + " symbol="+symbol + " quatity="+str(totalQuatity)+", "
    try:
        stock = Stock(symbol, 'SMART', 'USD')
        # Create a market order
        order = MarketOrder(Orderaction, totalQuatity)

        # Place the order
        print(f"Placing order {symbol} {Orderaction} {totalQuatity}" )
        trade = ib.placeOrder(stock, order)

        # Wait until the order is placed or updated
        ib.sleep(5)
        # Check if the order is filled or failed
        if (trade.orderStatus.status == 'Filled') :
            msg = msg + "Order {Orderaction} successfully filled. portfolio is automatic updated"
            returnResult = {"retStatus": 'Filled', "message": msg}
        else:
            msg =  msg +  f"Order Status is {trade.orderStatus.status} you have to update portfolio manual."
            returnResult = {"retStatus": trade.orderStatus.status, "message": msg}
    except Exception as order_error:
        msg = msg + f"Error during order placement: {order_error}"
        returnResult = {"retStatus": "error", "message": msg}
    return returnResult
def notifyCenter(message):
    print(message)
    sendtelegrammsg(message)
    writeToLogfile(message)

def update_stocks_input_list(portfolioChangesList):
    ''' after all checks all recommendations are in replaceValueList
      this function change input stocks file according to recommendations
      '''
    global fixedInvestment,enableTakeProfit
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
        # Define the stock you want to buy

    with open(investDataFile, 'r') as file:
        symbols_input_list = json.load(file)
        for item in portfolioChangesList:
            for record in symbols_input_list:
                symbol = record["symbol"]
                action = record['action']
                if symbol == item['stock']['symbol']:
                    if (item['change_action'] == 'sellToBuy') and (record['action'] == 'sell'):
                        if 'isNeedToCheckTakeProfit' in record:
                            record['isNeedToCheckTakeProfit'] = False
                        quantity = record["quantity"]
                        result = TWSMarketorder(ib,record["symbol"], "SELL", quantity)
                        if result["retStatus"] == 'Filled':
                            record['action'] = 'buy'
                            notifyCenter(result["message"])
                        else:
                            notifyCenter(result["message"])
                    elif (item['change_action'] == 'buyToSell') and (record['action'] == 'buy'):
                        closedPrice = item['smObj']['closed']
                        quantity = int(fixedInvestment / closedPrice)
                        result = TWSMarketorder(ib,record["symbol"], "BUY", quantity)
                        notifyCenter(result["message"])
                        if result["retStatus"] == 'Filled':
                            record['action'] = 'sell'
                            record["quantity"] = quantity
                    elif (item['change_action'] == 'disableTakeProfit') and (record['action'] == 'sell'):
                        record['isNeedToCheckTakeProfit'] = False
                        quantity = int(record["quantity"] / 3)
                        result = TWSMarketorder(ib,record["symbol"], "SELL", quantity)
                        notifyCenter(result["message"])
                        if (result["retStatus"] == 'Filled') :              #or(result["retStatus"] == 'PreSubmitted')
                            record["quantity"] = record["quantity"] - quantity
                            message = result["message"]
                            notifyCenter(message)

    with open(investDataFile, 'w') as file:
        json.dump(symbols_input_list, file, indent=4)  # Write the updated symbols to the file
    msg = "portfolio file was update . please take attention for manual update."
    result = {"retStatus": False, "message": msg}
    return(result)


def percentage_difference(closedvalue, smavalue):
    # Calculate the percentage difference
    percentage_difference = ((closedvalue - smavalue) / closedvalue) * 100
    formatted_percentage_difference = "{:.2f}".format(percentage_difference)
    # Print the result
    return (formatted_percentage_difference)

def is_need_buy(smaValue, closedValue, percentagedifference):
    ''' check if need to buy
     check if stock moving average  trand is up
     check if price is above average and it is not far from average
    '''
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
    result = False
    if (smaValue >= closedValue):
        result = True
        return result
    return result

def sendtelegrammsg(message):
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
            spreadsheet = client.open("pythoninvesttest")
            # Check if the "history" sheet exists, if not create it
        except Exception as e:
            print("fail to open sheet pythoninvesttest")
            print(f"An error exception is: {e}")
            return

        try:
            worksheet = spreadsheet.worksheet("investHistoryCommands")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="investHistoryCommands", rows="100", cols="20")
        # Check if the first row is empty (i.e., if the sheet is new)
        if not worksheet.cell(1, 1).value:
            # Add title row
            title_row = ["Date", "Symbol", "Action", "Indecator", "Indicator Value", "Closed", "difference %" ,"Notes"]
            worksheet.update(range_name='A1:H1', values=[title_row])

        # Get the current date
        current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Append the current date to each row and add to the "history" sheet
        for row in symbolsList:
            row.insert(0, current_date)
            result = worksheet.append_row(row)

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

        worksheet.sort((1, 'des'))

def maRule(stockObj, apikey):
    '''

    :param symbol:
    :param smarange:
    :param action:
    :param apikey:
    :return: mapkey symbol : buyToSell/SellToBuy
    '''
    symbol = stockObj["symbol"]
    smarange = stockObj["range"]
    action = stockObj["action"]
    disableTakeProfit = False
    takeProfitPercentage = 1000
    if "isNeedToCheckTakeProfit" in stockObj:
        disableTakeProfit = stockObj["isNeedToCheckTakeProfit"]
        takeProfitPercentage = stockObj["takeProfitPercentage"]

    sma = 0
    result = None
    #    url = "https://financialmodelingprep.com/api/v3/technical_indicator/1day/AAPL?type=sma&period=150&apikey=XOdeeszqGm4RohYI1hZH1dJb92ALCFZN"
    payload = {}
    headers = {}
    params = {
        'type': 'sma',
        'period': str(smarange),
        'apikey': apikey
    }
    url = "https://financialmodelingprep.com/api/v3/technical_indicator/1day/" + symbol
    response = requests.request("GET", url, headers=headers, data=payload, params=params)
    data = response.json()
    maIndicator = data[0]["sma"]
    maInicatorDaysBeforeNear = data[7]["sma"]
    maInicatorDaysBeforeFar = data[14]["sma"]
    isMaTrandUp = False
    if (maIndicator > maInicatorDaysBeforeNear) and (maInicatorDaysBeforeNear > maInicatorDaysBeforeFar):
        isMaTrandUp = True
    closePrice = data[0]["close"]
    percentageDifference = percentage_difference(closePrice, maIndicator)
    msg = symbol + ', action ' + action + \
          ", rang " + str(smarange) + ",sma " + \
          str(int(data[0]["sma"])) + ",close " + \
          str(int(data[0]["close"])) + \
          ", percentage difference " + str(percentageDifference) + "%"
    googleSheetsRaw = [symbol, action, 'sma' + str(smarange), int(data[0]["sma"]), int(data[0]["close"]),
                       str(percentageDifference) + "%"]
    smObj={"symbol":symbol,"action":action,"sma":data[0]["sma"],"closed":data[0]["close"]}
    if action == "sell":
        if (disableTakeProfit) and (float(percentageDifference) > takeProfitPercentage):
            result = {"stock": stockObj, 'change_action': 'disableTakeProfit',"smObj":smObj}
            msg = msg + ", You have to take profit"
            notifyCenter(msg)
            googleSheetsRaw.append("You have to take profit")
            googlesheets_add_history([googleSheetsRaw], color_flag=True)
        else:
            isSell = is_need_sell(closedValue=closePrice, smaValue=maIndicator)
            if isSell:
                result = {"stock": stockObj, 'change_action': 'sellToBuy',"smObj":smObj}
                msg = msg + ", You have to sell"
                notifyCenter(msg)
                googleSheetsRaw.append("You have to sell")
                googlesheets_add_history([googleSheetsRaw], color_flag=True)
            else:
                print(msg)
                writeToLogfile(msg)
                googlesheets_add_history([googleSheetsRaw])
    elif action == "buy":
        isBuy = is_need_buy(smaValue=maIndicator, closedValue=closePrice, percentagedifference=percentageDifference)
        if (isBuy == True) and (isMaTrandUp == True):
            result = {"stock": stockObj, 'change_action': 'buyToSell',"smObj":smObj}
            msg = msg + ", You have to buy"
            notifyCenter(msg)
            googleSheetsRaw.append("You have to buy")
            googlesheets_add_history([googleSheetsRaw], color_flag=True)
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
'''
enableLogFile = False
enableSendTelgram = False
enableGoogleSheetUpdate = False
updateBuySellInInputFile = False
smapercentagedifference = 0

get_general_parameters()
apikey = os.getenv("FINANCIALMODELINGPREP_APIKEY")
investDataFile = "data_invest.json"
try:
    with open(investDataFile, 'r') as file:
        stocks = json.load(file)
    portfolioChangesList = []
    # create change portfolio changes list
    for stock in stocks:
        isNeedTakeProfit = False
        if debug == True:
            maRule_result = None
            if stock["symbol"] == "ARKW":
                maRule_result = maRule(stock, apikey)
        else:
            maRule_result = maRule(stock, apikey)
        if maRule_result is not None:
            portfolioChangesList.append(maRule_result)
    if (updateBuySellInInputFile) and (TWSEnable):
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
