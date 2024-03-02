import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QSystemTrayIcon, QMenu, QGridLayout, QHBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from plyer import notification

class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2omer: 20:00")
        self.setGeometry(100, 100, 400, 200)
        self.setFixedSize(400, 200)

        self.focus_minutes = 20
        self.focus_seconds = 0
        self.break_minutes = 0
        self.break_seconds = 20
        self.time_left = self.focus_minutes * 60 + self.focus_seconds
        self.is_focus_period = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.timeout.connect(self.update_tooltip)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        period_layout = QHBoxLayout()
        self.period_label = QLabel()
        period_layout.addWidget(self.period_label)
        self.timer_label = QLabel()
        period_layout.addWidget(self.timer_label)
        layout.addLayout(period_layout)

        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel("Focus Period:"), 2, 0)
        self.focus_minutes_spinbox = QSpinBox(self)
        self.focus_minutes_spinbox.setSuffix(" minutes")
        self.focus_minutes_spinbox.setValue(self.focus_minutes)
        self.focus_minutes_spinbox.valueChanged.connect(self.validate_input)
        grid_layout.addWidget(self.focus_minutes_spinbox, 2, 1)
        self.focus_seconds_spinbox = QSpinBox(self)
        self.focus_seconds_spinbox.setSuffix(" seconds")
        self.focus_seconds_spinbox.setRange(0, 59)
        self.focus_seconds_spinbox.setValue(self.focus_seconds)
        self.focus_seconds_spinbox.valueChanged.connect(self.validate_input)
        grid_layout.addWidget(self.focus_seconds_spinbox, 2, 2)
        grid_layout.addWidget(QLabel("Break Period:"), 3, 0)
        self.break_minutes_spinbox = QSpinBox(self)
        self.break_minutes_spinbox.setSuffix(" minutes")
        self.break_minutes_spinbox.setRange(0, 59)
        self.break_minutes_spinbox.setValue(self.break_minutes)
        self.break_minutes_spinbox.valueChanged.connect(self.validate_input)
        grid_layout.addWidget(self.break_minutes_spinbox, 3, 1)
        self.break_seconds_spinbox = QSpinBox(self)
        self.break_seconds_spinbox.setSuffix(" seconds")
        self.break_seconds_spinbox.setRange(0, 59)
        self.break_seconds_spinbox.setValue(self.break_seconds)
        self.break_seconds_spinbox.valueChanged.connect(self.validate_input)
        grid_layout.addWidget(self.break_seconds_spinbox, 3, 2)
        layout.addLayout(grid_layout)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_timer)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)
        self.add_system_tray_icon()

    def add_system_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "clock.png")
        self.tray_icon.setIcon(QIcon(icon_path))
        tray_menu = QMenu(self)
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
            if self.is_focus_period:
                self.time_left = self.focus_minutes * 60 + self.focus_seconds
            else:
                self.time_left = self.break_minutes * 60 + self.break_seconds
            self.setWindowTitle(f"2omer: {self.format_time(self.time_left)}")
            self.timer.start(1000)
        else:
            self.update_timer_display()
            self.setWindowTitle(f"2omer: {self.format_time(self.time_left)}")

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
        self.time_left = self.focus_minutes * 60 + self.focus_seconds if self.is_focus_period \
            else self.break_minutes * 60 + self.break_seconds

    def show_notification(self):
        notification_title = "Timer Alert"
        notification_text = f"It's time for a {'break' if self.is_focus_period else 'focus period'}"
        notification.notify(
            title=notification_title,
            message=notification_text,
            app_name="2omer"
        )

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def update_tooltip(self):
        self.tray_icon.setToolTip(self.format_time(self.time_left))

    def validate_input(self):
        if (self.focus_minutes_spinbox.value() == 0 and self.focus_seconds_spinbox.value() == 0) \
                or (self.break_minutes_spinbox.value() == 0 and self.break_seconds_spinbox.value() == 0):
            self.start_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    timer_app.start_timer()
    sys.exit(app.exec_())
