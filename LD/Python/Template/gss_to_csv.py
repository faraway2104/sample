from __future__ import print_function
import pickle
import os.path
import sys
import csv
import csv_util
#
def export_raw_csv(out_dir, worksheets, service_sheet, sheet_id):
    if os.path.isdir(out_dir) == False:
        os.makedirs(out_dir)

    #出力
    for sheet in worksheets:
        sheet_name = sheet.get("properties", {}).get("title", {})

        with open(out_dir + sheet_name + '.csv', 'w', encoding='utf-8', newline='\n') as f:
            result = service_sheet.values().get(spreadsheetId=sheet_id, range=sheet_name).execute()
            values = result.get('values', [])
            if not values:
                 print('No data found.')
            else:
                 for row in values:
                     writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
                     writer.writerow(row)


#
def export_stringtable_csv(out_dir, raw_dir):
    if os.path.isdir(out_dir) == False:
        os.makedirs(out_dir)

    settings_csv_data = csv_util.get_csv(raw_dir + 'settings.csv')

    # デフォルト言語を取得
    found_deflang, i_deflang, j_deflang = csv_util.find_str_from_csv_data(settings_csv_data, 'デフォルト言語')
    if found_deflang:
        deflang = settings_csv_data[i_deflang][j_deflang + 1]
    else:
        print('Error : not found default language.')
        sys.exit(1)

    # 出力対象シートを取得
    sheet_names = []
    found_sheet, i_sheet, j_sheet = csv_util.find_str_from_csv_data(settings_csv_data, '出力対象シート')
    if found_sheet:
        for idx_sheet in range(j_sheet + 1, len(settings_csv_data[i_sheet]), 1):
            sheet_names.append(settings_csv_data[i_sheet][idx_sheet])

    for i, sheet_name in enumerate(sheet_names):
        #
        with open(out_dir + sheet_name + '.csv', 'w', encoding='utf-8', newline='\n') as f:
            writer1 = csv.writer(f)
            writer1.writerow(['Key','SourceString'])
            writer2 = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)

            sheet_csv_data = csv_util.get_csv(raw_dir + sheet_name + '.csv')

            found_id, i_id, j_id = csv_util.find_str_from_csv_data(sheet_csv_data, 'ID')
            if not found_id:
                print('Error : not found default language text.')
                sys.exit(1)

            found_deftext, i_deftext, j_deftext = csv_util.find_str_from_csv_data(sheet_csv_data, deflang)
            if not found_deftext:
                print('Error : not found default language text.')
                sys.exit(1)

            for idx_row in range(i_id + 1, len(sheet_csv_data), 1):
                id = sheet_csv_data[idx_row][j_id]
                deftext = sheet_csv_data[idx_row][j_deftext]
                writer2.writerow([id, deftext])
