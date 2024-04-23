import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QSystemTrayIcon, QMenu, QGridLayout, QHBoxLayout, QSizePolicy, QMessageBox
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
SETTINGS_FILE = os.path.join(os.getenv('APPDATA'), "timer_settings.json")  # JSON file to store timer settings in appdata


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE}: {DEFAULT_FOCUS_MINS:02}:{DEFAULT_FOCUS_SECS:02}")
        self.setGeometry(100, 100, APP_WIDTH, APP_HEIGHT)
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)
        self.load_font()

        self.init_period_values()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.timeout.connect(self.update_tooltip)

        self.setup_ui()
        self.add_system_tray_icon()
        
    def init_period_values(self):
        # Check if settings file exists
        if os.path.exists(SETTINGS_FILE):
            # Load settings from JSON file
            with open(SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
                self.focus_minutes = settings.get('focus_minutes', DEFAULT_FOCUS_MINS)
                self.focus_seconds = settings.get('focus_seconds', DEFAULT_FOCUS_SECS)
                self.break_minutes = settings.get('break_minutes', DEFAULT_BREAK_MINS)
                self.break_seconds = settings.get('break_seconds', DEFAULT_BREAK_SECS)
        else:
            # If settings file doesn't exist, prompt the user to continue
            reply = QMessageBox(QMessageBox.Question, 'No existing settings', 'No existing settings where found. You can create to save settings, or ignore to choose everytime')
            reply.addButton('Create', QMessageBox.YesRole)
            reply.addButton('Ignore', QMessageBox.NoRole)
            button = reply.exec_()
            if button == QMessageBox.No:
                sys.exit()  # Exit the application if the user chooses not to continue
            else:
                # Use default values if the user chooses to continue
                self.focus_minutes = DEFAULT_FOCUS_MINS
                self.focus_seconds = DEFAULT_FOCUS_SECS
                self.break_minutes = DEFAULT_BREAK_MINS
                self.break_seconds = DEFAULT_BREAK_SECS

        self.time_left = self.focus_minutes * 60 + self.focus_seconds
        self.is_focus_period = True


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

    def add_system_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.get_script_dir_path(ICON_PATH)))
        tray_menu = QMenu(self)
        clear_action = tray_menu.addAction("Clear Config")
        clear_action.triggered.connect(self.clear_config)
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.update_tooltip()
        self.tray_icon.show()
        self.setWindowIcon(QIcon(self.get_script_dir_path(ICON_PATH)))

    def get_script_dir_path(self, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, filename)

    def start_timer(self):
        self.set_custom_times()  # Set custom times first
        if not self.timer.isActive():
            self.set_period_time()  # Update period time based on custom input
            self.timer.start(TIMER_INTERVAL)
            self.start_button.setEnabled(False)
            self.save_settings()  # Save settings when timer starts

    def reset_timer(self):
        self.timer.stop()
        self.init_period_values()
        self.update_timer_display()
        self.start_button.setEnabled(True)
        self.save_settings()  # Save settings when timer resets

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

    def save_settings(self):
        settings = {
            'focus_minutes': self.focus_minutes,
            'focus_seconds': self.focus_seconds,
            'break_minutes': self.break_minutes,
            'break_seconds': self.break_seconds
        }
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file)

    def clear_config(self):
        reply = QMessageBox.question(self, 'Clear Configuration', 'Are you sure you want to clear the configuration?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(SETTINGS_FILE)
                QMessageBox.information(self, 'Config Cleared', 'Configuration cleared successfully.', QMessageBox.Ok)
            except FileNotFoundError:
                QMessageBox.warning(self, 'Config Not Found', 'Configuration file not found.', QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}', QMessageBox.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    timer_app.start_timer()
    sys.exit(app.exec_())
