import json
import requests
import os
from datetime import datetime

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
    logfile_path = os.getenv("logfile_path")

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
    msg = symbol + ', action ' + action + ", rang " + str(smarange) + ",sma " + str(
        int(data[0]["sma"])) + ",close " + str(int(data[0]["close"]))
    if  action == "sell":
        isSell = isNeedSell(data)
        if isSell:
            print(msg + ", You have to sell")
            sendtegrammsg(msg  + ", You have to sell")
            writeToLogfile(msg + ", You have to sell", logfile_path)
        else:
            print(msg)
            writeToLogfile(msg , logfile_path)
    elif action == "buy":
        isBuy = isNeedBuy(data)
        if isBuy:
            print(msg + ", You have to buy")
            sendtegrammsg(msg  + ", You have to buy")
            writeToLogfile(msg + ", You have to buy", logfile_path)
        else:
            print(msg)
            writeToLogfile(msg , logfile_path)



def sendtegrammsg(message):
    # Replace 'your_bot_token' with your bot's token
    bot_token = os.getenv("bot_token")

    # Replace 'your_chat_id' with the chat ID or the recipient's user ID
    chat_id = '420134022'

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
def writeToLogfile(line,logfile_path):
    # Get the current date and time
    now = datetime.now()
    # Format it as a string
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    logfile_path = os.getenv("logfile_path")
    # Open the file in append mode ('a')
    with open(logfile_path, "a") as logfile:
        # Write a line to the log file
        logfile.write(current_time +","+ line +" \n")

debug = True
apikey = os.getenv("apikey")
# Read the JSON file
with open('data_invest.json', 'r') as file:
    symbols = json.load(file)
for item in symbols:
    if debug == True:
     if item["symbol"] == "AMZN":
        getsma(item["symbol"],item["range"],item["action"],apikey)
    else:
        getsma(item["symbol"],item["range"],item["action"],apikey)

