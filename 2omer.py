import sys  # Import the sys module, which provides access to some variables used or maintained by the Python interpreter and to functions that interact strongly with the interpreter.
import os  # Import the os module, which provides a portable way of using operating system-dependent functionality.
import json  # Import the json module, which enables you to parse JSON (JavaScript Object Notation) strings and files.
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QSystemTrayIcon, QMenu, QGridLayout, QHBoxLayout, QSizePolicy, QMessageBox  # Import various classes from the PyQt5.QtWidgets module, which provides a set of UI components for creating desktop applications.
from PyQt5.QtCore import QTimer, Qt  # Import the QTimer and Qt classes from the PyQt5.QtCore module, which provides core non-GUI functionality.
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QScreen  # Import classes from the PyQt5.QtGui module, which provides tools for working with graphical user interfaces.

# Enable high DPI scaling
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Set the attribute for enabling high DPI (dots per inch) scaling to True in the QApplication class.

# Constants for application
FONT_PATH = "C:/Windows/Fonts/segoeui.ttf"  # Define the path to the font file.
FONT_NAME = "Segoe UI Variable"  # Define the name of the font to be used.
ICON_PATH = "clock.png"  # Define the path to the application icon file.
APP_TITLE = "2omer"  # Define the title of the application.
APP_WIDTH = 315  # Define the width of the application window.
APP_HEIGHT = 150  # Define the height of the application window.
DEFAULT_FOCUS_MINS = 20  # Define the default focus period minutes.
DEFAULT_FOCUS_SECS = 0  # Define the default focus period seconds.
DEFAULT_BREAK_MINS = 0  # Define the default break period minutes.
DEFAULT_BREAK_SECS = 20  # Define the default break period seconds.
TIMER_INTERVAL = 1000  # Define the interval (in milliseconds) for the timer.
SPINBOX_WIDTH = 60  # Define the width of the spinbox widgets.
SETTINGS_FILE = os.path.expanduser("~/.timer_settings.json")  # Define the path to the settings file.

# Main application class
class TimerApp(QWidget):
    def __init__(self):
        super().__init__()  # Call the constructor of the base class.
        self.setWindowTitle(APP_TITLE)  # Set the title of the application window.
        self.setWindowIcon(QIcon(self.get_script_dir_path(ICON_PATH)))  # Set the icon of the application window.
        self.load_font()  # Load the custom font.
        self.init_period_values()  # Initialize the period values.
        self.timer = QTimer(self)  # Create a QTimer object.
        self.timer.timeout.connect(self.update_timer)  # Connect the timer's timeout signal to the update_timer method.
        self.timer.timeout.connect(self.update_tooltip)  # Connect the timer's timeout signal to the update_tooltip method.
        self.setup_ui()  # Set up the user interface.
        self.add_system_tray_icon()  # Add the system tray icon.
        self.is_timer_running = False  # Set the timer running status to False.
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)  # Set the fixed size of the application window.

    def init_period_values(self):
        """Initialize the period values."""
        if os.path.exists(SETTINGS_FILE):  # Check if the settings file exists.
            with open(SETTINGS_FILE, 'r') as file:  # Open the settings file for reading.
                settings = json.load(file)  # Load the settings from the file.
                # Get the focus and break period values from the settings file, or use defaults if not present.
                self.focus_minutes = settings.get('focus_minutes', DEFAULT_FOCUS_MINS)
                self.focus_seconds = settings.get('focus_seconds', DEFAULT_FOCUS_SECS)
                self.break_minutes = settings.get('break_minutes', DEFAULT_BREAK_MINS)
                self.break_seconds = settings.get('break_seconds', DEFAULT_BREAK_SECS)
        else:  # If the settings file doesn't exist.
            # Prompt the user to create or ignore settings.
            reply = QMessageBox(QMessageBox.Question, 'No existing settings', 'No existing settings where found. You can create to save settings, or ignore to choose everytime')
            reply.addButton('Create', QMessageBox.YesRole)
            reply.addButton('Ignore', QMessageBox.NoRole)
            button = reply.exec_()
            if button == QMessageBox.No:  # If the user chooses to ignore.
                sys.exit()  # Exit the application.
            else:  # If the user chooses to create settings.
                # Set default period values.
                self.focus_minutes = DEFAULT_FOCUS_MINS
                self.focus_seconds = DEFAULT_FOCUS_SECS
                self.break_minutes = DEFAULT_BREAK_MINS
                self.break_seconds = DEFAULT_BREAK_SECS
        self.time_left = None  # Initialize the time left.
        self.is_focus_period = True  # Set the focus period flag to True.

    def load_font(self):
        """Load the custom font."""
        QFontDatabase.addApplicationFont(FONT_PATH)  # Add the custom font to the application font database.

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()  # Create a vertical box layout.
        self.setup_period_display(layout)  # Set up the period display.
        self.setup_time_input(layout)  # Set up the time input.
        self.setup_buttons(layout)  # Set up the buttons.
        self.setLayout(layout)  # Set the main layout of the widget.

    def setup_period_display(self, layout):
        """Set up the period display."""
        self.period_label = self.create_label("<b>Click start to begin</b>", alignment=Qt.AlignCenter, font_name=FONT_NAME)  # Create a label for displaying the current period.
        layout.addWidget(self.period_label)  # Add the label to the layout.

    def setup_time_input(self, layout):
        """Set up the time input."""
        grid_layout = QGridLayout()  # Create a grid layout for time input.
        grid_layout.addWidget(self.create_label("Focus Period:"), 1, 0, Qt.AlignLeft)  # Add label for focus period.
        grid_layout.addWidget(self.create_label("Break Period:"), 2, 0, Qt.AlignLeft)  # Add label for break period.
        # Create spinboxes for inputting focus and break periods.
        self.focus_minutes_spinbox, self.focus_seconds_spinbox = self.create_period_layout(grid_layout, 1, self.focus_minutes, self.focus_seconds)
        self.break_minutes_spinbox, self.break_seconds_spinbox = self.create_period_layout(grid_layout, 2, self.break_minutes, self.break_seconds)
        layout.addLayout(grid_layout)  # Add the grid layout to the main layout.

    def create_period_layout(self, layout, row, minutes, seconds):
        """Create layout for inputting focus and break periods."""
        period_layout = QHBoxLayout()  # Create a horizontal box layout.
        minutes_spinbox = self.create_spinbox(minutes, "", 0, 59)  # Create spinbox for minutes.
        period_layout.addWidget(minutes_spinbox)  # Add minutes spinbox to layout.
        period_layout.addWidget(self.create_label("minutes"), alignment=Qt.AlignLeft)  # Add label for minutes.
        seconds_spinbox = self.create_spinbox(seconds, "", 0, 59)  # Create spinbox for seconds.
        layout.addLayout(period_layout, row, 1)  # Add minutes spinbox layout to grid layout.
        layout.addWidget(seconds_spinbox, row, 2, alignment=Qt.AlignRight)  # Add seconds spinbox to grid layout.
        layout.addWidget(self.create_label("seconds"), row, 3, alignment=Qt.AlignLeft)  # Add label for seconds to grid layout.
        return minutes_spinbox, seconds_spinbox  # Return spinboxes.

    def setup_buttons(self, layout):
        """Set up the buttons."""
        self.control_button = self.create_button("Start", self.control_timer)  # Create a button for controlling the timer.
        layout.addWidget(self.control_button)  # Add the button to the layout.

    def create_button(self, title, function):
        """Create a button."""
        button = QPushButton(title, self)  # Create a QPushButton with specified title.
        button.clicked.connect(function)  # Connect the button's clicked signal to the specified function.
        return button  # Return the created button.

    def create_label(self, text, alignment=None, font_name=None):
        """Create a label."""
        label = QLabel(text)  # Create a QLabel with specified text.
        if alignment:  # If alignment is specified.
            label.setAlignment(alignment)  # Set the alignment of the label.
        if font_name:  # If font name is specified.
            label.setFont(QFont(font_name, self.get_font_size()))  # Set the font of the label.
        return label  # Return the created label.

    def get_font_size(self):
        """Calculate the font size based on DPI."""
        screen = QApplication.primaryScreen()  # Get the primary screen.
        dpi = screen.logicalDotsPerInch()  # Get the logical dots per inch of the screen.
        return int((dpi / 96) * 14)  # Calculate and return the font size based on DPI.

    def create_spinbox(self, value, suffix, min_value, max_value):
        """Create a spinbox."""
        spinbox = QSpinBox(self)  # Create a QSpinBox.
        spinbox.setSuffix(suffix)  # Set the suffix for the spinbox.
        spinbox.setRange(min_value, max_value)  # Set the range of values for the spinbox.
        spinbox.setValue(value)  # Set the initial value of the spinbox.
        spinbox.setFocusPolicy(Qt.StrongFocus)  # Set the focus policy of the spinbox.
        spinbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set the size policy of the spinbox.
        spinbox.setFixedWidth(SPINBOX_WIDTH)  # Set the fixed width of the spinbox.
        spinbox.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #d4d4d4; border-radius: 5px; background-color: #f0f0f0; }")  # Set the stylesheet for the spinbox.
        spinbox.valueChanged.connect(self.validate_input)  # Connect the valueChanged signal of the spinbox to the validate_input method.
        return spinbox  # Return the created spinbox.

    def add_system_tray_icon(self):
        """Add system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)  # Create a QSystemTrayIcon.
        self.tray_icon.setIcon(QIcon(self.get_script_dir_path(ICON_PATH)))  # Set the icon for the system tray icon.
        tray_menu = QMenu(self)  # Create a menu for the system tray icon.
        clear_action = tray_menu.addAction("Clear Config")  # Add an action to clear configuration to the menu.
        clear_action.triggered.connect(self.clear_config)  # Connect the action's triggered signal to the clear_config method.
        tray_menu.addSeparator()  # Add a separator to the menu.
        exit_action = tray_menu.addAction("Exit")  # Add an action to exit the application to the menu.
        exit_action.triggered.connect(self.close)  # Connect the action's triggered signal to the close method.
        self.tray_icon.setContextMenu(tray_menu)  # Set the context menu for the system tray icon.
        self.update_tooltip()  # Update the tooltip for the system tray icon.
        self.tray_icon.show()  # Show the system tray icon.
        self.setWindowIcon(QIcon(self.get_script_dir_path(ICON_PATH)))  # Set the application icon.

    def get_script_dir_path(self, filename):
        """Get the path to the file in the script directory."""
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script.
        return os.path.join(script_dir, filename)  # Return the path to the file in the script directory.

    def control_timer(self):
        """Control the timer."""
        if self.is_timer_running:  # If the timer is running.
            self.pause_timer()  # Pause the timer.
        else:  # If the timer is not running.
            self.start_timer()  # Start the timer.

    def start_timer(self):
        """Start the timer."""
        self.set_custom_times()  # Set custom times for focus and break periods.
        if not self.timer.isActive():  # If the timer is not active.
            self.set_period_time()  # Set the period time.
            self.timer.start(TIMER_INTERVAL)  # Start the timer with the specified interval.
            self.control_button.setText("Pause")  # Set the text of the control button to "Pause".
            self.is_timer_running = True  # Set the timer running status to True.
            self.save_settings()  # Save the current settings.

    def pause_timer(self):
        """Pause the timer."""
        self.timer.stop()  # Stop the timer.
        self.control_button.setText("Resume")  # Set the text of the control button to "Resume".
        self.is_timer_running = False  # Set the timer running status to False.
        self.save_settings()  # Save the current settings.

    def reset_timer(self):
        """Reset the timer."""
        self.timer.stop()  # Stop the timer.
        self.init_period_values()  # Reinitialize the period values.
        self.update_timer_display()  # Update the timer display.
        self.control_button.setText("Start")  # Set the text of the control button to "Start".
        self.is_timer_running = False  # Set the timer running status to False.
        self.save_settings()  # Save the current settings.

    def update_timer(self):
        """Update the timer."""
        self.time_left -= 1  # Decrement the time left.
        if self.time_left <= 0:  # If time is up.
            self.timer.stop()  # Stop the timer.
            self.show_notification()  # Show a notification.
            self.switch_period()  # Switch to the next period.
            self.set_period_time()  # Set the time for the new period.
            self.timer.start(TIMER_INTERVAL)  # Restart the timer.
        else:  # If time is not up.
            self.update_timer_display()  # Update the timer display.

    def update_timer_display(self):
        """Update the timer display."""
        if self.time_left is not None:  # If time left is set.
            self.setWindowTitle(f"{APP_TITLE}: {self.format_time(self.time_left)}")  # Update the window title.
            period = "Focus Period" if self.is_focus_period else "Break Period"  # Determine the current period.
            self.period_label.setText(f"<b>{period}: {self.format_time(self.time_left)}</b>")  # Update the period label.
        else:  # If time left is not set.
            self.setWindowTitle(APP_TITLE)  # Set default window title.
            self.period_label.setText("<b>Click to Start</b>")  # Set default text for period label.

    def set_custom_times(self):
        """Set custom times for focus and break periods."""
        self.focus_minutes = self.focus_minutes_spinbox.value()  # Get the value of focus minutes from spinbox.
        self.focus_seconds = self.focus_seconds_spinbox.value()  # Get the value of focus seconds from spinbox.
        self.break_minutes = self.break_minutes_spinbox.value()  # Get the value of break minutes from spinbox.
        self.break_seconds = self.break_seconds_spinbox.value()  # Get the value of break seconds from spinbox.

    def switch_period(self):
        """Switch to the next period."""
        self.is_focus_period = not self.is_focus_period  # Toggle the focus period flag.
        self.set_period_time()  # Set the time for the new period.

    def set_period_time(self):
        """Set the time for the current period."""
        if self.is_focus_period:  # If it's focus period.
            self.time_left = self.focus_minutes * 60 + self.focus_seconds  # Set time left for focus period.
        else:  # If it's break period.
            self.time_left = self.break_minutes * 60 + self.break_seconds  # Set time left for break period.

    def show_notification(self):
        """Show a notification."""
        period = "Focus" if self.is_focus_period else "Break"  # Determine the current period.
        message = f"It's time for the {period} period."  # Create notification message.
        notification.notify(title=APP_TITLE, message=message, app_name=APP_TITLE, timeout=5)  # Show the notification.

    def update_tooltip(self):
        """Update the tooltip for the system tray icon."""
        if self.time_left is not None:  # If time left is set.
            self.tray_icon.setToolTip(self.format_time(self.time_left))  # Update tooltip with time left.
        else:  # If time left is not set.
            self.tray_icon.setToolTip(APP_TITLE)  # Set default tooltip.

    def validate_input(self):
        """Validate input values."""
        if (self.focus_minutes_spinbox.value() == 0 and self.focus_seconds_spinbox.value() == 0) \
                or (self.break_minutes_spinbox.value() == 0 and self.break_seconds_spinbox.value() == 0):
            self.control_button.setEnabled(False)  # Disable control button if both periods are zero.
        else:
            self.control_button.setEnabled(True)  # Enable control button if at least one period is non-zero.

    def format_time(self, seconds):
        """Format time in minutes and seconds."""
        minutes = seconds // 60  # Calculate minutes.
        seconds = seconds % 60  # Calculate remaining seconds.
        return f"{minutes:02}:{seconds:02}"  # Format minutes and seconds with leading zeros.

    def save_settings(self):
        """Save current settings to the settings file."""
        settings = {
            'focus_minutes': self.focus_minutes,
            'focus_seconds': self.focus_seconds,
            'break_minutes': self.break_minutes,
            'break_seconds': self.break_seconds
        }  # Create dictionary of current settings.
        with open(SETTINGS_FILE, 'w') as file:  # Open the settings file for writing.
            json.dump(settings, file)  # Write the settings to the file.

    def clear_config(self):
        """Clear the configuration."""
        reply = QMessageBox.question(self, 'Clear Configuration', 'Are you sure you want to clear the configuration?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # Prompt the user to confirm clearing the configuration.
        if reply == QMessageBox.Yes:  # If user confirms.
            try:
                os.remove(SETTINGS_FILE)  # Remove the settings file.
                QMessageBox.information(self, 'Config Cleared', 'Configuration cleared successfully.', QMessageBox.Ok)  # Show information message.
            except FileNotFoundError:  # If settings file not found.
                QMessageBox.warning(self, 'Config Not Found', 'Configuration file not found.', QMessageBox.Ok)  # Show warning message.
            except Exception as e:  # If an error occurs.
                QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}', QMessageBox.Ok)  # Show critical error message.

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create an application object.
    timer_app = TimerApp()  # Create an instance of the TimerApp class.
    timer_app.show()  # Show the main window.
    sys.exit(app.exec_())  # Execute the application.
