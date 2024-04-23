import sys  # Importing sys module for system-specific parameters and functions
import os  # Importing os module for interacting with the operating system
import json  # Importing json module for working with JSON data
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QSystemTrayIcon, QMenu, QGridLayout, QHBoxLayout, QSizePolicy, QMessageBox  # Importing PyQt5 modules for GUI
from PyQt5.QtCore import QTimer, Qt  # Importing QTimer and Qt from PyQt5.QtCore for handling time and Qt constants
from PyQt5.QtGui import QIcon, QFont, QFontDatabase  # Importing QIcon, QFont, QFontDatabase from PyQt5.QtGui for handling icons and fonts

# Constants for application
FONT_PATH = "C:/Windows/Fonts/segoeui.ttf"  # Path to the font file
FONT_NAME = "Segoe UI Variable"  # Name of the font
FONT_SIZE = 14  # Size of the font
ICON_PATH = "clock.png"  # Path to the application icon
APP_TITLE = "2omer"  # Title of the application
APP_WIDTH = 450  # Width of the application window
APP_HEIGHT = 250  # Height of the application window
DEFAULT_FOCUS_MINS = 20  # Default focus period minutes
DEFAULT_FOCUS_SECS = 0  # Default focus period seconds
DEFAULT_BREAK_MINS = 0  # Default break period minutes
DEFAULT_BREAK_SECS = 20  # Default break period seconds
TIMER_INTERVAL = 1000  # Timer interval in milliseconds
SPINBOX_WIDTH = 60  # Width of the spin boxes
SETTINGS_FILE = os.path.join(os.getenv('APPDATA'), "timer_settings.json")  # Path to the settings JSON file in appdata

# Main application class
class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE}: {DEFAULT_FOCUS_MINS:02}:{DEFAULT_FOCUS_SECS:02}")  # Setting window title
        self.setGeometry(100, 100, APP_WIDTH, APP_HEIGHT)  # Setting window geometry
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)  # Fixing window size
        self.load_font()  # Loading custom font
        self.init_period_values()  # Initializing period values
        self.timer = QTimer(self)  # Creating QTimer instance
        self.timer.timeout.connect(self.update_timer)  # Connecting timer timeout signal to update_timer method
        self.timer.timeout.connect(self.update_tooltip)  # Connecting timer timeout signal to update_tooltip method
        self.setup_ui()  # Setting up UI elements
        self.add_system_tray_icon()  # Adding system tray icon
        
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
        self.time_left = self.focus_minutes * 60 + self.focus_seconds  # Calculating total time left
        self.is_focus_period = True  # Flag to indicate whether it's focus period

    def load_font(self):
        QFontDatabase.addApplicationFont(FONT_PATH)  # Loading custom font from file

    def setup_ui(self):
        layout = QVBoxLayout()  # Creating vertical layout
        self.setup_period_display(layout)  # Setting up period display
        self.setup_time_input(layout)  # Setting up time input controls
        self.setup_buttons(layout)  # Setting up buttons
        self.setLayout(layout)  # Setting main layout

    def setup_period_display(self, layout):
        self.period_label = self.create_label("", alignment=Qt.AlignCenter, font_name=FONT_NAME, font_size=FONT_SIZE)  # Creating label for period display
        layout.addWidget(self.period_label)  # Adding period label to layout

    def setup_time_input(self, layout):
        grid_layout = QGridLayout()  # Creating grid layout
        grid_layout.addWidget(self.create_label("Focus Period:"), 1, 0, Qt.AlignLeft)  # Adding label for focus period
        grid_layout.addWidget(self.create_label("Break Period:"), 2, 0, Qt.AlignLeft)  # Adding label for break period
        # Creating spin boxes for focus and break periods
        self.focus_minutes_spinbox, self.focus_seconds_spinbox = self.create_period_layout(grid_layout, 1, self.focus_minutes, self.focus_seconds)
        self.break_minutes_spinbox, self.break_seconds_spinbox = self.create_period_layout(grid_layout, 2, self.break_minutes, self.break_seconds)
        layout.addLayout(grid_layout)  # Adding grid layout to main layout

    def create_period_layout(self, layout, row, minutes, seconds):
        period_layout = QHBoxLayout()  # Creating horizontal layout
        minutes_spinbox = self.create_spinbox(minutes, "", 0, 59)  # Creating spin box for minutes
        period_layout.addWidget(minutes_spinbox)  # Adding minutes spin box to layout
        period_layout.addWidget(self.create_label("minutes"), alignment=Qt.AlignLeft)  # Adding label for minutes
        seconds_spinbox = self.create_spinbox(seconds, "", 0, 59)  # Creating spin box for seconds
        layout.addLayout(period_layout, row, 1)  # Adding period layout to grid layout
        layout.addWidget(seconds_spinbox, row, 2, alignment=Qt.AlignRight)  # Adding seconds spin box to grid layout
        layout.addWidget(self.create_label("seconds"), row, 3, alignment=Qt.AlignLeft)  # Adding label for seconds to grid layout
        return minutes_spinbox, seconds_spinbox  # Returning spin boxes

    def setup_buttons(self, layout):
        # Creating start and reset buttons
        self.start_button = self.create_button("Start", self.start_timer)
        self.reset_button = self.create_button("Reset", self.reset_timer)
        layout.addWidget(self.start_button)  # Adding start button to layout
        layout.addWidget(self.reset_button)  # Adding reset button to layout

    def create_button(self, title, function):
        button = QPushButton(title, self)  # Creating QPushButton with given title
        button.clicked.connect(function)  # Connecting button click signal to given function
        return button  # Returning created button

    def create_label(self, text, alignment=None, font_name=None, font_size=None):
        label = QLabel(text)  # Creating QLabel with given text
        if alignment:
            label.setAlignment(alignment)  # Setting alignment if provided
        if font_name and font_size:
            label.setFont(QFont(font_name, font_size))  # Setting font if provided
        return label  # Returning created label

    def create_spinbox(self, value, suffix, min_value, max_value):
        spinbox = QSpinBox(self)  # Creating QSpinBox
        spinbox.setSuffix(suffix)  # Setting suffix for spin box
        spinbox.setRange(min_value, max_value)  # Setting range for spin box
        spinbox.setValue(value)  # Setting initial value for spin box
        spinbox.setFocusPolicy(Qt.StrongFocus)  # Setting focus policy
        spinbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Setting size policy
        spinbox.setFixedWidth(SPINBOX_WIDTH)  # Setting fixed width
        spinbox.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #d4d4d4; border-radius: 5px; background-color: #f0f0f0; }")  # Setting style sheet
        spinbox.valueChanged.connect(self.validate_input)  # Connecting value changed signal to validate_input method
        return spinbox  # Returning created spin box

    def add_system_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)  # Creating QSystemTrayIcon
        self.tray_icon.setIcon(QIcon(self.get_script_dir_path(ICON_PATH)))  # Setting icon for system tray
        tray_menu = QMenu(self)  # Creating menu for system tray
        clear_action = tray_menu.addAction("Clear Config")  # Adding action to clear configuration
        clear_action.triggered.connect(self.clear_config)  # Connecting action to clear_config method
        tray_menu.addSeparator()  # Adding separator in menu
        exit_action = tray_menu.addAction("Exit")  # Adding action to exit application
        exit_action.triggered.connect(self.close)  # Connecting action to close method
        self.tray_icon.setContextMenu(tray_menu)  # Setting context menu for system tray
        self.update_tooltip()  # Updating tooltip for system tray
        self.tray_icon.show()  # Showing system tray icon
        self.setWindowIcon(QIcon(self.get_script_dir_path(ICON_PATH)))  # Setting window icon

    def get_script_dir_path(self, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Getting directory path of script
        return os.path.join(script_dir, filename)  # Returning path by joining directory path and filename

    def start_timer(self):
        self.set_custom_times()  # Setting custom times
        if not self.timer.isActive():
            self.set_period_time()  # Setting period time based on custom input
            self.timer.start(TIMER_INTERVAL)  # Starting timer
            self.start_button.setEnabled(False)  # Disabling start button
            self.save_settings()  # Saving settings when timer starts

    def reset_timer(self):
        self.timer.stop()  # Stopping timer
        self.init_period_values()  # Reinitializing period values
        self.update_timer_display()  # Updating timer display
        self.start_button.setEnabled(True)  # Enabling start button
        self.save_settings()  # Saving settings when timer resets

    def update_timer(self):
        self.time_left -= 1  # Decreasing time left by 1 second
        if self.time_left <= 0:
            self.timer.stop()  # Stopping timer if time left is zero or negative
            self.show_notification()  # Showing notification
            self.switch_period()  # Switching period
            self.set_period_time()  # Setting period time
            self.timer.start(TIMER_INTERVAL)  # Restarting timer
        else:
            self.update_timer_display()  # Updating timer display

    def update_timer_display(self):
        self.setWindowTitle(f"{APP_TITLE}: {self.format_time(self.time_left)}")  # Updating window title
        period = "Focus Period" if self.is_focus_period else "Break Period"  # Determining period
        self.period_label.setText(f"<b>{period}: {self.format_time(self.time_left)}</b>")  # Updating period label

    def set_custom_times(self):
        # Setting custom times from spin boxes
        self.focus_minutes = self.focus_minutes_spinbox.value()
        self.focus_seconds = self.focus_seconds_spinbox.value()
        self.break_minutes = self.break_minutes_spinbox.value()
        self.break_seconds = self.break_seconds_spinbox.value()

    def switch_period(self):
        self.is_focus_period = not self.is_focus_period  # Toggling between focus and break periods
        self.set_period_time()  # Setting period time based on current period

    def set_period_time(self):
        if self.is_focus_period:
            self.time_left = self.focus_minutes * 60 + self.focus_seconds  # Setting time for focus period
        else:
            self.time_left = self.break_minutes * 60 + self.break_seconds  # Setting time for break period

    def show_notification(self):
        notification_title = "2omer"  # Notification title
        period = "break" if self.is_focus_period else "focus period"  # Determining period for notification
        notification_text = f"It's time for a {period}"  # Notification text
        self.tray_icon.showMessage(notification_title, notification_text)  # Showing notification in system tray

    def update_tooltip(self):
        self.tray_icon.setToolTip(self.format_time(self.time_left))  # Updating tooltip for system tray

    def validate_input(self):
        # Disabling start button if any spin box is set to 0
        if (self.focus_minutes_spinbox.value() == 0 and self.focus_seconds_spinbox.value() == 0) \
                or (self.break_minutes_spinbox.value() == 0 and self.break_seconds_spinbox.value() == 0):
            self.start_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)

    def format_time(self, seconds):
        # Formatting time from total seconds to mm:ss format
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def save_settings(self):
        # Saving settings to JSON file
        settings = {
            'focus_minutes': self.focus_minutes,
            'focus_seconds': self.focus_seconds,
            'break_minutes': self.break_minutes,
            'break_seconds': self.break_seconds
        }
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file)

    def clear_config(self):
        # Clearing configuration settings
        reply = QMessageBox.question(self, 'Clear Configuration', 'Are you sure you want to clear the configuration?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(SETTINGS_FILE)  # Removing settings file
                QMessageBox.information(self, 'Config Cleared', 'Configuration cleared successfully.', QMessageBox.Ok)
            except FileNotFoundError:
                QMessageBox.warning(self, 'Config Not Found', 'Configuration file not found.', QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}', QMessageBox.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Creating QApplication instance
    timer_app = TimerApp()  # Creating TimerApp instance
    timer_app.show()  # Showing TimerApp window
    timer_app.start_timer()  # Starting timer
    sys.exit(app.exec_())  # Exiting application with system exit code
