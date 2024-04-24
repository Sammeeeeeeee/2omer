# Notes: Comments and other parts where made by AI. Use at your own risk. 
import sys  # Importing the sys module allows access to system-specific parameters and functions.
import os  # Importing the os module provides a way of using operating system dependent functionality.
import json  # Importing the json module enables parsing and serializing JSON data.
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox, QSystemTrayIcon, QMenu, QGridLayout, QHBoxLayout, QSizePolicy, QMessageBox, QSplashScreen  # Importing classes from PyQt5.QtWidgets module to create GUI applications.
from PyQt5.QtCore import QTimer, Qt  # Importing classes from PyQt5.QtCore module for handling core functionality.
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QPixmap  # Importing classes from PyQt5.QtGui module for handling GUI elements.

# Enable high DPI scaling
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Enabling high DPI scaling for better resolution on high DPI displays.

# Constants for application
FONT_PATH = "C:/Windows/Fonts/segoeui.ttf"  # Path to the custom font file.
FONT_NAME = "Segoe UI Variable"  # Name of the custom font.
ICON_PATH = "clock.png"  # Path to the application icon file.
SPLASH_PATH = "splash.png"  # Path to the splash screen image file.
APP_TITLE = "2omer"  # Title of the application.
APP_WIDTH = 315  # Width of the application window.
APP_HEIGHT = 150  # Height of the application window.
DEFAULT_FOCUS_MINS = 20  # Default duration for focus period in minutes.
DEFAULT_FOCUS_SECS = 0  # Default duration for focus period in seconds.
DEFAULT_BREAK_MINS = 0  # Default duration for break period in minutes.
DEFAULT_BREAK_SECS = 20  # Default duration for break period in seconds.
TIMER_INTERVAL = 1000  # Timer interval in milliseconds.
SPINBOX_WIDTH = 60  # Width of the spinbox widgets.
SETTINGS_FILE = os.path.expanduser("~/.timer_settings.json")  # File path for storing application settings.

# Define the main application class
class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)  # Set the window title.
        self.setWindowIcon(QIcon(self.get_script_dir_path(ICON_PATH)))  # Set the window icon.
        self.load_font()  # Load the custom font.
        self.init_period_values()  # Initialize period values from settings.
        self.timer = QTimer(self)  # Create a QTimer object for handling time-based events.
        self.timer.timeout.connect(self.update_timer)  # Connect the timeout signal of the timer to the update_timer method.
        self.timer.timeout.connect(self.update_tooltip)  # Connect the timeout signal of the timer to the update_tooltip method.
        self.setup_ui()  # Set up the user interface.
        self.add_system_tray_icon()  # Add system tray icon.
        self.is_timer_running = False  # Flag to track if the timer is running.
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)  # Set fixed size for the application window.

        # Add splash screen
        self.splash = QSplashScreen(QPixmap(self.get_script_dir_path(SPLASH_PATH)))  # Create a splash screen with the specified image.
        self.splash.show()  # Display the splash screen.
        QTimer.singleShot(1000, self.show_main_window)  # Use QTimer to delay the display of the main window.

    # Method to show the main window after the splash screen
    def show_main_window(self):
        self.splash.close()  # Close the splash screen.
        self.show()  # Show the main window.

    # Method to initialize period values from settings or use defaults
    def init_period_values(self):
        """Initialize the period values."""
        if os.path.exists(SETTINGS_FILE):  # Check if settings file exists.
            with open(SETTINGS_FILE, 'r') as file:  # Open the settings file for reading.
                settings = json.load(file)  # Load settings from JSON file.
                self.focus_minutes = settings.get('focus_minutes', DEFAULT_FOCUS_MINS)  # Get focus minutes from settings, or use default.
                self.focus_seconds = settings.get('focus_seconds', DEFAULT_FOCUS_SECS)  # Get focus seconds from settings, or use default.
                self.break_minutes = settings.get('break_minutes', DEFAULT_BREAK_MINS)  # Get break minutes from settings, or use default.
                self.break_seconds = settings.get('break_seconds', DEFAULT_BREAK_SECS)  # Get break seconds from settings, or use default.
        else:
            # If settings file doesn't exist, prompt user to create or ignore settings
            reply = QMessageBox(QMessageBox.Question, 'No existing settings', 'No existing settings were found. You can create to save settings, or ignore to choose every time')
            reply.addButton('Create', QMessageBox.YesRole)
            reply.addButton('Ignore', QMessageBox.NoRole)
            button = reply.exec_()
            if button == QMessageBox.No:  # If user chooses to ignore settings, exit the application.
                sys.exit()
            else:  # If user chooses to create settings, use default values.
                self.focus_minutes = DEFAULT_FOCUS_MINS
                self.focus_seconds = DEFAULT_FOCUS_SECS
                self.break_minutes = DEFAULT_BREAK_MINS
                self.break_seconds = DEFAULT_BREAK_SECS
        self.time_left = None  # Initialize time left to None.
        self.is_focus_period = True  # Set initial period to focus.

    # Method to load the custom font
    def load_font(self):
        """Load the custom font."""
        QFontDatabase.addApplicationFont(FONT_PATH)  # Add custom font to the application font database.

    # Method to set up the user interface
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()  # Create a vertical layout.
        self.setup_period_display(layout)  # Set up the period display.
        self.setup_time_input(layout)  # Set up the time input.
        self.setup_buttons(layout)  # Set up the buttons.
        self.setLayout(layout)  # Set the layout for the widget.

    # Method to set up the period display
    def setup_period_display(self, layout):
        """Set up the period display."""
        self.period_label = self.create_label("<b>Click start to begin</b>", alignment=Qt.AlignCenter, font_name=FONT_NAME)  # Create a label for displaying the current period.
        layout.addWidget(self.period_label)  # Add the label to the layout.

    # Method to set up the time input
    def setup_time_input(self, layout):
        """Set up the time input."""
        grid_layout = QGridLayout()  # Create a grid layout.
        grid_layout.addWidget(self.create_label("Focus Period:"), 1, 0, Qt.AlignLeft)  # Add label for focus period to the grid layout.
        grid_layout.addWidget(self.create_label("Break Period:"), 2, 0, Qt.AlignLeft)  # Add label for break period to the grid layout.
        self.focus_minutes_spinbox, self.focus_seconds_spinbox = self.create_period_layout(grid_layout, 1, self.focus_minutes, self.focus_seconds)  # Create spinboxes for focus period.
        self.break_minutes_spinbox, self.break_seconds_spinbox = self.create_period_layout(grid_layout, 2, self.break_minutes, self.break_seconds)  # Create spinboxes for break period.
        layout.addLayout(grid_layout)  # Add the grid layout to the main layout.

    # Method to create layout for inputting focus and break periods
    def create_period_layout(self, layout, row, minutes, seconds):
        """Create layout for inputting focus and break periods."""
        period_layout = QHBoxLayout()  # Create a horizontal layout.
        minutes_spinbox = self.create_spinbox(minutes, "", 0, 59)  # Create spinbox for minutes.
        period_layout.addWidget(minutes_spinbox)  # Add minutes spinbox to the layout.
        period_layout.addWidget(self.create_label("minutes"), alignment=Qt.AlignLeft)  # Add label for minutes to the layout.
        seconds_spinbox = self.create_spinbox(seconds, "", 0, 59)  # Create spinbox for seconds.
        layout.addLayout(period_layout, row, 1)  # Add minutes spinbox layout to the grid layout.
        layout.addWidget(seconds_spinbox, row, 2, alignment=Qt.AlignRight)  # Add seconds spinbox to the grid layout.
        layout.addWidget(self.create_label("seconds"), row, 3, alignment=Qt.AlignLeft)  # Add label for seconds to the grid layout.
        return minutes_spinbox, seconds_spinbox  # Return spinbox widgets.

    # Method to set up the buttons
    def setup_buttons(self, layout):
        """Set up the buttons."""
        self.control_button = self.create_button("Start", self.control_timer)  # Create a button for controlling the timer.
        layout.addWidget(self.control_button)  # Add the button to the layout.

    # Method to create a button
    def create_button(self, title, function):
        """Create a button."""
        button = QPushButton(title, self)  # Create a QPushButton with specified title.
        button.clicked.connect(function)  # Connect the button click signal to the specified function.
        return button  # Return the created button.

    # Method to create a label
    def create_label(self, text, alignment=None, font_name=None):
        """Create a label."""
        label = QLabel(text)  # Create a QLabel with specified text.
        if alignment:
            label.setAlignment(alignment)  # Set the alignment of the label.
        if font_name:
            label.setFont(QFont(font_name, self.get_font_size()))  # Set the font of the label.
        return label  # Return the created label.

    # Method to calculate font size based on DPI
    def get_font_size(self):
        """Calculate the font size based on DPI."""
        screen = QApplication.primaryScreen()  # Get the primary screen.
        dpi = screen.logicalDotsPerInch()  # Get the DPI of the screen.
        return int((dpi / 96) * 14)  # Calculate and return the font size.

    # Method to create a spinbox
    def create_spinbox(self, value, suffix, min_value, max_value):
        """Create a spinbox."""
        spinbox = QSpinBox(self)  # Create a QSpinBox.
        spinbox.setSuffix(suffix)  # Set the suffix for the spinbox.
        spinbox.setRange(min_value, max_value)  # Set the range of values for the spinbox.
        spinbox.setValue(value)  # Set the initial value of the spinbox.
        spinbox.setFocusPolicy(Qt.StrongFocus)  # Set the focus policy for the spinbox.
        spinbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set the size policy for the spinbox.
        spinbox.setFixedWidth(SPINBOX_WIDTH)  # Set the fixed width of the spinbox.
        spinbox.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #d4d4d4; border-radius: 5px; background-color: #f0f0f0; }")  # Set the stylesheet for the spinbox.
        spinbox.valueChanged.connect(self.validate_input)  # Connect value changed signal to validate_input method.
        return spinbox  # Return the created spinbox.

    # Method to add system tray icon
    def add_system_tray_icon(self):
        """Add system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)  # Create a QSystemTrayIcon.
        self.tray_icon.setIcon(QIcon(self.get_script_dir_path(ICON_PATH)))  # Set the icon for the system tray.
        tray_menu = QMenu(self)  # Create a QMenu for the system tray icon.
        clear_action = tray_menu.addAction("Clear Config")  # Add action to clear configuration to the tray menu.
        clear_action.triggered.connect(self.clear_config)  # Connect the action to the clear_config method.
        tray_menu.addSeparator()  # Add a separator to the tray menu.
        exit_action = tray_menu.addAction("Exit")  # Add action to exit the application to the tray menu.
        exit_action.triggered.connect(self.close)  # Connect the action to close the application.
        self.tray_icon.setContextMenu(tray_menu)  # Set the context menu for the system tray icon.
        self.update_tooltip()  # Update the tooltip for the system tray icon.
        self.tray_icon.show()  # Show the system tray icon.
        self.setWindowIcon(QIcon(self.get_script_dir_path(ICON_PATH)))  # Set the window icon.

    # Method to get the path to a file in the script directory
    def get_script_dir_path(self, filename):
        """Get the path to the file in the script directory."""
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the script directory.
        return os.path.join(script_dir, filename)  # Return the path to the file in the script directory.

    # Method to control the timer
    def control_timer(self):
        """Control the timer."""
        if self.is_timer_running:
            self.pause_timer()  # If timer is running, pause it.
        else:
            self.start_timer()  # If timer is not running, start it.

    # Method to start the timer
    def start_timer(self):
        """Start the timer."""
        self.set_custom_times()  # Set custom times for focus and break periods.
        if not self.timer.isActive():  # Check if timer is not active.
            self.set_period_time()  # Set the time for the current period.
            self.timer.start(TIMER_INTERVAL)  # Start the timer with specified interval.
            self.control_button.setText("Pause")  # Change the button text to "Pause".
            self.is_timer_running = True  # Set timer running flag to True.
            self.save_settings()  # Save current settings.

    # Method to pause the timer
    def pause_timer(self):
        """Pause the timer."""
        self.timer.stop()  # Stop the timer.
        self.control_button.setText("Resume")  # Change the button text to "Resume".
        self.is_timer_running = False  # Set timer running flag to False.
        self.save_settings()  # Save current settings.

    # Method to reset the timer
    def reset_timer(self):
        """Reset the timer."""
        self.timer.stop()  # Stop the timer.
        self.init_period_values()  # Reinitialize period values.
        self.update_timer_display()  # Update the timer display.
        self.control_button.setText("Start")  # Change the button text to "Start".
        self.is_timer_running = False  # Set timer running flag to False.
        self.save_settings()  # Save current settings.

    # Method to update the timer
    def update_timer(self):
        """Update the timer."""
        self.time_left -= 1  # Decrement the time left.
        if self.time_left <= 0:  # If time left is zero or negative.
            self.timer.stop()  # Stop the timer.
            self.show_notification()  # Show a notification.
            self.switch_period()  # Switch to the next period.
            self.set_period_time()  # Set the time for the current period.
            self.timer.start(TIMER_INTERVAL)  # Restart the timer.
        else:
            self.update_timer_display()  # Update the timer display.

    # Method to update the timer display
    def update_timer_display(self):
        """Update the timer display."""
        if self.time_left is not None:  # If time left is not None.
            self.setWindowTitle(f"{APP_TITLE}: {self.format_time(self.time_left)}")  # Set the window title with remaining time.
            period = "Focus Period" if self.is_focus_period else "Break Period"  # Determine the current period.
            self.period_label.setText(f"<b>{period}: {self.format_time(self.time_left)}</b>")  # Update the period label.
        else:
            self.setWindowTitle(APP_TITLE)  # Set the window title to the default title.
            self.period_label.setText("<b>Click to Start</b>")  # Set the period label to default message.

    # Method to set custom times for focus and break periods
    def set_custom_times(self):
        """Set custom times for focus and break periods."""
        self.focus_minutes = self.focus_minutes_spinbox.value()  # Get focus minutes from spinbox.
        self.focus_seconds = self.focus_seconds_spinbox.value()  # Get focus seconds from spinbox.
        self.break_minutes = self.break_minutes_spinbox.value()  # Get break minutes from spinbox.
        self.break_seconds = self.break_seconds_spinbox.value()  # Get break seconds from spinbox.

    # Method to switch to the next period
    def switch_period(self):
        """Switch to the next period."""
        self.is_focus_period = not self.is_focus_period  # Toggle between focus and break periods.
        self.set_period_time()  # Set the time for the current period.

    # Method to set the time for the current period
    def set_period_time(self):
        """Set the time for the current period."""
        if self.is_focus_period:  # If it's focus period.
            self.time_left = self.focus_minutes * 60 + self.focus_seconds  # Calculate total time left for focus period.
        else:  # If it's break period.
            self.time_left = self.break_minutes * 60 + self.break_seconds  # Calculate total time left for break period.

    # Method to show a notification
    def show_notification(self):
        """Show a notification."""
        period = "Focus" if self.is_focus_period else "Break"  # Determine the current period.
        message = f"It's time for the {period} period."  # Compose the notification message.
        QMessageBox.information(self, APP_TITLE, message, QMessageBox.Ok)  # Show the notification dialog.

    # Method to update the tooltip for the system tray icon
    def update_tooltip(self):
        """Update the tooltip for the system tray icon."""
        if self.time_left is not None:  # If time left is not None.
            self.tray_icon.setToolTip(self.format_time(self.time_left))  # Update tooltip with remaining time.
        else:
            self.tray_icon.setToolTip(APP_TITLE)  # Set the default tooltip.

    # Method to validate input values
    def validate_input(self):
        """Validate input values."""
        if (self.focus_minutes_spinbox.value() == 0 and self.focus_seconds_spinbox.value() == 0) \
                or (self.break_minutes_spinbox.value() == 0 and self.break_seconds_spinbox.value() == 0):  # Check if either focus or break period is set to zero.
            self.control_button.setEnabled(False)  # Disable the control button.
        else:
            self.control_button.setEnabled(True)  # Enable the control button.

    # Method to format time in minutes and seconds
    def format_time(self, seconds):
        """Format time in minutes and seconds."""
        minutes = seconds // 60  # Calculate minutes.
        seconds = seconds % 60  # Calculate remaining seconds.
        return f"{minutes:02}:{seconds:02}"  # Return formatted time string.

    # Method to save current settings to the settings file
    def save_settings(self):
        """Save current settings to the settings file."""
        settings = {
            'focus_minutes': self.focus_minutes,  # Save focus minutes.
            'focus_seconds': self.focus_seconds,  # Save focus seconds.
            'break_minutes': self.break_minutes,  # Save break minutes.
            'break_seconds': self.break_seconds  # Save break seconds.
        }
        with open(SETTINGS_FILE, 'w') as file:  # Open settings file for writing.
            json.dump(settings, file)  # Write settings to JSON file.

    # Method to clear the configuration
    def clear_config(self):
        """Clear the configuration."""
        reply = QMessageBox.question(self, 'Clear Configuration', 'Are you sure you want to clear the configuration?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # Ask for confirmation to clear configuration.
        if reply == QMessageBox.Yes:  # If user confirms to clear configuration.
            try:
                os.remove(SETTINGS_FILE)  # Remove the settings file.
                QMessageBox.information(self, 'Config Cleared', 'Configuration cleared successfully.', QMessageBox.Ok)  # Show success message.
            except FileNotFoundError:  # If settings file not found.
                QMessageBox.warning(self, 'Config Not Found', 'Configuration file not found.', QMessageBox.Ok)  # Show warning message.
            except Exception as e:  # Handle other exceptions.
                QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}', QMessageBox.Ok)  # Show error message.


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create a PyQt application object.
    timer_app = TimerApp()  # Create an instance of the TimerApp class.
    sys.exit(app.exec_())  # Execute the application.
