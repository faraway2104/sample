from __future__ import print_function
import os.path
import sys
import csv
import csv_util

PO_HEADER_FORMAT = '''# Game {0} translation.
# Copyright Epic Games, Inc. All Rights Reserved.
# 
msgid ""
msgstr ""
"Project-Id-Version: {1}\\n"
"POT-Creation-Date: 2020-08-18 09:13\\n"
"PO-Revision-Date: 2020-08-18 09:13\\n"
"Language-Team: \\n"
"Language: {2}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=1; plural=0;\\n"

'''

PO_DATA_FORMAT = '''#. Key:	{0}
#. SourceLocation:	{1}
#: {1}
msgctxt \"{2}\"
msgid \"{3}\"
msgstr \"{4}\"

'''

#
def export_po(out_dir, raw_dir):
    # 
    settings_csv_data = csv_util.get_csv(raw_dir + 'settings.csv')
    # ターゲット名の取得
    found_target, i_target, j_target = csv_util.find_str_from_csv_data(settings_csv_data, 'ターゲット名')
    if not found_target:
        print('Error : Not found \"ターゲット名\" in settings.csv')
        return False
    target_name = settings_csv_data[i_target][j_target + 1]

    # StringTable出力先の取得
    found_st, i_st, j_st = csv_util.find_str_from_csv_data(settings_csv_data, 'StringTable出力先')
    if not found_st:
        print('Error : Not found \"StringTable出力先\" in settings.csv')
        return False
    asset_dir = settings_csv_data[i_st][j_st + 1]

    # 出力対象シートを取得
    sheet_names = []
    found_sheet, i_sheet, j_sheet = csv_util.find_str_from_csv_data(settings_csv_data, '出力対象シート')
    if found_sheet:
        for idx_sheet in range(j_sheet + 1, len(settings_csv_data[i_sheet]), 1):
            sheet_names.append(settings_csv_data[i_sheet][idx_sheet])
    found_lang, i_lang, j_lang = csv_util.find_str_from_csv_data(settings_csv_data, '出力対象言語')
    found_deflang, i_deflang, j_deflang = csv_util.find_str_from_csv_data(settings_csv_data, 'デフォルト言語')
    if found_lang and found_deflang:
        if j_lang == j_deflang:
            deflang = settings_csv_data[i_deflang][j_deflang + 1]
            for idx_lang in range(j_lang + 1, len(settings_csv_data[i_lang]), 1):
                lang = settings_csv_data[i_lang][idx_lang]
                __output_po(out_dir, raw_dir, target_name, sheet_names, deflang, lang, asset_dir)
        else:
            print('not match foramt. j_lang={0} j_deflang={1}'.format(j_lang, j_deflang))
    else:
        print('not match foramt. found_lang={0} found_deflang={1}'.format(found_lang, found_deflang))
    return True

def __output_po(out_dir, raw_dir, target_name, sheet_names, deflang, lang, asset_dir):
    out_text = ''
    header = PO_HEADER_FORMAT.format('Japanese', target_name, lang)
    out_text += header

    for sheet_name in sheet_names:
        sheet_csv_data = csv_util.get_csv(raw_dir + sheet_name + '.csv')
        found_id, i_id, j_id = csv_util.find_str_from_csv_data(sheet_csv_data, 'ID')
        found_deftext, i_deftext, j_deftext = csv_util.find_str_from_csv_data(sheet_csv_data, deflang)
        found_text, i_text, j_text = csv_util.find_str_from_csv_data(sheet_csv_data, lang)
        if found_id and found_deftext and found_text:
            if i_id == i_text and i_id == i_deftext:
                for idx_row in range(i_id + 1, len(sheet_csv_data), 1):
                    id = sheet_csv_data[idx_row][j_id]
                    deftext = sheet_csv_data[idx_row][j_deftext]
                    text = sheet_csv_data[idx_row][j_text]
                    data = PO_DATA_FORMAT.format(id, asset_dir + '/' + sheet_name + '.' + sheet_name, sheet_name + ',' + id, deftext, text)
                    out_text += data
            else:
                print('not match foramt. i_id={0} i_deftext={1} i_text={2}'.format(i_id, i_deftext, i_text))
        else:
            print('not match foramt. found_id={0} found_deftext={1} found_text={2}'.format(found_id, found_deftext, found_text))

    # 出力
    if os.path.isdir(out_dir + lang) == False:
        os.makedirs(out_dir + lang)
    with open(out_dir + lang + '/' + target_name + '.po', 'w', encoding='utf-8-sig', newline='\n') as f:
        f.write(out_text)
    return True

