# Stock Moving Average Trading Bot

This software tracks a stock's moving average and executes buy and sell orders accordingly.

## Trading Strategy

- **Sell Order**:  
  A sell order is triggered immediately when the stock price crosses below the moving average.  
  Example: Using a 150-day moving average, if the price moves from above to below, a sell order is placed.

- **Buy Order**:  
  A buy order is executed if:
  1. The stock has shown a clear upward trend.
  2. The price crosses above the moving average from below.
  3. The stock is within the range defined in the parameters file.

## Configuration
External environment parameters:
 globalFileParameters  general file parameters default name is general_parameters.json;
 GOOGLE_APPLICATION_CREDENTIALS
    if "enableGoogleSheetUpdate": true
      api key to share logs on google sheet
 INVEST_LOGFILE
    if "enableLogFile": true
       enable local logfile
 TELEGRAM_BOT_TOKEN
    if "enableSendTelgram": true
      token to send alerts to telegram bot
 TELEGRAM_CHAT_ID
    if "enableSendTelgram": true
        telegram bot id



## Disclaimer

This software is for informational and educational purposes only. Trading involves risk, and past performance is not indicative of future results.
