"""
    Goes through files and collects data about CAC
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

class MetadataForYear:
    """
        Used to track metadata about total and CAC cases per year
    """
    def __init__(self):
        self.date_of_first_case = ''
        self.id_of_first_case = ''
        self.date_of_last_case = ''
        self.id_of_last_case = ''
        self.total_cases = 0
        self.cac_cases = 0
        self.cac_defendants = 0
        self.cac_js_defendants = 0
        self.cac_open_case_defendants = 0
        self.discounted_cases = []
        self.avg_months_taken_for_judgement_satisfied = timedelta()
        self.avg_denominator = 0

class CaseAggregateData:
    """
        Used to track aggregate data about all closed/open CAC cases
    """
    def __init__(self):
        self.total_defendants = 0
        self.unique_defendants = set()
        self.avg_yrs_for_js_or_update = [0,0]
        self.defendants_with_attorneys = 0
        self.total_default_judgements = 0
        self.avg_yrs_for_default_judgement = [0,0]
        self.avg_amt_per_default_judgement = [0,0]
        self.total_default_judgement_amt = 0
        self.avg_default_judgements_per_defendant = [0,0]
        self.num_bankruptcy_notices = 0
        self.avg_yrs_for_bankruptcy_notice = [0,0]
        self.num_bankruptcy_stays = 0
        self.avg_yrs_for_bankruptcy_stay = [0,0]
        self.num_possible_bankruptcy_notices = 0
        self.avg_yrs_for_possible_bankruptcy_notice = [0,0]

def write_chart_data(chart_years_written, chart_sheet, open_cases_chart_data):
    for defendant, years, amt in open_cases_chart_data:
        chart_sheet.write(chart_years_written, 4, defendant)
        chart_sheet.write(chart_years_written, 5, years)
        chart_sheet.write(chart_years_written, 6, amt)
        chart_years_written += 1

def write_aggregates(agg, cases_written, sheet, avg_yrs_type):
    cases_written += 2

    sheet.write(cases_written, 0, "Total Defendants")
    sheet.write(cases_written, 1, "Total Unique Defendants")
    sheet.write(cases_written, 3, avg_yrs_type)
    sheet.write(cases_written, 5, "Number of Defendants with Attorneys")
    sheet.write(cases_written, 6, "Number of Default Judgements Secured")
    sheet.write(cases_written, 7, "Average Years (After Date of Filing/Previous Default Judgment) Default Judgements were Secured")
    sheet.write(cases_written, 8, "Average Amount Per Default Judgement")

    sheet.write(cases_written+3, 9, "Total Amount from all Default Judgements")

    sheet.write(cases_written, 9, "Average Amount of Default Judgements Against Single Defendant")
    sheet.write(cases_written, 10, "Number of Bankruptcy Filings")
    sheet.write(cases_written, 11, "Average Years (After Date of Filing/Previous Bankruptcy Filing) Bankruptcy was Filed For")
    sheet.write(cases_written, 12, "Number of Bankruptcy Stays")
    sheet.write(cases_written, 13, "Average Years (After Date of Filing/Previous Bankruptcy Stay) Bankruptcy Stays were Granted")
    sheet.write(cases_written, 17, "Number of Possible Bankruptcy Filings")
    sheet.write(cases_written, 18, "Average Years (After Date of Filing/Previous Possible Bankruptcy Filing) Possible Bankruptcy was Filed For")
    cases_written += 1
    sheet.write(cases_written, 0, agg.total_defendants)
    sheet.write(cases_written, 1, len(agg.unique_defendants))
    try:
        sheet.write(cases_written, 3, float('%.2f'%((agg.avg_yrs_for_js_or_update[0]/agg.avg_yrs_for_js_or_update[1]))))
    except:
        sheet.write(cases_written, 3, float('%.2f'%0))
    sheet.write(cases_written, 5, agg.defendants_with_attorneys)
    sheet.write(cases_written, 6, agg.total_default_judgements)
    try:
        sheet.write(cases_written, 7, float('%.2f'%((agg.avg_yrs_for_default_judgement[0]/agg.avg_yrs_for_default_judgement[1]))))
    except:
        sheet.write(cases_written, 7, float('%.2f'%0))
    try:
        sheet.write(cases_written, 8, float('%.2f'%((agg.avg_amt_per_default_judgement[0]/agg.avg_amt_per_default_judgement[1]))))
    except:
        sheet.write(cases_written, 8, float('%.2f'%0))
    sheet.write(cases_written+3, 9, agg.total_default_judgement_amt)
    try:
        sheet.write(cases_written, 9, float('%.2f'%((agg.avg_default_judgements_per_defendant[0]/agg.avg_default_judgements_per_defendant[1]))))
    except:
        sheet.write(cases_written, 9, float('%.2f'%0))
    sheet.write(cases_written, 10, agg.num_bankruptcy_notices)
    try:
        sheet.write(cases_written, 11, float('%.2f'%((agg.avg_yrs_for_bankruptcy_notice[0]/agg.avg_yrs_for_bankruptcy_notice[1]))))
    except:
        sheet.write(cases_written, 11, float('%.2f'%0))
    sheet.write(cases_written, 12, agg.num_bankruptcy_stays)
    try:
        sheet.write(cases_written, 13, float('%.2f'%((agg.avg_yrs_for_bankruptcy_stay[0]/agg.avg_yrs_for_bankruptcy_stay[1]))))
    except:
        sheet.write(cases_written, 13, float('%.2f'%0))
    sheet.write(cases_written, 17, agg.num_possible_bankruptcy_notices)
    try:
        sheet.write(cases_written, 18, float('%.2f'%((agg.avg_yrs_for_possible_bankruptcy_notice[0]/agg.avg_yrs_for_possible_bankruptcy_notice[1]))))
    except:
        sheet.write(cases_written, 18, float('%.2f'%0))



def write_metadata(metadata_sheet, metadata_years_written, chart_sheet, \
    chart_years_written, year_metadata, unique_defendants, one_year, total_defendants):
    for year, metadata in year_metadata.items():
        metadata_sheet.write(metadata_years_written, 0, year)
        metadata_sheet.write(metadata_years_written, 1, str(metadata.date_of_first_case))
        metadata_sheet.write(metadata_years_written, 2, metadata.id_of_first_case)
        metadata_sheet.write(metadata_years_written, 3, str(metadata.date_of_last_case))
        metadata_sheet.write(metadata_years_written, 4, metadata.id_of_last_case)
        metadata_sheet.write(metadata_years_written, 5, metadata.total_cases)
        metadata_sheet.write(metadata_years_written, 6, metadata.cac_cases)
        metadata_sheet.write(metadata_years_written, 7, metadata.cac_defendants)
        if year >= 2007:
            chart_sheet.write(chart_years_written, 0, year)
            chart_sheet.write(chart_years_written, 1, metadata.cac_cases)
            try:
                chart_sheet.write(chart_years_written, 2, float('%.2f'%(100*(metadata.cac_cases/metadata.total_cases))))
            except:
                chart_sheet.write(chart_years_written, 2, float('%.2f'%0))
            chart_years_written += 1
        try:
            metadata_sheet.write(metadata_years_written, 8, float('%.2f'%(100*(metadata.cac_cases/metadata.total_cases))))
        except:
            metadata_sheet.write(metadata_years_written, 8, float('%.2f'%0))
        metadata_sheet.write(metadata_years_written, 9, metadata.cac_js_defendants)
        try:
            metadata_sheet.write(metadata_years_written, 10, float('%.2f'%(100*(metadata.cac_js_defendants/metadata.cac_defendants))))
        except:
            metadata_sheet.write(metadata_years_written, 10, float('%.2f'%0))
        metadata_sheet.write(metadata_years_written, 11, metadata.cac_open_case_defendants)

        if metadata.avg_denominator > 0:
            metadata.avg_months_taken_for_judgement_satisfied /= metadata.avg_denominator
            metadata_sheet.write(metadata_years_written, 12, \
                float('%.2f'%(metadata.avg_months_taken_for_judgement_satisfied/one_year)))
        else:
            metadata_sheet.write(metadata_years_written, 12, 0)
        metadata_sheet.write(metadata_years_written, 13, ','.join(metadata.discounted_cases))
        metadata_years_written += 1

    additional_lines_written = metadata_years_written+2
    metadata_sheet.write(additional_lines_written, 0, 'Total Number of Defendants in Cases Brought by CAC')
    additional_lines_written += 1
    metadata_sheet.write(additional_lines_written, 0, total_defendants)
    additional_lines_written += 2
    metadata_sheet.write(additional_lines_written, 0, 'Number of Unique Defendants')
    additional_lines_written += 1
    metadata_sheet.write(additional_lines_written, 0, len(unique_defendants))


def write_to_sheet(sheet, agg, cases_written, case_id, \
        date_filed, date_of_js_or_update, total_defendants, defendant_attorney, \
        default_judgements, bankruptcy_notices, bankruptcy_stays, \
        possible_bankruptcy_notices, one_year, d_num, judges_with_ids, plaintiff, attorney):
    """
        Writes to judgement satisfied and open cases sheets and updates aggregates

        Returns: int, updated number of cases written to the current sheet
    """
    defualt_judgement_row = cases_written - 1
    bankruptcy_notice_row = cases_written - 1
    bankruptcy_stay_row = cases_written - 1
    possible_bankruptcy_notice_row = cases_written - 1
    sheet.write(cases_written, 0, case_id)

    sheet.write(cases_written, 1, str(date_filed))
    sheet.write(cases_written, 2, str(date_of_js_or_update))
    yrs_for_js_or_update = float('%.2f'%((date_of_js_or_update - date_filed)/one_year))

    sheet.write(cases_written, 3, yrs_for_js_or_update)
    agg.avg_yrs_for_js_or_update[0] += yrs_for_js_or_update
    agg.avg_yrs_for_js_or_update[1] += 1
    sheet.write(cases_written, 4, "Debtor " + str(total_defendants))
    sheet.write(cases_written, 5, defendant_attorney[:-1])
    if defendant_attorney[:-1]:
        agg.defendants_with_attorneys += 1
    sum_of_defualt_judgments = 0
    prev_dt = None
    for dt, amt in default_judgements:
        defualt_judgement_row += 1
        agg.total_default_judgements += 1
        sheet.write(defualt_judgement_row, 6, str(dt))
        if prev_dt:
            duration = float('%.2f'%((dt - prev_dt)/one_year))
            sheet.write(defualt_judgement_row, 7, duration)
            agg.avg_yrs_for_default_judgement[0] += duration
            agg.avg_yrs_for_default_judgement[1] += 1
        else:
            duration = float('%.2f'%((dt - date_filed)/one_year))
            sheet.write(defualt_judgement_row, 7, duration)
            agg.avg_yrs_for_default_judgement[0] += duration
            agg.avg_yrs_for_default_judgement[1] += 1
        try:
            amt = float(amt.replace('$','').replace(',',''))
        except:
            amt = 0
        sheet.write(defualt_judgement_row, 8, amt)
        sum_of_defualt_judgments += amt
        agg.avg_amt_per_default_judgement[0] += amt
        agg.avg_amt_per_default_judgement[1] += 1
        prev_dt = dt

    agg.total_default_judgement_amt += sum_of_defualt_judgments
    agg.avg_default_judgements_per_defendant[0] += sum_of_defualt_judgments
    agg.avg_default_judgements_per_defendant[1] += 1
    sheet.write(cases_written, 9, sum_of_defualt_judgments)

    prev_date_of_b_n = None
    if bankruptcy_notices[d_num]:
        for date_of_b_n in bankruptcy_notices[d_num]:
            bankruptcy_notice_row += 1
            agg.num_bankruptcy_notices += 1
            sheet.write(bankruptcy_notice_row, 10, str(date_of_b_n))
            if prev_date_of_b_n:
                duration = float('%.2f'%((date_of_b_n - prev_date_of_b_n)/one_year))
                sheet.write(bankruptcy_notice_row, 11, duration)
                agg.avg_yrs_for_bankruptcy_notice[0] += duration
                agg.avg_yrs_for_bankruptcy_notice[1] += 1
            else:
                duration = float('%.2f'%((date_of_b_n - date_filed)/one_year))
                sheet.write(bankruptcy_notice_row, 11, duration)
                agg.avg_yrs_for_bankruptcy_notice[0] += duration
                agg.avg_yrs_for_bankruptcy_notice[1] += 1


    prev_date_of_b_s = None
    if bankruptcy_stays:
        for date_of_b_s in bankruptcy_stays:
            bankruptcy_stay_row += 1
            agg.num_bankruptcy_stays += 1
            sheet.write(bankruptcy_stay_row, 12, str(date_of_b_s))
            if prev_date_of_b_s:
                duration = float('%.2f'%((date_of_b_s - prev_date_of_b_s)/one_year))
                sheet.write(bankruptcy_stay_row, 13, duration)
                agg.avg_yrs_for_bankruptcy_stay[0] += duration
                agg.avg_yrs_for_bankruptcy_stay[1] += 1
            else:
                duration = float('%.2f'%((date_of_b_s - date_filed)/one_year))
                sheet.write(bankruptcy_stay_row, 13, duration)
                agg.avg_yrs_for_bankruptcy_stay[0] += duration
                agg.avg_yrs_for_bankruptcy_stay[1] += 1
    sheet.write(cases_written, 14, create_judge_string(judges_with_ids))
    sheet.write(cases_written, 15, plaintiff)
    sheet.write(cases_written, 16, attorney)

    prev_date_of_p_b_n = None
    if possible_bankruptcy_notices[d_num]:
        for date_of_p_b_n in possible_bankruptcy_notices[d_num]:
            possible_bankruptcy_notice_row += 1
            agg.num_possible_bankruptcy_notices += 1
            sheet.write(possible_bankruptcy_notice_row, 17, str(date_of_p_b_n))
            if prev_date_of_p_b_n:
                duration = float('%.2f'%((date_of_p_b_n - prev_date_of_p_b_n)/one_year))
                sheet.write(possible_bankruptcy_notice_row, 18, duration)
                agg.avg_yrs_for_possible_bankruptcy_notice[0] += duration
                agg.avg_yrs_for_possible_bankruptcy_notice[1] += 1

            else:
                duration = float('%.2f'%((date_of_p_b_n - date_filed)/one_year))
                sheet.write(possible_bankruptcy_notice_row, 18, duration)
                agg.avg_yrs_for_possible_bankruptcy_notice[0] += duration
                agg.avg_yrs_for_possible_bankruptcy_notice[1] += 1

    cases_written = max(cases_written, defualt_judgement_row,\
            bankruptcy_stay_row, bankruptcy_notice_row) + 1

    return sum_of_defualt_judgments, cases_written


def create_judge_string(judges_with_ids):
    """
        Input: A list of tuples of the form [(judge_name: str, judge_id: str), ...]

        Returns: A string of the form 'judge_name (ID: judge_id ); ...'
    """
    to_return = ''
    for judge_name, judge_id in judges_with_ids:
        try:
            first_comma = judge_name.index(',')
            last_comma = judge_name.rindex(',')
            judge_name = judge_name[:first_comma+1] + ' ' + judge_name[first_comma+1:last_comma]
            to_return += judge_name + ' (ID: ' + judge_id + '); '
        except:
            if judge_id:
                to_return += judge_name + ' (ID: ' + judge_id + '); '
            else:
                to_return += judge_name + '; '
    return to_return[:-2]

def create_defendant_string(defendant_name):
    """
        Input: A string of the form 'last_name first_name middle_initial' or 'last_name first_name'

        Returns: A string of the form 'last_name, first_name middle_initial' or 'last_name, first_name'

        Note: Only works on defendants that are individuals, doesn't work if defendant is an organization.
    """
    try:
        first_space = defendant_name.index(' ')
        return defendant_name[:first_space] + ',' + defendant_name[first_space:]
    except:
        # print("ERROR 1:", defendant_name) #This print is to mark defendants whose names don't follow the general rule
        return defendant_name


def main():
    #SET UP OUTPUT FILE
    template_file = 'template.xlsx'
    read_workbook = open_workbook(template_file)
    write_workbook = copy(read_workbook) # a writable copy (I can't read values out of this, only write to it)
    metadata_sheet = write_workbook.get_sheet(0)
    closed_cases_sheet = write_workbook.get_sheet(1)
    open_cases_sheet = write_workbook.get_sheet(2)
    chart_sheet = write_workbook.get_sheet(3)
    closed_cases_written = 1
    open_cases_written = 1
    metadata_years_written = 1
    chart_years_written = 1

    #TIMEDETLA HELPER
    one_year = timedelta(days=365)

    #SEARCH STRING CONSTANTS
    date_string = "&nbsp;&nbsp;DATE".upper()
    credit_acceptance_string = 'CREDIT&nbsp;ACCEPTANCE'.upper()
    plaintiff_string = r'PLAINTIFF'.upper()
    defendant_string = r'DEFENDANT'.upper()
    small = 'Small;">'.upper()
    raw_date_string = small + r'\d+/\d+/\d+'
    judge_changed_string = 'JUDGE.*CHANGED'.upper()
    judge_from_string = 'FROM:.*(A-Z)*.*,'.upper()
    nbsp = '&nbsp;'.upper()
    judge_of_record = 'JUDGE&nbsp;OF&nbsp;RECORD:'.upper()
    len_judge_marker = len(judge_of_record)
    between_nbsp_string = r'[(&nbsp;)]+.*[(&nbsp;)]+'.upper()
    p_dash = 'P-'.upper()
    numbers = r'\d+'
    rest_of_credit_acceptance = 'CREDIT&nbsp;ACCEPTANCE.*</span>'.upper()
    double_slash = '//'
    defendant_and_number = r'D[\d]+' + '[&nbsp;]+DEFENDANT'.upper()
    rest_of_defendant = '&nbsp;&nbsp;&nbsp;DEFENDANT'.upper()
    judgement_by_default = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;JUDGMENT&nbsp;BY&nbsp;DEFAULT&nbsp;ENTERED'.upper()
    dollar_amt = r'\$\d+,*\d+\.\d+'
    judgement_satisfied_string = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;JUDGMENT&nbsp;SATISFIED'.upper()
    notice_of_bankruptcy = 'NOTICE&nbsp;OF&nbsp;BANKRUPTCY&nbsp;FILED.*</span>'.upper()
    filed = 'FILED'.upper()
    order_for_bankruptcy_stay = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ORDER&nbsp;FOR&nbsp;BANKRUPTCY&nbsp;STAY&nbsp;RECEIVED'.upper()
    d_string = r'D\d+'
    both = 'BOTH'.upper()

    #AGGREGATES FOR CLOSED AND OPEN CASES SEPARATELY
    closed_agg = CaseAggregateData()
    open_agg = CaseAggregateData()

    #TOTAL DEFENDANTS IN ALL CLOSED AND OPEN CAC CASES (used for naming)
    total_defendants = 0
    unique_defendants = set()

    open_cases_chart_data = []

    #YEAR MAPPING
    year_mapping = {
        0: 2000,
        1: 2001,
        2: 2002,
        3: 2003,
        4: 2004,
        5: 2005,
        6: 2006,
        7: 2007,
        8: 2008,
        9: 2009,
        10: 2010,
        11: 2011,
        12: 2012,
        13: 2013,
        14: 2014,
        15: 2015,
        16: 2016,
        17: 2017,
        18: 2018,
        90: 1990,
        91: 1991,
        92: 1992,
        93: 1993,
        94: 1994,
        95: 1995,
        96: 1996,
        97: 1997,
        98: 1998,
        99: 1999
    }

    #YEAR METADATA
    year_metadata = defaultdict(MetadataForYear)
    cases_to_redo = []
    cases_to_redo_file = open("cases_to_redo.txt", "w")

    #THIS DIRECTORY CONTAINS ALL THE HTML FILES SCRAPED FROM THE NODE JS HEADLESS BROWSER CODE
    data_directory = 'TODO: Where the data is'
    for filename in os.listdir(data_directory):
        if filename.endswith('html'):
            year = int(('19' + filename[:2]) if int(filename[:2]) > 18 else ('20' + filename[:2]))

            #CASE ID
            case_id = os.path.splitext(os.path.basename(filename))[0]

            page_content = open(data_directory + filename).read().upper();

            #INCORRECTLY SCRAPED CASES
            if date_string not in page_content:
                cases_to_redo.append(case_id)
                continue

            #DATE FILED
            date_span_index = page_content.index(date_string)
            #find the first date string before this
            date_filed = re.findall(raw_date_string, page_content[date_span_index:])[0]
            date_filed = date_filed[date_filed.index(small) + len(small):]
            date_filed = [int(d_f) for d_f in date_filed.split('/')]
            #Discount cases filed in a different year than the year their ID suggests they should be
            if date_filed[2] not in year_mapping or year_mapping[date_filed[2]] != year:
                year_metadata[year].discounted_cases.append(case_id)
                continue
            date_filed = date(year, date_filed[0], date_filed[1])

            #UPDATE YEAR METADATA
            if year_metadata[year].date_of_first_case == '':
                year_metadata[year].date_of_first_case = date_filed
                year_metadata[year].id_of_first_case = case_id
                year_metadata[year].date_of_last_case = date_filed
                year_metadata[year].id_of_last_case = case_id
            else:
                if case_id < year_metadata[year].id_of_first_case:
                    year_metadata[year].id_of_first_case = case_id
                    year_metadata[year].date_of_first_case = date_filed
                if case_id > year_metadata[year].id_of_last_case:
                    year_metadata[year].id_of_last_case = case_id
                    year_metadata[year].date_of_last_case = date_filed

            year_metadata[year].total_cases += 1

            if credit_acceptance_string in page_content:
                year_metadata[year].cac_cases += 1
                cac_index = page_content.index(credit_acceptance_string)

                #Discount cases in which 'credit acceptance ...' is not the plaintiff
                plaintiff_occurrences = re.findall(plaintiff_string, page_content[:cac_index])
                defendant_occurrences = re.findall(defendant_string, page_content[:cac_index])
                if len(plaintiff_occurrences) == 0 or len(defendant_occurrences) > 0:
                    continue

                #JUDGE(S)
                judges = set()
                for match in re.finditer(judge_changed_string, page_content):
                    try:
                        judge = re.search(judge_from_string, page_content[match.end():])
                        judge = judge.group(0).split(nbsp)
                        judge = ' '.join(judge[1:])
                    except:
                        judge = 'UNKNOWN JUDGE'
                    judges.add(judge)
                judge_index = page_content.index(judge_of_record)
                judge = re.findall(between_nbsp_string, \
                        page_content[judge_index+len_judge_marker:])[0]
                judge = judge[judge.index(nbsp):judge.rindex(nbsp)]
                judge = ' '.join([c for c in judge.split(nbsp) if c != ''])
                judges.add(judge)
                judges_with_ids = []
                for judge in judges:
                    judge_name = ''
                    judge_id = ''
                    for j in judge.split():
                        if j.startswith(p_dash) or j.isdigit():
                            judge_id = re.findall(numbers, j)[0]
                        else:
                            judge_name += j + ' '
                    judges_with_ids.append((judge_name[:-1], judge_id))


                #PLAINTIFF'S NAME and PLAINTIFF'S ATTORNEY
                #since we have screened out cases where "_ CREDIT ACCEPTANCE _" is not the plaintiff,
                #we can be confident that the first occurrence of rest_of_credit_acceptance is the line
                #with the plaintiff and attorney
                plaintiff = re.findall(rest_of_credit_acceptance, page_content[cac_index:])[0]
                plaintiff = plaintiff[:plaintiff.rindex(nbsp)]
                plaintiff = ' '.join([c for c in plaintiff.split(nbsp) if c != ''])
                [plaintiff, attorney] = plaintiff.split(double_slash)

                #DEFENDANTS
                defendant_number_to_defendant_name = defaultdict(str)
                defendant_numbers = list(set(re.findall(defendant_and_number, page_content)))
                for i, _ in enumerate(defendant_numbers):
                    defendant_numbers[i] = defendant_numbers[i][:defendant_numbers[i].index(nbsp)]
                num_defendants = len(defendant_numbers)

                # BANKRUPTCY FILED
                bankruptcy_notices = defaultdict(set)
                possible_bankruptcy_notices = defaultdict(set)
                for b_n in re.finditer(notice_of_bankruptcy, page_content):
                    b_n_index = b_n.start()
                    date_of_b_n = re.findall(raw_date_string, page_content[:b_n_index])[-1]
                    date_of_b_n = date_of_b_n[date_of_b_n.index(small) + len(small):]
                    date_of_b_n = [int(d_o_b_n) for d_o_b_n in \
                            date_of_b_n.split('/')]
                    date_of_b_n = date(year_mapping[date_of_b_n[2]], \
                        date_of_b_n[0], date_of_b_n[1])
                    if num_defendants == 1:
                        bankruptcy_notices[defendant_numbers[0]].add(date_of_b_n)
                    else:
                        b_n_string = b_n.group(0)
                        b_n_string = b_n_string[b_n_string.index(filed)+len(filed):b_n_string.rindex(nbsp)]
                        b_n_string = b_n_string.split(nbsp)
                        b_n_string = ' '.join([b for b in b_n_string if not b.isdigit()])
                        if defendant_string in b_n_string:
                            d_num = ''.join(c for c in b_n_string if c.isdigit())
                            d_num = ('D0' if len(d_num) == 1 else 'D') + d_num
                            bankruptcy_notices[d_num].add(date_of_b_n)
                        elif both in b_n_string and num_defendants == 2:
                            for d_num in defendant_numbers:
                                bankruptcy_notices[d_num].add(date_of_b_n)
                        else:
                            for d_num in defendant_numbers:
                                possible_bankruptcy_notices[d_num].add(date_of_b_n)
                            # print("ERROR 2:", case_id, b_n_string) #This error is to mark when there is a bankruptcy filing but unclear which defendant it pertains to

                for d_num in defendant_numbers:
                    defendant_attorney = ''
                    defendant_index = page_content.index(d_num+rest_of_defendant)
                    defendant = re.findall(between_nbsp_string, page_content[defendant_index:])[1]
                    defendant = defendant[defendant.index(nbsp):defendant.rindex(nbsp)]
                    defendant = defendant.replace(nbsp,' ')
                    defendant = defendant.strip()
                    if '   ' in defendant:
                        d_a = defendant.split('   ')
                        defendant = d_a[0]
                        defendant_attorney = d_a[-1]
                    defendant = defendant.replace('/',' ')
                    defendant_number_to_defendant_name[d_num] = defendant
                    total_defendants += 1
                    unique_defendants.add(defendant)

                    #DEFAULT JUDGEMENTS
                    date_of_js = None
                    default_judgements = []
                    default_judgement_string = d_num + judgement_by_default
                    len_target = len(default_judgement_string)
                    for match in re.finditer(default_judgement_string, page_content):
                            default_judgement_index = match.start()
                            #find the first date string before this
                            try:
                                default_judgement_date = re.findall(raw_date_string, \
                                    page_content[:default_judgement_index])[-1]
                                default_judgement_date = \
                                    default_judgement_date[default_judgement_date.index(small) + \
                                    len(small):]
                                default_judgement_date = [int(d_j_d) for d_j_d in \
                                        default_judgement_date.split('/')]
                                default_judgement_date = \
                                date(year_mapping[default_judgement_date[2]], \
                                    default_judgement_date[0], default_judgement_date[1])
                            except:
                                default_judgement_date = 'UNKNOWN DATE'
                            default_judgement_amt = re.findall(between_nbsp_string, \
                                            page_content[default_judgement_index+len_target:])[0]
                            try:
                                default_judgement_amt = re.findall(dollar_amt, default_judgement_amt)[0]
                            except:
                                default_judgement_amt = 'UNKNOWN AMT'
                            default_judgements.append((default_judgement_date, default_judgement_amt))

                    #BANKRUPTCY STAY GRANTED
                    bankruptcy_stays = set()
                    bankruptcy_stay_string = d_num + order_for_bankruptcy_stay
                    for b_s in re.finditer(bankruptcy_stay_string, page_content):
                        b_s_index = b_s.start()
                        b_s_string = b_s.group(0)
                        date_of_b_s = re.findall(raw_date_string, page_content[:b_s_index])[-1]
                        date_of_b_s = date_of_b_s[date_of_b_s.index(small) + len(small):]
                        date_of_b_s = [int(d_o_b_s) for d_o_b_s in \
                                date_of_b_s.split('/')]
                        date_of_b_s = date(year_mapping[date_of_b_s[2]], \
                            date_of_b_s[0], date_of_b_s[1])
                        bankruptcy_stays.add(date_of_b_s)

                    #JUDGEMENT SATISFIED STATUS
                    judgement_satisfied = (d_num + judgement_satisfied_string) in page_content
                    if judgement_satisfied:
                        js_index = page_content.index(d_num + judgement_satisfied_string)
                        #find the first date string before this
                        try:
                            date_of_js = re.findall(raw_date_string, page_content[:js_index])[-1]
                            date_of_js = date_of_js[date_of_js.index(small) + len(small):]
                            date_of_js = [int(d_o_j) for d_o_j in \
                                    date_of_js.split('/')]
                            date_of_js = date(year_mapping[date_of_js[2]], \
                                date_of_js[0], date_of_js[1])
                            year_metadata[year].avg_months_taken_for_judgement_satisfied += (date_of_js - date_filed)
                            year_metadata[year].avg_denominator += 1
                        except:
                            date_of_js = 'UNKNOWN DATE'

                        _, closed_cases_written = write_to_sheet(closed_cases_sheet, closed_agg, closed_cases_written, case_id, \
                                date_filed, date_of_js, total_defendants, defendant_attorney, \
                                default_judgements, bankruptcy_notices, bankruptcy_stays, \
                                possible_bankruptcy_notices, one_year, d_num, judges_with_ids, \
                                plaintiff, attorney)
                        closed_agg.total_defendants += 1
                        closed_agg.unique_defendants.add(defendant)

                        year_metadata[year].cac_js_defendants += 1
                        year_metadata[year].cac_defendants += 1
                    else:
                        date_of_last_update_to_case = re.findall(raw_date_string, page_content)[-1]
                        date_of_last_update_to_case = date_of_last_update_to_case\
                                [date_of_last_update_to_case.index(small) + len(small):]
                        date_of_last_update_to_case = [int(d_o_l_u_t_c) for d_o_l_u_t_c in \
                                date_of_last_update_to_case.split('/')]
                        date_of_last_update_to_case = date(year_mapping[date_of_last_update_to_case[2]], \
                            date_of_last_update_to_case[0], date_of_last_update_to_case[1])

                        sum_of_defualt_judgments, open_cases_written = write_to_sheet(open_cases_sheet, open_agg, open_cases_written, case_id, \
                                date_filed, date_of_last_update_to_case, total_defendants, defendant_attorney, \
                                default_judgements, bankruptcy_notices, bankruptcy_stays, \
                                possible_bankruptcy_notices, one_year, d_num, judges_with_ids, \
                                plaintiff, attorney)

                        open_agg.total_defendants += 1
                        open_agg.unique_defendants.add(defendant)

                        open_cases_chart_data.append(("Debtor " + str(total_defendants), \
                                float('%.2f'%((date_of_last_update_to_case-date_filed)/one_year)), \
                                sum_of_defualt_judgments))

                        year_metadata[year].cac_open_case_defendants += 1
                        year_metadata[year].cac_defendants += 1

                    if open_cases_written % 1000 == 0:
                        #Prints to report on progress of data analysis
                        print("CLOSED CASES WRITTEN: ", closed_cases_written)
                        print("OPEN CASES WRITTEN: ", open_cases_written)
                        write_workbook.save('output.xls')

    write_metadata(metadata_sheet, metadata_years_written, chart_sheet, \
            chart_years_written, year_metadata, unique_defendants, one_year, total_defendants)
    write_aggregates(open_agg, open_cases_written, open_cases_sheet, "Average Years Case Has Been Open")
    write_aggregates(closed_agg, closed_cases_written, closed_cases_sheet, "Average Years taken for Judgement to be Satisfied")
    write_chart_data(chart_years_written, chart_sheet, open_cases_chart_data)

    write_workbook.save('output.xls')
    cases_to_redo_file.write(str(cases_to_redo))
    cases_to_redo_file.close()

if __name__ == '__main__':
    main()
