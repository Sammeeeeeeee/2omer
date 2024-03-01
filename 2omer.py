import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer, Qt

class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("20-20-20 Timer")
        self.setGeometry(100, 100, 300, 200)

        self.focus_period = 20 * 60  # Default focus period: 20 minutes
        self.break_period = 20  # Default break period: 20 seconds

        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24pt;")
        self.update_timer()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        self.reset_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.timer_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.reset_button)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.is_break_time = False
        self.is_running = False

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.run_timer()

    def pause_timer(self):
        self.is_running = False
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    def reset_timer(self):
        self.is_running = False
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.is_break_time = False
        self.update_timer()

    def run_timer(self):
        start_time = self.focus_period if not self.is_break_time else self.break_period
        self.timer.start(1000)
        self.timer.timeout.connect(lambda: self.update_timer(start_time))

    def update_timer(self, remaining_time=None):
        if remaining_time is None:
            remaining_time = self.focus_period if not self.is_break_time else self.break_period
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.setText(timer_text)
        remaining_time -= 1
        if remaining_time < 0:
            if not self.is_break_time:
                QMessageBox.information(self, "Focus Period Over", "Take a break now!")
                self.is_break_time = True
            else:
                QMessageBox.information(self, "Break Over", "Focus time starts now!")
                self.is_break_time = False
            self.update_timer()

def main():
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
