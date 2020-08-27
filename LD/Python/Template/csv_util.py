from __future__ import print_function
import csv

# Return csv format array.
def get_csv(filepath):
    csv_data = []
    with open(filepath, 'r', encoding='utf-8', newline='\n') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_data.append(row)
    return csv_data

#
def find_str_from_csv_data(csv_data, str):
    for i, row in enumerate(csv_data):
        for j, col in enumerate(row):
            if col == str:
                return True, i, j
    return False, 0, 0

