import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtCore import QTimer


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize the application window
        self.setWindowTitle("20-20-20 Timer")
        self.setGeometry(100, 100, 300, 150)

        # Default focus time: 20 minutes, default break time: 20 seconds
        self.focus_time = 20 * 60
        self.break_time = 20
        self.time_left = self.focus_time
        self.is_focus_period = True

        # Initialize QTimer for updating the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Setup the user interface
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()  # Create a vertical layout for organizing widgets

        # Display the timer label
        self.timer_label = QLabel("Focus Period: 20:00", self)
        layout.addWidget(self.timer_label)

        # Button for starting the timer
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        # Button for resetting the timer
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_timer)
        layout.addWidget(self.reset_button)

        # Input field for customizing focus period
        self.focus_input = QLineEdit(self)
        self.focus_input.setPlaceholderText("Focus Period (minutes)")
        layout.addWidget(self.focus_input)

        # Input field for customizing break period
        self.break_input = QLineEdit(self)
        self.break_input.setPlaceholderText("Break Period (seconds)")
        layout.addWidget(self.break_input)

        # Set the layout for the widget
        self.setLayout(layout)

    def start_timer(self):
        # Start the timer if it's not already active and set custom times if provided
        if not self.timer.isActive():
            self.set_custom_times()
            self.timer.start(1000)
            self.start_button.setEnabled(False)

    def reset_timer(self):
        # Stop the timer, reset the time left, update UI, and enable the start button
        self.timer.stop()
        self.time_left = self.focus_time
        self.is_focus_period = True
        self.timer_label.setText(f"Focus Period: {self.format_time(self.focus_time)}")
        self.start_button.setEnabled(True)

    def update_timer(self):
        # Update the time left and handle timer expiration
        self.time_left -= 1

        if self.time_left <= 0:
            self.timer.stop()
            self.show_notification()
            self.switch_period()
            if self.is_focus_period:
                self.time_left = self.focus_time
            else:
                self.time_left = self.break_time
            self.timer.start(1000)
        else:
            self.timer_label.setText(f"{'Focus' if self.is_focus_period else 'Break'} Period: {self.format_time(self.time_left)}")

    def set_custom_times(self):
        # Set custom focus and break times if valid inputs are provided
        try:
            focus_time = int(self.focus_input.text()) * 60
            break_time = int(self.break_input.text())
            self.focus_time = focus_time if focus_time > 0 else self.focus_time
            self.break_time = break_time if break_time > 0 else self.break_time
        except ValueError:
            pass

    def switch_period(self):
        # Switch between focus and break periods
        self.is_focus_period = not self.is_focus_period
        self.time_left = self.focus_time if self.is_focus_period else self.break_time

    def format_time(self, seconds):
        # Format time from seconds to "mm:ss" format
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def show_notification(self):
        # Show a notification indicating the end of a focus or break period
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Timer Alert")
        msg_box.setText(f"It's time for a {'break' if self.is_focus_period else 'focus period'}")
        msg_box.exec_()


if __name__ == "__main__":
    # Create the application and show the timer widget
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    timer_app.start_timer()  # Start the timer automatically
    sys.exit(app.exec_())
