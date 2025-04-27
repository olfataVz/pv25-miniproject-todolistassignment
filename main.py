from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QCheckBox, QLabel, QWidget, QScrollArea
import sys
from datetime import datetime, timedelta

class ToDoListApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("todo_list.ui", self)

        # Data tugas default
        self.assignments = {
            'Today': [
                {"name": "Tugas Pengolahan Data", "deadline": "17 April, 23.59"},
            ],
            '1 Weeks': [
                {"name": "Tugas Pengenalan AI", "deadline": "20 April, 18.00"},
                {"name": "Tugas Sistem Basis Data", "deadline": "22 April, 12.00"},
            ],
            '1 Month': [
                {"name": "Tugas UAS PemVis", "deadline": "10 Mei, 15.00"},
                {"name": "Tugas Fuzzy Final", "deadline": "15 Mei, 10.00"},
            ]
        }

        self.completed_tasks = []

        # Gabungkan semua tugas
        self.assignments['1 Weeks'] += self.assignments['Today']
        self.assignments['1 Month'] += self.assignments['1 Weeks']

        # Connect tombol dan combobox
        self.comboBoxAssignment.currentTextChanged.connect(self.update_assignment_list)
        self.comboBoxCompleted.currentTextChanged.connect(self.update_completed_list)
        self.applyButton.clicked.connect(self.apply_completed_tasks)
        self.editButton.clicked.connect(self.edit_assignment)

        # Inisialisasi tampilan
        self.update_assignment_list("Today")
        self.update_completed_list("Today")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_assignment_list(self, timeframe):
        self.clear_layout(self.verticalLayoutAssignment)
        self.checkbox_map = {}
        for task in self.assignments.get(timeframe, []):
            cb = QCheckBox(f"{task['name']} - Deadline {task['deadline']}")
            cb.setStyleSheet("color: white;")
            self.verticalLayoutAssignment.addWidget(cb)
            self.checkbox_map[cb] = task
        self.verticalLayoutAssignment.addStretch(1)

    def apply_completed_tasks(self):
        for cb, task in list(self.checkbox_map.items()):
            if cb.isChecked():
                completed_task = task.copy()
                completed_task["completed_at"] = datetime.now()
                self.completed_tasks.append(completed_task)

                for key in ["Today", "1 Weeks", "1 Month"]:
                    self.assignments[key] = [t for t in self.assignments[key] if t != task]

        self.update_assignment_list(self.comboBoxAssignment.currentText())
        self.update_completed_list(self.comboBoxCompleted.currentText())

    def update_completed_list(self, timeframe):
        self.clear_layout(self.verticalLayoutCompleted)

        now = datetime.now()
        if timeframe == "Today":
            threshold = now - timedelta(days=1)
        elif timeframe == "1 Weeks":
            threshold = now - timedelta(weeks=1)
        elif timeframe == "1 Month":
            threshold = now - timedelta(days=30)
        else:
            threshold = datetime.min

        for task in self.completed_tasks:
            completed_time = task.get("completed_at", now)
            if completed_time >= threshold:
                label = QLabel(f"[Completed] {task['name']}")
                self.verticalLayoutCompleted.addWidget(label)
        self.verticalLayoutCompleted.addStretch(1)

    def edit_assignment(self):
        # Custom input dialog untuk nama
        name_dialog = QtWidgets.QInputDialog(self)
        name_dialog.setWindowTitle("New Assignment")
        name_dialog.setLabelText("Enter Assignment Name:")
        name_dialog.setStyleSheet("""
            QLabel, QLineEdit {
                color: white;
                background-color: #2b2b2b;
            }
        """)
        if name_dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        name = name_dialog.textValue()
        if not name:
            return

        # Custom input dialog untuk deadline
        deadline_dialog = QtWidgets.QInputDialog(self)
        deadline_dialog.setWindowTitle("New Assignment")
        deadline_dialog.setLabelText("Enter Deadline (format: 17 April, 23.59):")
        deadline_dialog.setStyleSheet("""
            QLabel, QLineEdit {
                color: white;
                background-color: #2b2b2b;
            }
        """)
        if deadline_dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        deadline_str = deadline_dialog.textValue()
        if not deadline_str:
            return

        # Parsing deadline
        try:
            deadline_date = datetime.strptime(deadline_str, "%d %B, %H.%M")
            deadline_date = deadline_date.replace(year=datetime.now().year)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Format Error", "Deadline format harus seperti: 17 April, 23.59")
            return

        today = datetime(2025, 4, 17)  # Simulasi tanggal hari ini
        new_task = {"name": name, "deadline": deadline_str}

        delta_days = (deadline_date - today).days

        if delta_days == 0:
            self.assignments['Today'].append(new_task)
            self.assignments['1 Weeks'].append(new_task)
            self.assignments['1 Month'].append(new_task)
        elif 0 < delta_days <= 7:
            self.assignments['1 Weeks'].append(new_task)
            self.assignments['1 Month'].append(new_task)
        elif delta_days > 7:
            self.assignments['1 Month'].append(new_task)
        else:
            QtWidgets.QMessageBox.warning(self, "Invalid Deadline", "Deadline sudah lewat!")
            return

        self.update_assignment_list(self.comboBoxAssignment.currentText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoListApp()
    window.show()
    sys.exit(app.exec())
