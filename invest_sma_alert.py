import json
import requests
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


debug = True


def get_general_parameters():
    global enableLogFile , enableSendTelgram ,enableGoogleSheetUpdate
    global smapercentagedifference
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
    except FileNotFoundError:
        print(f"Error: The file '{investDataFile}' was not found.")

    pass

def percentage_difference(closedvalue, smavalue):
    # Calculate the percentage difference
    percentage_difference = ((closedvalue - smavalue) / closedvalue) * 100
    formatted_percentage_difference = "{:.2f}".format(percentage_difference)
    # Print the result
    return (formatted_percentage_difference)

def is_need_buy(data):
    result = False
    closedValue = int(data[0]["close"])
    smaValue = int(data[0]["sma"])
#    smaValueBefore = int(data[7]["sma"])
    if (smaValue < closedValue ) :
        result = True
        return result
    return (result)

def is_need_sell(data):
    result = False
    closedValue = int(data[0]["close"])
    smaValue = int(data[0]["sma"])
    smaValueBefore = int(data[7]["sma"])
    if (smaValue >=closedValue ) :
        result = True
        return result
    return (result)


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
            logfile.write(current_time +","+ line +" \n")

def googlesheets_add_history(symbolsList, color_flag= False):
    global enableGoogleSheetUpdate
    if enableGoogleSheetUpdate is True:
        # # Load the credentials from the JSON key file
        # credentials = Credentials.from_service_account_file(
        #     'E:\\pythoninvest\\pythoninvest-434016-892129d295c9.json',
        #     scopes=["https://www.googleapis.com/auth/spreadsheets",
        #             "https://www.googleapis.com/auth/drive"]
        # )

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
        try:
            worksheet = spreadsheet.worksheet("history")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="history", rows="100", cols="20")
        # Check if the first row is empty (i.e., if the sheet is new)
        if not worksheet.cell(1, 1).value:
            # Add title row
            title_row = ["Date" ,"Symbol", "Action", "Indecator", "Indicator Value", "Closed" , "difference %"]
            worksheet.update(range_name='A1:G1', values = [title_row])


        # Get the current date
        current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Append the current date to each row and add to the "history" sheet
        for row in symbolsList:
            row.insert(0,current_date)
            result = worksheet.append_row(row)

            if color_flag:
                range = str(result['updates']['updatedRange']).split("!")[1]
            # Apply background color to the newly added rows
                worksheet.format(ranges= range,format= {
                    "backgroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 0.0
                    }
                })


        worksheet.sort((1, 'des'))

def getsma(symbol,smarange,action,apikey):
    sma=0

    #    url = "https://financialmodelingprep.com/api/v3/technical_indicator/1day/AAPL?type=sma&period=150&apikey=XOdeeszqGm4RohYI1hZH1dJb92ALCFZN"
    payload = {}
    headers = {}
    params = {
        'type': 'sma',
        'period': str(smarange),
        'apikey': apikey
    }
    url = "https://financialmodelingprep.com/api/v3/technical_indicator/1day/" + symbol
    response = requests.request("GET", url, headers=headers, data=payload,params=params)
#    print(response.status_code)
    data = response.json()
    maIndicator = data[0]["sma"]
    closePrice = data[0]["close"]
    percentagedifference = percentage_difference(closePrice, maIndicator)
    msg = symbol + ', action ' + action +\
          ", rang " + str(smarange) + ",sma " +\
          str(int(data[0]["sma"])) + ",close " +\
          str(int(data[0]["close"]))+\
          ", percentage difference "+ str(percentagedifference)+"%"
    googlesheetsraw = [symbol , action , 'sma'+ str(smarange) , int(data[0]["sma"]) ,int(data[0]["close"]),str(percentagedifference)+"%"]
    if  action == "sell":
        isSell = is_need_sell(data)
        if isSell:
            print(msg + ", You have to sell")
            sendtelegrammsg(msg + ", You have to sell")
            writeToLogfile(msg + ", You have to sell")
            googlesheetsraw.append("You have to sell")
            googlesheets_add_history([googlesheetsraw],color_flag= True)
        else:
            print(msg)
            writeToLogfile(msg)
            googlesheets_add_history([googlesheetsraw])
    elif action == "buy":
        isBuy = is_need_buy(data)
        if isBuy:
            print(msg + ", You have to buy")
            sendtelegrammsg(msg + ", You have to buy")
            writeToLogfile(msg + ", You have to buy")
            googlesheetsraw.append("You have to buy")
            googlesheets_add_history([googlesheetsraw],color_flag= True)
        else:
            print(msg)
            writeToLogfile(msg)
            googlesheets_add_history([googlesheetsraw])
    elif action == "trace":
        print(msg)
        writeToLogfile(msg)
        if  abs(float(percentagedifference)) <= smapercentagedifference:
            color_flag = True
        else:
            color_flag = False
        googlesheets_add_history([googlesheetsraw],color_flag= color_flag)






'''
--------------------------------------------------------------
'''
enableLogFile = False
enableSendTelgram = False
enableGoogleSheetUpdate = False
smapercentagedifference = 0

get_general_parameters()
apikey = os.getenv("FINANCIALMODELINGPREP_APIKEY")
investDataFile = "data_invest.json"
try:
    print("momodebug01")
    with open(investDataFile, 'r') as file:
        symbols = json.load(file)
    print("momodebug02")
    for item in symbols:
        print("momodebug03")
        if debug == True:
         if item["symbol"] == "ADBE":
            getsma(item["symbol"],item["range"],item["action"],apikey)
        else:
            getsma(item["symbol"],item["range"],item["action"],apikey)
except FileNotFoundError:
    print(f"Error: The file '{investDataFile}' was not found.")
except json.JSONDecodeError:
    print(f"Error: The file '{investDataFile}' contains invalid JSON.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
