import gspread
from google.oauth2.service_account import Credentials

# Load the credentials from the JSON key file
credentials = Credentials.from_service_account_file(
    'E:\\pythoninvest\\pythoninvest-434016-892129d295c9.json',
    scopes=["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]
)

# Authorize and create a client
client = gspread.authorize(credentials)

# Open the Google Sheet by name
spreadsheet = client.open("pythoninvesttest")

# Select the first worksheet
worksheet = spreadsheet.sheet1

# Example: Read data from the first row
first_row = worksheet.row_values(1)
print(f"First Row: {first_row}")

# Example: Write data to the first cell (A1)
worksheet.update('A1', 'Hello, World!')

# Example: Read a specific cell value (B2)
cell_value = worksheet.acell('B2').value
print(f"Value at B2: {cell_value}")
