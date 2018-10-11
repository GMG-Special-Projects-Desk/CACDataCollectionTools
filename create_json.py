import os
from collections import defaultdict
from pprint import pprint
from colorama import Fore
from datetime import datetime
import re
from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf
import os
from datetime import date, timedelta
import json

def main():
    template_file = 'TODO: Where the data spreadsheet is'
    read_workbook = open_workbook(template_file)
    chart_sheet = read_workbook.sheet_by_index(3)

    defendant_col = 4
    yrs_col = 5
    amt_col = 6

    output_data = []

    i = 1
    cell = chart_sheet.cell(i,defendant_col)
    while (True):
        defendant = cell.value
        years = chart_sheet.cell(i, yrs_col).value
        amt = chart_sheet.cell(i, amt_col).value
        output_data.append([defendant, years, amt])
        i += 1
        try:
            cell = chart_sheet.cell(i,defendant_col)
        except:
            break

    with open('visualization/cases_length_amt_data.json', 'w') as outfile:
        json.dump(output_data, outfile)

if __name__ == '__main__':
    main()
