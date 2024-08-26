import requests
import os

def isNeedSell(data):
    result = False
    closedValue = int(data[0]["close"])
    smaValue = int(data[0]["sma"])
    if (smaValue >=closedValue ):
        result = True
        return result
    return (result)
def getsma(symbol,smarange,apikey):
    sma=0
    url = "https://financialmodelingprep.com/api/v3/technical_indicator/1day/AAPL?type=sma&period=150&apikey=XOdeeszqGm4RohYI1hZH1dJb92ALCFZN"
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
    if isSell:
        print(symbol + ", rang " + str(smarange) + ",sma " + str(int(data[0]["sma"])) + ",close " + str(
            int(data[0]["close"]))+ ", You have to sell")
    else:
        print(symbol +", rang " + str(smarange) +",sma "+ str(int(data[0]["sma"])) +",close "+ str(int(data[0]["close"])) )

apikey = os.getenv("apikey")
symbols = [{"symbol":'AAPL',"range":150},
           {"symbol":'AFRM',"range":300},
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