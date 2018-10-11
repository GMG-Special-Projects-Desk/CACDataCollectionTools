"""
Prints duplicate filenames
"""
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


def main():
    filenames = set()
    for filename in os.listdir("TODO: Where the data is"):
        if "(1)" in filename:
            print(filename)
        filenames.add(filename)

if __name__ == '__main__':
    main()
