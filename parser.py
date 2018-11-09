import xml.etree.ElementTree as ET
import re
import dateutil.parser
import os
import datetime


def test_file(file):
    # open xml
    tree = ET.parse(file)
    root = tree.getroot()

    # find all TEST elements with the correct description
    target_test = root.findall(".//*TEST[@Description='Clear the Diagnostic Trouble Codes (MSM)']")

    if target_test:
        contains_test = True
    else:
        return False, False

    # parse for DTC
    dtc_dict = {}

    for attribute in target_test[0][0]:
        test_string = attribute.get('Val')
        if test_string:
            matches = re.findall('\d{6}-\d*', test_string)
            if matches:
                assert len(matches) == 1
                spn, fmi = matches[0].split('-')
                dtc_dict.setdefault(spn, [])
                dtc_dict[spn].append(fmi)

    check_list = ['12', '14', '31']
    contains_fault = False

    for fmi_list in dtc_dict.values():
        if all(elem in fmi_list for elem in check_list):
            contains_fault = True

    return contains_test, contains_fault


def main(start, end=datetime.date.today(), directory=os.getcwd(), progress_bar = None):

    start_date = dateutil.parser.parse(start).date()

    if type(end) == str:
        end_date = dateutil.parser.parse(end).date()
    elif type(end) == datetime.date:
        end_date = end
    else:
        raise TypeError('End Date is not a valid format')

    files_to_test = []
    for filename in os.listdir(directory):
        if '.xml' in filename:
            front, date, end = filename.split('_')
            file_date = dateutil.parser.parse(date).date()
            if start_date <= file_date <= end_date:
                files_to_test.append(filename)

    counter = 0
    tests_run, faults = 0, 0
    for file in files_to_test:
        contains_test, contains_fault = test_file(os.path.join(directory, file))
        if contains_test:
            tests_run += 1
        if contains_fault:
            faults += 1
        counter += 1

        if progress_bar:
            progress_bar.setValue((counter/len(files_to_test))*100)

    print('{} files tested {} tests found, {} fails'.format(len(files_to_test), tests_run, faults))


target_directory = 'test_files'

if __name__ == '__main__':
    main(start='20181001', directory=target_directory)
