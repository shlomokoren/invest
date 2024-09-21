import yfinance as yf
from datetime import datetime, timedelta

# Get today's date and the date from one year ago
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365)

# Fetch the historical data for MSI (Motorola Solutions)
msi_data = yf.download("MSI", start=start_date, end=end_date)

# Display the closing prices
print(msi_data['Close'])
