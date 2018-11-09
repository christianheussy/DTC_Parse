import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QFileDialog, QProgressBar,\
    QTextEdit, QLabel, QMessageBox, QDateEdit

from PyQt5.QtCore import QDate

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


def main(start, end=datetime.date.today(), directory=os.getcwd(), progress_bar=None):
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
            progress_bar.setValue((counter / len(files_to_test)) * 100)

    number_tested = len(files_to_test)
    return str(len(files_to_test)), str(tests_run), str(faults)


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.pbar = QProgressBar(self)
        self.num_files = QTextEdit()
        self.num_tests = QTextEdit()
        self.num_fails = QTextEdit()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit(QDate.currentDate())
        self.folder_path = None
        self.initUI()

    def initUI(self):

        run_button = QPushButton("Parse Files")
        file_select_button = QPushButton("Select Directory")

        output_labels = ['Files Parsed:', 'Tests Found:', 'Fails Found']

        vbox = QVBoxLayout()
        vbox.addWidget(file_select_button)
        vbox.addWidget(run_button)
        vbox.addWidget(self.start_date)
        vbox.addWidget(self.end_date)
        vbox.addStretch(1)

        label_box = QVBoxLayout()

        for label_name in output_labels:
            label_box.addWidget(QLabel(label_name))

        res_box = QVBoxLayout()
        res_box.addWidget(self.num_files)
        res_box.addWidget(self.num_tests)
        res_box.addWidget(self.num_fails)

        top_box = QHBoxLayout()
        top_box.addLayout(vbox)
        top_box.addLayout(label_box)
        top_box.addLayout(res_box)

        bottom_box = QHBoxLayout()
        bottom_box.addWidget(self.pbar)

        window_box = QVBoxLayout()
        window_box.addLayout(top_box)
        window_box.addLayout(bottom_box)

        self.setLayout(window_box)

        # actions
        file_select_button.clicked.connect(self.show_dialog)
        run_button.clicked.connect(self.parse_files)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('DTC Parser')
        self.show()

    def show_dialog(self):
        dialog = QFileDialog
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        self.folder_path = folder_path

    def parse_files(self):

        if self.folder_path:
            num_files, tests, faults = main(start='20181001', directory=self.folder_path, progress_bar=self.pbar)
            self.num_files.setText(num_files)
            self.num_tests.setText(tests)
            self.num_fails.setText(faults)
        else:
            self.pop_error('No directory specified')

    def pop_error(self, message):
        QMessageBox.about(self, "Error", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())