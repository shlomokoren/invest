import json
import requests
import os
from datetime import datetime

debug = True

def percentageDifference(closedvalue,smavalue):
    # Calculate the percentage difference
    percentage_difference = ((closedvalue - smavalue) / closedvalue) * 100
    formatted_percentage_difference = "{:.2f}".format(percentage_difference)
    # Print the result
    return (formatted_percentage_difference)

def isNeedBuy(data):
    result = False
    closedValue = int(data[0]["close"])
    smaValue = int(data[0]["sma"])
#    smaValueBefore = int(data[7]["sma"])
    if (smaValue < closedValue ) :
        result = True
        return result
    return (result)


def isNeedSell(data):
    result = False
    closedValue = int(data[0]["close"])
    smaValue = int(data[0]["sma"])
    smaValueBefore = int(data[7]["sma"])
    if (smaValue >=closedValue ) :
        result = True
        return result
    return (result)
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
    percentage_difference = percentageDifference(data[0]["close"], data[0]["sma"])
    msg = symbol + ', action ' + action +\
          ", rang " + str(smarange) + ",sma " +\
          str(int(data[0]["sma"])) + ",close " +\
          str(int(data[0]["close"]))+\
          ", percentage difference "+ str(percentage_difference)+"%"

    if  action == "sell":
        isSell = isNeedSell(data)
        if isSell:
            print(msg + ", You have to sell")
            sendtelegrammsg(msg + ", You have to sell")
            writeToLogfile(msg + ", You have to sell")
        else:
            print(msg)
            writeToLogfile(msg)
    elif action == "buy":
        isBuy = isNeedBuy(data)
        if isBuy:
            print(msg + ", You have to buy")
            sendtelegrammsg(msg + ", You have to buy")
            writeToLogfile(msg + ", You have to buy")
        else:
            print(msg)
            writeToLogfile(msg)
    elif action == "trace":
        print(msg)
        writeToLogfile(msg)


def sendtelegrammsg(message):
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
    # Get the current date and time
    now = datetime.now()
    # Format it as a string
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    logfile_path = str(os.getenv("INVEST_LOGFILE"))
    # Open the file in append mode ('a')
    with open(logfile_path, "a") as logfile:
        # Write a line to the log file
        logfile.write(current_time +","+ line +" \n")

apikey = os.getenv("FINANCIALMODELINGPREP_APIKEY")
# Read the JSON file
script_directory = os.path.dirname(os.path.abspath(__file__))
# if os.name == "nt":
#     investDataFile = script_directory + "\\data_invest.json"
# else:
#     investDataFile=script_directory + "/data_invest.json"
investDataFile = "data_invest.json"
try:
    with open(investDataFile, 'r') as file:
        symbols = json.load(file)
    for item in symbols:
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
