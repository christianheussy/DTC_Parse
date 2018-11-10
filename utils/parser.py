import xml.etree.ElementTree as ET
import re
import dateutil.parser
import os
import datetime


class Parser:
    def __init__(self, target_directory, progress_bar=False):
        self.target_directory = target_directory
        self.progress_bar = progress_bar

    def test_file(self, file):
        # open xml
        tree = ET.parse(file)
        root = tree.getroot()

        # find all TEST elements with the correct description
        target_test = root.findall(".//*TEST[@Description='Clear the Diagnostic Trouble Codes (MSM)']")
        chassis_tag = root.findall(".//*ATTRIBUTE[@ATT_NAME='ChassisNumber']")
        process_tag = root.findall(".PROCESS[@Description='Pre-Dyno']")

        chassis_number = chassis_tag[0].get('ATT_VAL')

        if target_test and process_tag:
            criteria_met = True
        else:
            criteria_met = False

        # parse for DTC information and build dict of fmis per switch (spn)
        dtc_dict = {}
        if criteria_met:
            for attribute in target_test[0][0]:
                test_string = attribute.get('Val')
                if test_string:
                    matches = re.findall('\d{6}-\d*', test_string)
                    if matches:
                        assert len(matches) == 1
                        spn, fmi = matches[0].split('-')
                        dtc_dict.setdefault(spn, [])
                        dtc_dict[spn].append(fmi)

        # check that one switch has all three FMI present
        check_list = ['12', '14', '31']
        contains_fault = False
        for fmi_list in dtc_dict.values():
            if all(elem in fmi_list for elem in check_list):
                contains_fault = True

        return criteria_met, contains_fault, chassis_number

    def parse_directory(self, start, end=datetime.date.today()):
        start_date = dateutil.parser.parse(start).date()

        if type(end) == str:
            end_date = dateutil.parser.parse(end).date()
        elif type(end) == datetime.date:
            end_date = end
        else:
            raise TypeError('End Date is not a valid format')

        files_to_test = []
        for filename in os.listdir(self.target_directory):
            if '.xml' in filename:
                front, date, end = filename.split('_')
                file_date = dateutil.parser.parse(date).date()
                if start_date <= file_date <= end_date:
                    files_to_test.append(filename)

        counter = 0
        total_tests, total_faults = 0, 0
        chassis_tested, chassis_failed = [], []

        for file in files_to_test:
            contains_test, contains_fault, chassis_number = self.test_file(os.path.join(self.target_directory, file))
            if contains_test:
                total_tests += 1
                chassis_tested.append(chassis_number)
            if contains_fault:
                total_faults += 1
                chassis_failed.append(chassis_number)

            counter += 1
            if self.progress_bar:
                self.progress_bar.setValue((counter / len(files_to_test)) * 100)

        number_files_tested = len(files_to_test)
        number_chassis_tested = len(chassis_tested)
        number_chassis_failed = len(chassis_failed)
        return number_files_tested, total_tests, total_faults, number_chassis_tested, number_chassis_failed
