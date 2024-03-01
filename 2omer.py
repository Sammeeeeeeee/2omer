import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtCore import QTimer, Qt


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("20-20-20 Timer")
        self.setGeometry(100, 100, 300, 150)

        self.focus_time = 20 * 60  # default focus time: 20 minutes
        self.break_time = 20  # default break time: 20 seconds
        self.time_left = self.focus_time
        self.is_focus_period = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.timer_label = QLabel("Focus Period: 20:00", self)
        layout.addWidget(self.timer_label)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_timer)
        layout.addWidget(self.reset_button)

        self.focus_input = QLineEdit(self)
        self.focus_input.setPlaceholderText("Focus Period (minutes)")
        layout.addWidget(self.focus_input)

        self.break_input = QLineEdit(self)
        self.break_input.setPlaceholderText("Break Period (seconds)")
        layout.addWidget(self.break_input)

        self.setLayout(layout)

    def start_timer(self):
        if not self.timer.isActive():
            self.set_custom_times()
            self.timer.start(1000)
            self.start_button.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        self.time_left = self.focus_time
        self.is_focus_period = True
        self.timer_label.setText(f"Focus Period: {self.format_time(self.focus_time)}")
        self.start_button.setEnabled(True)

    def update_timer(self):
        self.time_left -= 1

        if self.time_left <= 0:
            self.timer.stop()
            self.show_notification()
            self.switch_period()
            self.reset_timer()
        else:
            self.timer_label.setText(f"{'Focus' if self.is_focus_period else 'Break'} Period: {self.format_time(self.time_left)}")

    def set_custom_times(self):
        try:
            focus_time = int(self.focus_input.text()) * 60
            break_time = int(self.break_input.text())
            self.focus_time = focus_time if focus_time > 0 else self.focus_time
            self.break_time = break_time if break_time > 0 else self.break_time
        except ValueError:
            pass

    def switch_period(self):
        self.is_focus_period = not self.is_focus_period
        self.time_left = self.focus_time if self.is_focus_period else self.break_time

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def show_notification(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Timer Alert")
        msg_box.setText(f"It's time for a {'focus' if self.is_focus_period else 'break'}!")
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    sys.exit(app.exec_())
