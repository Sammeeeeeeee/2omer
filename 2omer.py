import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QSpinBox,
    QSystemTrayIcon,
    QMenu,
    QGridLayout,
    QHBoxLayout,
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from plyer import notification


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2omer: 20:00")
        self.setFixedSize(400, 200)

        self.default_focus_minutes = 20
        self.default_focus_seconds = 0
        self.default_break_minutes = 0
        self.default_break_seconds = 20

        self.focus_minutes = self.default_focus_minutes
        self.focus_seconds = self.default_focus_seconds
        self.break_minutes = self.default_break_minutes
        self.break_seconds = self.default_break_seconds

        self.time_left = self.focus_minutes * 60 + self.focus_seconds
        self.is_focus_period = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.timeout.connect(self.update_tooltip)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.setup_period_display(layout)
        self.setup_time_input(layout)
        self.setup_buttons(layout)

        self.setLayout(layout)
        self.add_system_tray_icon()

    def setup_period_display(self, layout):
        period_layout = QHBoxLayout()
        self.period_label = QLabel("Focus Period")
        self.period_label.setObjectName("PeriodLabel")
        period_layout.addWidget(self.period_label)
        self.timer_label = QLabel()
        self.timer_label.setObjectName("TimerLabel")
        period_layout.addWidget(self.timer_label)
        layout.addLayout(period_layout)

    def setup_time_input(self, layout):
        grid_layout = QGridLayout()

        grid_layout.addWidget(QLabel("Focus Period:"), 1, 0)
        self.focus_minutes_spinbox = self.create_spinbox(self.focus_minutes, " minutes", 0, 59)
        grid_layout.addWidget(self.focus_minutes_spinbox, 1, 1)
        self.focus_seconds_spinbox = self.create_spinbox(self.focus_seconds, " seconds", 0, 59)
        grid_layout.addWidget(self.focus_seconds_spinbox, 1, 2)

        grid_layout.addWidget(QLabel("Break Period:"), 2, 0)
        self.break_minutes_spinbox = self.create_spinbox(self.break_minutes, " minutes", 0, 59)
        grid_layout.addWidget(self.break_minutes_spinbox, 2, 1)
        self.break_seconds_spinbox = self.create_spinbox(self.break_seconds, " seconds", 0, 59)
        grid_layout.addWidget(self.break_seconds_spinbox, 2, 2)

        layout.addLayout(grid_layout)

    def setup_buttons(self, layout):
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("StartButton")
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("ResetButton")
        self.reset_button.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

    def create_spinbox(self, value, suffix, min_value, max_value):
        spinbox = QSpinBox()
        spinbox.setSuffix(suffix)
        spinbox.setRange(min_value, max_value)
        spinbox.setValue(value)
        spinbox.valueChanged.connect(self.validate_input)
        return spinbox

    def add_system_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "clock.png")
        try:
            self.tray_icon.setIcon(QIcon(icon_path))
        except FileNotFoundError as e:
            print("Icon file not found:", e)
        tray_menu = QMenu()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.update_tooltip()
        self.tray_icon.show()
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)

    def start_timer(self):
        if not self.timer.isActive():
            self.set_custom_times()
            self.timer.start(1000)
            self.start_button.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        self.time_left = self.focus_minutes * 60 + self.focus_seconds
        self.is_focus_period = True
        self.update_timer_display()
        self.setWindowTitle("2omer: 20:00")
        self.start_button.setEnabled(True)

    def update_timer(self):
        self.time_left -= 1
        if self.time_left <= 0:
            self.timer.stop()
            self.show_notification()
            self.switch_period()
            self.set_period_time()
            self.timer.start(1000)
        else:
            self.update_timer_display()

    def update_timer_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_str = f"{minutes:02}:{seconds:02}"
        self.timer_label.setText(f"<b>{time_str}</b>")
        self.period_label.setText("Focus Period" if self.is_focus_period else "Break Period")

    def set_custom_times(self):
        self.focus_minutes = self.focus_minutes_spinbox.value()
        self.focus_seconds = self.focus_seconds_spinbox.value()
        self.break_minutes = self.break_minutes_spinbox.value()
        self.break_seconds = self.break_seconds_spinbox.value()

    def switch_period(self):
        self.is_focus_period = not self.is_focus_period

    def set_period_time(self):
        if self.is_focus_period:
            self.time_left = self.focus_minutes * 60 + self.focus_seconds
        else:
            self.time_left = self.break_minutes * 60 + self.break_seconds

    def show_notification(self):
        notification_title = "Timer Alert"
        period = "break" if self.is_focus_period else "focus period"
        notification_text = f"It's time for a {period}"
        try:
            notification.notify(title=notification_title, message=notification_text, app_name="2omer")
        except Exception as e:
            print("Failed to show notification:", e)

    def update_tooltip(self):
        self.tray_icon.setToolTip(self.format_time(self.time_left))

    def validate_input(self):
        if (
            self.focus_minutes_spinbox.value() == 0 and self.focus_seconds_spinbox.value() == 0
        ) or (
            self.break_minutes_spinbox.value() == 0 and self.break_seconds_spinbox.value() == 0
        ):
            self.start_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
        QWidget {
            background-color: #f0f0f0;
            color: #333;
        }
        QLabel#PeriodLabel {
            font-weight: bold;
            font-size: 18px;
        }
        QLabel#TimerLabel {
            font-size: 24px;
        }
        QPushButton#StartButton, QPushButton#ResetButton {
            background-color: #007bff;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton#StartButton:hover, QPushButton#ResetButton:hover {
            background-color: #0056b3;
        }
        """
    )
    timer_app = TimerApp()
    timer_app.show()
    timer_app.start_timer()
    sys.exit(app.exec_())
