import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QFileDialog, QProgressBar,\
    QTextEdit, QLabel, QMessageBox, QDateEdit
from PyQt5.QtCore import QDate
from utils import parser


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.pbar = QProgressBar(self)
        self.num_files = QTextEdit()
        self.num_tests = QTextEdit()
        self.num_fails = QTextEdit()
        self.num_chassis = QTextEdit()
        self.num_chassis_failed = QTextEdit()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit(QDate.currentDate())
        self.folder_path = None
        self.init_ui()

    def init_ui(self):

        run_button = QPushButton("Parse Files")
        file_select_button = QPushButton("Select Directory")

        output_labels = ['Files Parsed:', 'Total Tests:', 'Total Tests Failed:', 'Unique Chassis Tested:',
                         'Unique Chassis Failed:']

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
        res_box.addWidget(self.num_chassis)
        res_box.addWidget(self.num_chassis_failed)

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
            parse = parser.Parser(self.folder_path, self.pbar)
            num_files, tests, faults, num_chassis, num_chassis_fail = parse.parse_directory('20181001')
            self.num_files.setText(str(num_files))
            self.num_tests.setText(str(tests))
            self.num_fails.setText(str(faults))
            self.num_chassis.setText(str(num_chassis))
            self.num_chassis_failed.setText(str(num_chassis_fail))
        else:
            self.pop_error('No directory specified')

    def pop_error(self, message):
        QMessageBox.about(self, "Error", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
