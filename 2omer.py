import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QSystemTrayIcon, QMenu, QGridLayout, QHBoxLayout, QSizePolicy, QMessageBox, QSplashScreen
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QPixmap

# Enable high DPI scaling
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

# Constants for application
FONT_PATH = "C:/Windows/Fonts/segoeui.ttf"
FONT_NAME = "Segoe UI Variable"
ICON_PATH = "clock.png"
SPLASH_PATH = "splash.png"
APP_TITLE = "2omer"
APP_WIDTH = 315
APP_HEIGHT = 150
DEFAULT_FOCUS_MINS = 20
DEFAULT_FOCUS_SECS = 0
DEFAULT_BREAK_MINS = 0
DEFAULT_BREAK_SECS = 20
TIMER_INTERVAL = 1000
SPINBOX_WIDTH = 60
SETTINGS_FILE = os.path.expanduser("~/.timer_settings.json")


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(self.get_script_dir_path(ICON_PATH)))
        self.load_font()
        self.init_period_values()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.timeout.connect(self.update_tooltip)
        self.setup_ui()
        self.add_system_tray_icon()
        self.is_timer_running = False
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)

        # Add splash screen
        self.splash = QSplashScreen(QPixmap(self.get_script_dir_path(SPLASH_PATH)))
        self.splash.show()
        QTimer.singleShot(1000, self.show_main_window)

    def show_main_window(self):
        self.splash.close()
        self.show()

    def init_period_values(self):
        """Initialize the period values."""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
                self.focus_minutes = settings.get('focus_minutes', DEFAULT_FOCUS_MINS)
                self.focus_seconds = settings.get('focus_seconds', DEFAULT_FOCUS_SECS)
                self.break_minutes = settings.get('break_minutes', DEFAULT_BREAK_MINS)
                self.break_seconds = settings.get('break_seconds', DEFAULT_BREAK_SECS)
        else:
            reply = QMessageBox(QMessageBox.Question, 'No existing settings', 'No existing settings where found. You can create to save settings, or ignore to choose everytime')
            reply.addButton('Create', QMessageBox.YesRole)
            reply.addButton('Ignore', QMessageBox.NoRole)
            button = reply.exec_()
            if button == QMessageBox.No:
                sys.exit()
            else:
                self.focus_minutes = DEFAULT_FOCUS_MINS
                self.focus_seconds = DEFAULT_FOCUS_SECS
                self.break_minutes = DEFAULT_BREAK_MINS
                self.break_seconds = DEFAULT_BREAK_SECS
        self.time_left = None
        self.is_focus_period = True

    def load_font(self):
        """Load the custom font."""
        QFontDatabase.addApplicationFont(FONT_PATH)

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        self.setup_period_display(layout)
        self.setup_time_input(layout)
        self.setup_buttons(layout)
        self.setLayout(layout)

    def setup_period_display(self, layout):
        """Set up the period display."""
        self.period_label = self.create_label("<b>Click start to begin</b>", alignment=Qt.AlignCenter, font_name=FONT_NAME)
        layout.addWidget(self.period_label)

    def setup_time_input(self, layout):
        """Set up the time input."""
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.create_label("Focus Period:"), 1, 0, Qt.AlignLeft)
        grid_layout.addWidget(self.create_label("Break Period:"), 2, 0, Qt.AlignLeft)
        self.focus_minutes_spinbox, self.focus_seconds_spinbox = self.create_period_layout(grid_layout, 1, self.focus_minutes, self.focus_seconds)
        self.break_minutes_spinbox, self.break_seconds_spinbox = self.create_period_layout(grid_layout, 2, self.break_minutes, self.break_seconds)
        layout.addLayout(grid_layout)

    def create_period_layout(self, layout, row, minutes, seconds):
        """Create layout for inputting focus and break periods."""
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
        """Set up the buttons."""
        self.control_button = self.create_button("Start", self.control_timer)
        layout.addWidget(self.control_button)

    def create_button(self, title, function):
        """Create a button."""
        button = QPushButton(title, self)
        button.clicked.connect(function)
        return button

    def create_label(self, text, alignment=None, font_name=None):
        """Create a label."""
        label = QLabel(text)
        if alignment:
            label.setAlignment(alignment)
        if font_name:
            label.setFont(QFont(font_name, self.get_font_size()))
        return label

    def get_font_size(self):
        """Calculate the font size based on DPI."""
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        return int((dpi / 96) * 14)

    def create_spinbox(self, value, suffix, min_value, max_value):
        """Create a spinbox."""
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
        """Add system tray icon."""
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
        """Get the path to the file in the script directory."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, filename)

    def control_timer(self):
        """Control the timer."""
        if self.is_timer_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        """Start the timer."""
        self.set_custom_times()
        if not self.timer.isActive():
            self.set_period_time()
            self.timer.start(TIMER_INTERVAL)
            self.control_button.setText("Pause")
            self.is_timer_running = True
            self.save_settings()

    def pause_timer(self):
        """Pause the timer."""
        self.timer.stop()
        self.control_button.setText("Resume")
        self.is_timer_running = False
        self.save_settings()

    def reset_timer(self):
        """Reset the timer."""
        self.timer.stop()
        self.init_period_values()
        self.update_timer_display()
        self.control_button.setText("Start")
        self.is_timer_running = False
        self.save_settings()

    def update_timer(self):
        """Update the timer."""
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
        """Update the timer display."""
        if self.time_left is not None:
            self.setWindowTitle(f"{APP_TITLE}: {self.format_time(self.time_left)}")
            period = "Focus Period" if self.is_focus_period else "Break Period"
            self.period_label.setText(f"<b>{period}: {self.format_time(self.time_left)}</b>")
        else:
            self.setWindowTitle(APP_TITLE)
            self.period_label.setText("<b>Click to Start</b>")

    def set_custom_times(self):
        """Set custom times for focus and break periods."""
        self.focus_minutes = self.focus_minutes_spinbox.value()
        self.focus_seconds = self.focus_seconds_spinbox.value()
        self.break_minutes = self.break_minutes_spinbox.value()
        self.break_seconds = self.break_seconds_spinbox.value()

    def switch_period(self):
        """Switch to the next period."""
        self.is_focus_period = not self.is_focus_period
        self.set_period_time()

    def set_period_time(self):
        """Set the time for the current period."""
        if self.is_focus_period:
            self.time_left = self.focus_minutes * 60 + self.focus_seconds
        else:
            self.time_left = self.break_minutes * 60 + self.break_seconds

    def show_notification(self):
        """Show a notification."""
        period = "Focus" if self.is_focus_period else "Break"
        message = f"It's time for the {period} period."
        QMessageBox.information(self, APP_TITLE, message, QMessageBox.Ok)

    def update_tooltip(self):
        """Update the tooltip for the system tray icon."""
        if self.time_left is not None:
            self.tray_icon.setToolTip(self.format_time(self.time_left))
        else:
            self.tray_icon.setToolTip(APP_TITLE)

    def validate_input(self):
        """Validate input values."""
        if (self.focus_minutes_spinbox.value() == 0 and self.focus_seconds_spinbox.value() == 0) \
                or (self.break_minutes_spinbox.value() == 0 and self.break_seconds_spinbox.value() == 0):
            self.control_button.setEnabled(False)
        else:
            self.control_button.setEnabled(True)

    def format_time(self, seconds):
        """Format time in minutes and seconds."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def save_settings(self):
        """Save current settings to the settings file."""
        settings = {
            'focus_minutes': self.focus_minutes,
            'focus_seconds': self.focus_seconds,
            'break_minutes': self.break_minutes,
            'break_seconds': self.break_seconds
        }
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file)

    def clear_config(self):
        """Clear the configuration."""
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
    sys.exit(app.exec_())
