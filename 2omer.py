import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QSystemTrayIcon, QGridLayout, QHBoxLayout, QSizePolicy, QDialog, QRadioButton, QDialogButtonBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QFont, QFontDatabase

# Constants for application
FONT_PATH = "C:/Windows/Fonts/segoeui.ttf"
FONT_NAME = "Segoe UI Variable"
FONT_SIZE = 14
ICON_PATH = "clock.png"
APP_TITLE = "2omer"
APP_WIDTH = 450
APP_HEIGHT = 250
DEFAULT_FOCUS_MINS = 20
DEFAULT_FOCUS_SECS = 0
DEFAULT_BREAK_MINS = 0
DEFAULT_BREAK_SECS = 20
TIMER_INTERVAL = 1000
SPINBOX_WIDTH = 60

class TimerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.config_dir = os.path.join(os.getenv('APPDATA'), '2omer')
        self.config_file = os.path.join(self.config_dir, "config.json")

        self.load_config()
        self.setWindowTitle(f"{APP_TITLE}: {self.focus_minutes:02}:{self.focus_seconds:02}")
        self.setGeometry(100, 100, APP_WIDTH, APP_HEIGHT)
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)
        self.load_font()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.timeout.connect(self.update_tooltip)

        self.setup_ui()
        self.add_system_tray_icon()

    def load_config(self):
        try:
            with open(self.config_file, "r") as config_file:
                config = json.load(config_file)
                self.focus_minutes = config.get("focus_minutes", DEFAULT_FOCUS_MINS)
                self.focus_seconds = config.get("focus_seconds", DEFAULT_FOCUS_SECS)
                self.break_minutes = config.get("break_minutes", DEFAULT_BREAK_MINS)
                self.break_seconds = config.get("break_seconds", DEFAULT_BREAK_SECS)
        except FileNotFoundError:
            self.create_default_config()

        self.time_left = self.focus_minutes * 60 + self.focus_seconds
        self.is_focus_period = True

    def save_config(self):
        config = {
            "focus_minutes": self.focus_minutes_spinbox.value(),
            "focus_seconds": self.focus_seconds_spinbox.value(),
            "break_minutes": self.break_minutes_spinbox.value(),
            "break_seconds": self.break_seconds_spinbox.value()
        }
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            with open(self.config_file, "w") as config_file:
                json.dump(config, config_file)
        except Exception as e:
            print(f"Error saving config: {e}")

    def create_default_config(self):
        default_config = {
            "focus_minutes": DEFAULT_FOCUS_MINS,
            "focus_seconds": DEFAULT_FOCUS_SECS,
            "break_minutes": DEFAULT_BREAK_MINS,
            "break_seconds": DEFAULT_BREAK_SECS
        }
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            with open(self.config_file, "w") as config_file:
                json.dump(default_config, config_file)
        except Exception as e:
            print(f"Error creating default config: {e}")
            sys.exit()

        # Assign default values
        self.focus_minutes = DEFAULT_FOCUS_MINS
        self.focus_seconds = DEFAULT_FOCUS_SECS
        self.break_minutes = DEFAULT_BREAK_MINS
        self.break_seconds = DEFAULT_BREAK_SECS

    def load_font(self):
        QFontDatabase.addApplicationFont(FONT_PATH)

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setup_period_display(layout)
        self.setup_time_input(layout)
        self.setup_buttons(layout)
        self.setLayout(layout)

    def setup_period_display(self, layout):
        self.period_label = self.create_label("", alignment=Qt.AlignCenter, font_name=FONT_NAME, font_size=FONT_SIZE)
        layout.addWidget(self.period_label)

    def setup_time_input(self, layout):
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.create_label("Focus Period:"), 1, 0, Qt.AlignLeft)
        grid_layout.addWidget(self.create_label("Break Period:"), 2, 0, Qt.AlignLeft)
        self.focus_minutes_spinbox, self.focus_seconds_spinbox = self.create_period_layout(grid_layout, 1, self.focus_minutes, self.focus_seconds)
        self.break_minutes_spinbox, self.break_seconds_spinbox = self.create_period_layout(grid_layout, 2, self.break_minutes, self.break_seconds)
        layout.addLayout(grid_layout)

        # Connect valueChanged signal of spinboxes to save_config method
        self.focus_minutes_spinbox.valueChanged.connect(self.save_config)
        self.focus_seconds_spinbox.valueChanged.connect(self.save_config)
        self.break_minutes_spinbox.valueChanged.connect(self.save_config)
        self.break_seconds_spinbox.valueChanged.connect(self.save_config)

    def create_period_layout(self, layout, row, minutes, seconds):
        period_layout = QHBoxLayout()
        minutes_spinbox = self.create_spinbox(minutes, "", 0, 59)
        period_layout.addWidget(minutes_spinbox)
        period_layout.addWidget(self.create_label("minutes"), alignment=Qt.AlignLeft)
        seconds_spinbox = self.create_spinbox(seconds, "", 0, 59)
        layout.addLayout(period_layout, row, 1)
        layout.addWidget(seconds_spinbox, row, 2, alignment=Qt.AlignRight)
        layout.addWidget(self.create_label("seconds"), row, 3, alignment=Qt.AlignLeft)
        return minutes_spinbox, seconds_spinbox

    def setup_buttons(self, layout):
        self.start_button = self.create_button("Start", self.start_timer)
        self.reset_button = self.create_button("Reset", self.reset_timer)
        layout.addWidget(self.start_button)
        layout.addWidget(self.reset_button)

    def create_button(self, title, function):
        button = QPushButton(title, self)
        button.clicked.connect(function)
        return button

    def create_label(self, text, alignment=None, font_name=None, font_size=None):
        label = QLabel(text)
        if alignment:
            label.setAlignment(alignment)
        if font_name and font_size:
            label.setFont(QFont(font_name, font_size))
        return label

    def create_spinbox(self, value, suffix, min_value, max_value):
        spinbox = QSpinBox(self)
        spinbox.setSuffix(suffix)
        spinbox.setRange(min_value, max_value)
        spinbox.setValue(value)
        spinbox.setFocusPolicy(Qt.StrongFocus)
        spinbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        spinbox.setFixedWidth(SPINBOX_WIDTH)
        spinbox.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #d4d4d4; border-radius: 5px; background-color: #f0f0f0; }")
        spinbox.valueChanged.connect(self.validate_input)
        return spinbox

    def start_timer(self):
        self.set_custom_times()  # Set custom times first
        if not self.timer.isActive():
            self.set_period_time()  # Update period time based on custom input
            self.timer.start(TIMER_INTERVAL)
            self.start_button.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        self.load_config()
        self.set_period_time()  # Update period time based on loaded configuration
        self.update_timer_display()
        self.start_button.setEnabled(True)

    def update_timer(self):
        self.time_left -= 1
        if self.time_left <= 0:
            self.timer.stop()
            self.show_notification()
            self.switch_period()
            self.set_period_time()
            self.timer.start(TIMER_INTERVAL)
        else:
            self.update_timer_display()

    def update_timer_display(self):
        self.setWindowTitle(f"{APP_TITLE}: {self.format_time(self.time_left)}")
        period = "Focus Period" if self.is_focus_period else "Break Period"
        self.period_label.setText(f"<b>{period}: {self.format_time(self.time_left)}</b>")

    def set_custom_times(self):
        self.focus_minutes = self.focus_minutes_spinbox.value()
        self.focus_seconds = self.focus_seconds_spinbox.value()
        self.break_minutes = self.break_minutes_spinbox.value()
        self.break_seconds = self.break_seconds_spinbox.value()

    def switch_period(self):
        self.is_focus_period = not self.is_focus_period
        self.set_period_time()  # Update period time based on whether it's a focus or break period

    def set_period_time(self):
        if self.is_focus_period:
            self.time_left = self.focus_minutes * 60 + self.focus_seconds
        else:
            self.time_left = self.break_minutes * 60 + self.break_seconds

    def show_notification(self):
        notification_title = "2omer"
        period = "break" if self.is_focus_period else "focus period"
        notification_text = f"It's time for a {period}"
        self.tray_icon.showMessage(notification_title, notification_text)

    def update_tooltip(self):
        self.tray_icon.setToolTip(self.format_time(self.time_left))

    def validate_input(self):
        if (self.focus_minutes_spinbox.value() == 0 and self.focus_seconds_spinbox.value() == 0) \
                or (self.break_minutes_spinbox.value() == 0 and self.break_seconds_spinbox.value() == 0):
            self.start_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def add_system_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(ICON_PATH), self)
        self.tray_icon.show()

def main():
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    timer_app.start_timer()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
