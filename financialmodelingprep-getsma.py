import requests
import os

def isNeedSell(data):
    result = False
    closedValue = int(data[0]["close"])
    smaValue = int(data[0]["sma"])
#    smaValueBefore = int(data[7]["sma"])
    if (smaValue >=closedValue ) :
        result = True
        return result
    return (result)
def getsma(symbol,smarange,apikey):
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
    isSell = isNeedSell(data)
    msg = "test "+symbol +", rang " + str(smarange) +",sma "+ str(int(data[0]["sma"])) +",close "+ str(int(data[0]["close"]))
    if isSell:
        print(msg + ", You have to sell")
        sendtegrammsg(msg  + ", You have to sell")
    else:
        print(msg)
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


apikey = os.getenv("apikey")
symbols = [{"symbol":'AAPL',"range":150},
           {"symbol":'AFRM',"range":200},
           {"symbol":'AMD',"range":300},
           {"symbol":'CRM',"range":300},
           {"symbol":'GOOG',"range":150},
           {"symbol": 'MSFT', "range": 200},
           {"symbol": 'MSI', "range": 150},
           {"symbol": 'NVDA', "range": 150},
           {"symbol": 'ORCL', "range": 150},
           {"symbol": 'ASML', "range": 200},
           {"symbol": 'ARKW', "range": 150},
           {"symbol": 'AMZN', "range": 200}]
for item in symbols:
    getsma(item["symbol"],item["range"],apikey)
