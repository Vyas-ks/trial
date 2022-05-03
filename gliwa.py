"""
 Copyright 2020 Continental Corporation
    :file: gliwa.py
    :platform: windows
    :synopsis:
    This script will parse T1 Report and returns dataframe of memory components

    :author
    Andrei-Antonio Robu (andrei-antonio.robu@continental-corporation.com)
"""

import csv
import pandas as pd


def intid(processid):

    """
     This function converts the processid from string to float
     It is helpful when files are consolidated on processid
    :param processid:
    :return: float
    """
    return float(int(processid))


def generate_memory_components(t1_report):

    """
          This function will extract the Memory Components usage out of the T1_report

          :param t1_report:

          :return: void
     """
    memory_components = "Memory_Components.csv"
    with open(t1_report, 'r', newline='', encoding='utf-8') as f_input, \
            open(memory_components, mode='w', newline='', encoding='utf-8') as f_output:
        csv_reader = csv.reader(f_input, delimiter=";")
        csv_writer = csv.writer(f_output, delimiter=';')
        flag = False
        for row in csv_reader:
            try:
                if row[0].startswith("Process Memory"):
                    flag = True

                    csv_writer.writerow(row)
            except IndexError:
                pass
            try:
                if flag is True and row[0].startswith('    '):
                    row[0] = row[0].strip(" ")
                    csv_writer.writerow(row)
            except IndexError:
                break
    gliwa_df = pd.read_csv(memory_components, delimiter=';')

    del gliwa_df['Data Memory [Sample Count]']
    del gliwa_df['Code Memory [Sample Count]']
    #del gliwa_df['Heap Memory [Sample Count]']
    del gliwa_df['Data Memory [Max] [B]']
    del gliwa_df['Data Memory [Min] [B]']
    del gliwa_df['Code Memory [Max] [B]']
    del gliwa_df['Code Memory [Min] [B]']
    del gliwa_df['Heap Memory [Max] [B]']
    del gliwa_df['Heap Memory [Min] [B]']
    stack_df = extract_stack_memory(t1_report)
    gliwa_df["Stack Memory [Avg] [B]"] = stack_df["Stack Memory [Avg] [B]"]

    gliwa_df2 = pd.DataFrame(gliwa_df['Process Memory'].str.rsplit(" ", n=2, expand=True))
    gliwa_df2.rename({0: 'Process Name', 2: 'Process Id'}, axis=1, inplace=True)
    gliwa_df2.drop(columns=[1], inplace=True)

    gliwa_df2['Gliwa Data Memory[KB]'] = gliwa_df['Data Memory [Avg] [B]']/1024
    gliwa_df2['Gliwa Code Memory[KB]'] = gliwa_df['Code Memory [Avg] [B]'] / 1024
    gliwa_df2['Gliwa Heap Memory[KB]'] = gliwa_df['Heap Memory [Avg] [B]'] / 1024
    gliwa_df2['Gliwa Stack Memory[KB]'] = gliwa_df["Stack Memory [Avg] [B]"] / 1024

    gliwa_df2['Gliwa Code Memory[KB]'] = gliwa_df2['Gliwa Code Memory[KB]'].round(decimals=0)

    del gliwa_df2['Process Id']

    gliwa_df2['Gliwa RAM Total'] = \
        gliwa_df2['Gliwa Data Memory[KB]'] +\
        gliwa_df2['Gliwa Code Memory[KB]'] +\
        gliwa_df2['Gliwa Heap Memory[KB]'] + gliwa_df2['Gliwa Stack Memory[KB]']

    gliwa_df2 = gliwa_df2.sort_values(by=['Process Name'])
    print("Gliwa_Memory_Components.csv generated")
    gliwa_df2.to_excel(r"C:\Users\uie97079\Documents\Project docs\Z233\GliwaOutput.xlsx", index=False, na_rep=0)
    #return gliwa_df2


def extract_stack_memory(t1_report):
    """
        This function will extract the Stack Memory out of the T1_report

        :param t1_report: T1 report path

        :return: dataframe
    """
    with open(t1_report, 'r', newline='', encoding='utf-8') as f_input:
        csv_reader = csv.reader(f_input, delimiter=";")

        components_df = pd.DataFrame(columns=["Process Memory", "Stack Memory [Avg] [B]"])
        component_index = -1
        thread_flag = False
        sum_flag = False
        current_component_name = ''
        sum1 = 0
        for row in csv_reader:
            try:
                if row[0].startswith("Thread Memory"):
                    thread_flag = True
                    continue
            except IndexError:
                pass
            try:
                if thread_flag is True and not row[0].startswith("    "):
                    if sum_flag:
                        components_df.loc[component_index, "Process Memory"] \
                            = current_component_name
                        components_df.loc[component_index, "Stack Memory [Avg] [B]"] = sum1
                    component_index += 1
                    current_component_name = row[0]
                    sum1 = 0
                if thread_flag is True and row[0].startswith("    "):
                    if row[3] != "n/a":
                        sum1 += int(row[3])
                        sum_flag = True
            except IndexError:
                components_df.loc[component_index, "Process Memory"] = current_component_name
                components_df.loc[component_index, "Stack Memory [Avg] [B]"] = sum1
                break
    return components_df


t1_report = r"C:\Users\uie97079\Documents\Project docs\Z233\PH00_trace_report_Reinterpreted-T1scopeStream_20220427_11_34_03_4400.csv"

generate_memory_components(t1_report)