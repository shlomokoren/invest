from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os


def googlesheets_add_history(symbolsList):
    # Load the credentials from the JSON key file
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
        title_row = ["Symbol", "Action", "Indecator", "Indicator Value", "Closed", "Date"]
        worksheet.update('A1:F1', [title_row])


    # Get the current date
    current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Append the current date to each row and add to the "history" sheet
    for row in symbolsList:
        row.append(current_date)
        worksheet.append_row(row)
    worksheet.sort((6, 'des'))



symbolsList = [["MSFT", "trace", 'sma300', 539, 573],["AMZN", "trace",'sma150',179,174]]
googlesheets_add_history(symbolsList)
