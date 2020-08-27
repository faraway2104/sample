from __future__ import print_function
import os.path
import sys
import csv
import json
import csv_util

#
def export_json(out_dir, raw_dir, stringtable_dir, po_dir):
    # 
    settings_csv_data = csv_util.get_csv(raw_dir + 'settings.csv')

    # ターゲット名を取得
    target_name = ''
    found_target, i_target, j_target = csv_util.find_str_from_csv_data(settings_csv_data, 'ターゲット名')
    if found_target:
        target_name = settings_csv_data[i_target][j_target + 1]

    # 出力対象シートを取得
    sheet_names = []
    found_sheet, i_sheet, j_sheet = csv_util.find_str_from_csv_data(settings_csv_data, '出力対象シート')
    if found_sheet:
        for idx_sheet in range(j_sheet + 1, len(settings_csv_data[i_sheet]), 1):
            sheet_names.append(settings_csv_data[i_sheet][idx_sheet])

    # 出力対象言語を取得
    lang_names = []
    found_lang, i_lang, j_lang = csv_util.find_str_from_csv_data(settings_csv_data, '出力対象言語')
    if found_lang:
        for idx_lang in range(j_lang + 1, len(settings_csv_data[i_lang]), 1):
            lang_names.append(settings_csv_data[i_lang][idx_lang])
    else:
        print('not match foramt. found_lang={0} found_deflang={1}'.format(found_lang, found_deflang))

    #デフォルト言語を取得
    deflang = ''
    found_deflang, i_deflang, j_deflang = csv_util.find_str_from_csv_data(settings_csv_data, 'デフォルト言語')
    if found_deflang:
        deflang = settings_csv_data[i_deflang][j_deflang + 1]
    else:
        print('not match foramt. j_lang={0} j_deflang={1}'.format(j_lang, j_deflang))

    # StringTable出力先を取得
    found_st, i_st, j_st = csv_util.find_str_from_csv_data(settings_csv_data, 'StringTable出力先')
    if not found_st:
        print('Error : Not found \"StringTable出力先\" in settings.csv')
    stringtable_assetdir = settings_csv_data[i_st][j_st + 1]

    # 出力テキスト
    out_text = {}
    out_text['NativeCulture'] = deflang
    out_text['Cultures'] = []
    for culture in lang_names:
        out_text['Cultures'].append(culture)
    out_text['StringTableAssetDir'] = stringtable_assetdir
    out_text['StringTableCSVDir'] = stringtable_dir
    out_text['PODir'] = po_dir
    out_text['StringTableName'] = []
    for sheet_name in sheet_names:
        out_text['StringTableName'].append(sheet_name)

    # ファイル出力
    if os.path.isdir(out_dir) == False:
        os.makedirs(out_dir)
    with open(out_dir + '/' + target_name + '.json', 'w', encoding='utf-8-sig', newline='\n') as f:
        json.dump(out_text, f, ensure_ascii=False, indent=4, sort_keys=False, separators=(',', ': '))
