import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QSystemTrayIcon, QMenu, QGridLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
import os
from plyer import notification

class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize the application window
        self.setWindowTitle("2omer - 20:00")  # Change the window title here
        self.setGeometry(100, 100, 400, 200)
        self.setFixedSize(400, 200)  # Lock the size

        # Default focus time: 20 minutes, default break time: 20 seconds
        self.focus_minutes = 20
        self.focus_seconds = 0
        self.break_minutes = 0
        self.break_seconds = 20
        self.time_left = self.focus_minutes * 60 + self.focus_seconds
        self.is_focus_period = True

        # Initialize QTimer for updating the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.timeout.connect(self.update_tooltip)  # Connect the update_tooltip method to timer's timeout signal

        # Setup the user interface
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()  # Create a vertical layout for organizing widgets

        # Create a grid layout with two rows and two columns
        grid_layout = QGridLayout()

        # Label and spin boxes for focus period
        grid_layout.addWidget(QLabel("Focus Period:"), 0, 0)
        self.focus_minutes_spinbox = QSpinBox(self)
        self.focus_minutes_spinbox.setSuffix(" minutes")
        self.focus_minutes_spinbox.setValue(self.focus_minutes)
        grid_layout.addWidget(self.focus_minutes_spinbox, 0, 1)
        self.focus_seconds_spinbox = QSpinBox(self)
        self.focus_seconds_spinbox.setSuffix(" seconds")
        self.focus_seconds_spinbox.setRange(0, 59)
        self.focus_seconds_spinbox.setValue(self.focus_seconds)
        grid_layout.addWidget(self.focus_seconds_spinbox, 0, 2)

        # Label and spin boxes for break period
        grid_layout.addWidget(QLabel("Break Period:"), 1, 0)
        self.break_minutes_spinbox = QSpinBox(self)
        self.break_minutes_spinbox.setSuffix(" minutes")
        self.break_minutes_spinbox.setRange(0, 59)
        self.break_minutes_spinbox.setValue(self.break_minutes)
        grid_layout.addWidget(self.break_minutes_spinbox, 1, 1)
        self.break_seconds_spinbox = QSpinBox(self)
        self.break_seconds_spinbox.setSuffix(" seconds")
        self.break_seconds_spinbox.setRange(0, 59)
        self.break_seconds_spinbox.setValue(self.break_seconds)
        grid_layout.addWidget(self.break_seconds_spinbox, 1, 2)

        # Add the grid layout to the main layout
        layout.addLayout(grid_layout)

        # Label for displaying timer
        self.timer_label = QLabel()
        layout.addWidget(self.timer_label)

        # Button for starting the timer
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        # Button for resetting the timer
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_timer)
        layout.addWidget(self.reset_button)

        # Set the layout for the widget
        self.setLayout(layout)

        # Add system tray icon
        self.add_system_tray_icon()

    def add_system_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)

        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the icon file relative to the script's directory
        icon_path = os.path.join(script_dir, "clock.png")

        self.tray_icon.setIcon(QIcon(icon_path))  # Set the icon using QIcon with the constructed path to clock.png

        # Create a menu for the system tray icon
        tray_menu = QMenu(self)
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # Set the menu for the system tray icon
        self.tray_icon.setContextMenu(tray_menu)

        # Show remaining time as tooltip when hovering over the tray icon
        self.update_tooltip()

        self.tray_icon.show()

        # Set the window icon
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)

    def start_timer(self):
        # Start the timer if it's not already active and set custom times if provided
        if not self.timer.isActive():
            self.set_custom_times()
            self.timer.start(1000)
            self.start_button.setEnabled(False)

    def reset_timer(self):
        # Stop the timer, reset the time left, update UI, and enable the start button
        self.timer.stop()
        self.time_left = self.focus_minutes * 60 + self.focus_seconds
        self.is_focus_period = True
        self.update_timer_display()
        self.setWindowTitle("2omer - 20:00")  # Reset window title
        self.start_button.setEnabled(True)

    def update_timer(self):
        # Update the time left and handle timer expiration
        self.time_left -= 1

        if self.time_left <= 0:
            self.timer.stop()
            self.show_notification()
            self.switch_period()
            if self.is_focus_period:
                self.time_left = self.focus_minutes * 60 + self.focus_seconds
            else:
                self.time_left = self.break_minutes * 60 + self.break_seconds
            self.setWindowTitle("2omer - 20:00")  # Reset window title
            self.timer.start(1000)
        else:
            self.update_timer_display()
            self.setWindowTitle(f"2omer - {self.format_time(self.time_left)}")  # Update window title

    def update_timer_display(self):
        # Update the timer label text with the current time left, bolding the time left part
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.setText(f"Focus Period: <b>{minutes:02}:{seconds:02}</b>")

    def set_custom_times(self):
        # Set custom focus and break times if valid inputs are provided
        self.focus_minutes = self.focus_minutes_spinbox.value()
        self.focus_seconds = self.focus_seconds_spinbox.value()
        self.break_minutes = self.break_minutes_spinbox.value()
        self.break_seconds = self.break_seconds_spinbox.value()

    def switch_period(self):
        # Switch between focus and break periods
        self.is_focus_period = not self.is_focus_period
        self.time_left = self.focus_minutes * 60 + self.focus_seconds if self.is_focus_period \
            else self.break_minutes * 60 + self.break_seconds

    def show_notification(self):
        # Show a notification indicating the end of a focus or break period
        notification_title = "Timer Alert"
        notification_text = f"It's time for a {'break' if self.is_focus_period else 'focus period'}"
        notification.notify(
            title=notification_title,
            message=notification_text,
            app_name="2omer"
        )

    def format_time(self, seconds):
        # Format time from seconds to "mm:ss" format
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def update_tooltip(self):
        # Update the tooltip text with the current time left
        self.tray_icon.setToolTip(self.format_time(self.time_left))


if __name__ == "__main__":
    # Create the application and show the timer widget
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    timer_app.start_timer()  # Start the timer automatically
    sys.exit(app.exec_())
