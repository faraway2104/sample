from __future__ import print_function
import pickle
import os.path
import sys
import csv
import tqdm
import csv_util
import gss_to_csv
import csv_to_po
import csv_to_json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1OTQSKEoodfNt3N50x8BUo11YcIBrqXy8p0t1lyLg4X4'

def main():
    progress_bar = tqdm.tqdm(total = 4)

    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('tmp/gss/token.pickle'):
        with open('tmp/gss/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'in/gss/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        if os.path.isdir('out/gss'):
            os.makedirs('tmp/gss')
        with open('tmp/gss/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    service_sheet = service.spreadsheets()
    sheet_meta = service_sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    progress_bar.update(1)
    doc_name = sheet_meta.get('properties' , {}).get("title", {})
    worksheets = sheet_meta.get('sheets', '')

    #出力先の取得
    settings_sheet = service_sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='settings').execute()
    if settings_sheet == None:
        print('Not found sheet \"settings\".')
        sys.exit(1)
    settings_values = settings_sheet.get('values', [])
    if not settings_values:
        print('No data found.')
        sys.exit(1)
    found_out, i_out, j_out = csv_util.find_str_from_csv_data(settings_values, '出力先')
    if not found_out:
        print('Not found \"出力先\".')
        sys.exit(1)
    out_dir = settings_values[i_out][j_out + 1] + '/' + doc_name
    out_dir = out_dir.replace('\\', '/')

    # 生のCSVをエクスポートする
    out_raw_dir = out_dir + '/raw/'
    gss_to_csv.export_raw_csv(out_raw_dir, worksheets, service_sheet, SPREADSHEET_ID)
    progress_bar.update(2)

    # StringTable用のCSVをエクスポートする
    out_stringtable_dir = out_dir + '/stringtable/'
    in_raw_dir = out_raw_dir
    gss_to_csv.export_stringtable_csv(out_stringtable_dir, in_raw_dir)
    progress_bar.update(3)

    # 
    out_po_dir = out_dir + '/po/'
    csv_to_po.export_po(out_po_dir, in_raw_dir)
    progress_bar.update(4)

    #
    out_json_dir = out_dir
    in_stringtable_dir = out_stringtable_dir
    in_po_dir = out_po_dir
    csv_to_json.export_json(out_json_dir, in_raw_dir, in_stringtable_dir, in_po_dir)

if __name__ == '__main__':
    main()
    sys.exit(0)
