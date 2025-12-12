# sheets_utils.py

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_client():
    creds_path = os.getenv("SHEETS_CREDENTIALS_JSON_PATH")
    if not creds_path:
        raise RuntimeError("SHEETS_CREDENTIALS_JSON_PATH not set")
    # normalize
    creds_path = creds_path.replace("\\\\", "/").replace("\\", "/")
    if not os.path.exists(creds_path):
        raise RuntimeError(f"Credentials JSON not found at: {creds_path}")
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client

def append_row_to_sheet(row):
    spreadsheet_id = os.getenv("SHEETS_SPREADSHEET_ID")
    if not spreadsheet_id:
        raise RuntimeError("SHEETS_SPREADSHEET_ID not set")
    client = get_client()
    sheet = client.open_by_key(spreadsheet_id).sheet1
    sheet.append_row(row)
