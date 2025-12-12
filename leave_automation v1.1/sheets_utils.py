# sheets_utils.py
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_client():
    creds_path = os.getenv("SHEETS_CREDENTIALS_JSON_PATH")
    if not creds_path:
        raise ValueError("SHEETS_CREDENTIALS_JSON_PATH not set")
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client

def append_row_to_sheet(row):
    spreadsheet_id = os.getenv("SHEETS_SPREADSHEET_ID")
    client = get_client()
    sheet = client.open_by_key(spreadsheet_id).sheet1
    sheet.append_row(row)
