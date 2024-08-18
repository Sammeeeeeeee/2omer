import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox,
    QSystemTrayIcon, QMenu, QGridLayout, QHBoxLayout, QSizePolicy, QMessageBox,
    QSplashScreen, QAction
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QPixmap
from plyer import notification

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

FONT_PATH = "C:/Windows/Fonts/segoeui.ttf"
FONT_NAME = "Segoe UI Variable"
ICON_PATH = "clock.png"
ICO_PATH = "2omer_icon.ico"
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
        self.setup_ui()
        self.add_system_tray_icon()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.timeout.connect(self.update_tooltip)
        
        self.is_timer_running = False
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)

        self.splash = QSplashScreen(QPixmap(self.get_script_dir_path(SPLASH_PATH)))
        self.splash.show()
        QTimer.singleShot(1000, self.show_main_window)

        self.minimize_to_tray = True  # Flag to control minimize vs exit

    def show_main_window(self):
        self.splash.close()
        self.show()
        if self.auto_start:
            self.start_timer()

    def init_period_values(self):
        self.auto_start = False
        self.minimize_notification_shown = False
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
                self.focus_minutes = settings.get('focus_minutes', DEFAULT_FOCUS_MINS)
                self.focus_seconds = settings.get('focus_seconds', DEFAULT_FOCUS_SECS)
                self.break_minutes = settings.get('break_minutes', DEFAULT_BREAK_MINS)
                self.break_seconds = settings.get('break_seconds', DEFAULT_BREAK_SECS)
                self.auto_start = settings.get('auto_start', False)
                self.minimize_notification_shown = settings.get('minimize_notification_shown', False)
        else:
            reply = QMessageBox.question(
                self, 'No existing settings found',
                '<b>No existing settings file was found.</b> Create settings file? This will create a file in your home directory to store preferences between runs.',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                sys.exit()
            self.focus_minutes = DEFAULT_FOCUS_MINS
            self.focus_seconds = DEFAULT_FOCUS_SECS
            self.break_minutes = DEFAULT_BREAK_MINS
            self.break_seconds = DEFAULT_BREAK_SECS
        
        self.time_left = None
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
        self.period_label = self.create_label("<b>Click start to begin</b>", alignment=Qt.AlignCenter, font_name=FONT_NAME)
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
        minutes_spinbox = self.create_spinbox(minutes)
        period_layout.addWidget(minutes_spinbox)
        period_layout.addWidget(self.create_label("minutes"), alignment=Qt.AlignLeft)
        seconds_spinbox = self.create_spinbox(seconds)
        layout.addLayout(period_layout, row, 1)
        layout.addWidget(seconds_spinbox, row, 2, alignment=Qt.AlignRight)
        layout.addWidget(self.create_label("seconds"), row, 3, alignment=Qt.AlignLeft)
        return minutes_spinbox, seconds_spinbox

    def setup_buttons(self, layout):
        self.control_button = self.create_button("Start", self.control_timer)
        layout.addWidget(self.control_button)

    def create_button(self, title, function):
        button = QPushButton(title, self)
        button.clicked.connect(function)
        return button

    def create_label(self, text, alignment=None, font_name=None):
        label = QLabel(text)
        if alignment:
            label.setAlignment(alignment)
        if font_name:
            label.setFont(QFont(font_name, self.get_font_size()))
        return label

    def get_font_size(self):
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        return int((dpi / 96) * 14)

    def create_spinbox(self, value):
        spinbox = QSpinBox(self)
        spinbox.setRange(0, 59)
        spinbox.setValue(value)
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
        
        self.auto_start_action = QAction("Auto Start", self, checkable=True)
        self.auto_start_action.setChecked(self.auto_start)
        self.auto_start_action.triggered.connect(self.toggle_auto_start)
        tray_menu.addAction(self.auto_start_action)
        
        tray_menu.addSeparator()
        restore_action = tray_menu.addAction("Open")
        restore_action.triggered.connect(self.restore_window)
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_application)
        self.tray_icon.setContextMenu(tray_menu)
        
        # Connect the double-click activation signal
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        self.update_tooltip()
        self.tray_icon.show()
        self.setWindowIcon(QIcon(self.get_script_dir_path(ICON_PATH)))

    def get_script_dir_path(self, filename):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    def closeEvent(self, event):
        if self.minimize_to_tray:
            event.ignore()  # Ignore the close event
            self.hide()  # Hide the window
            if not self.minimize_notification_shown:
                self.tray_icon.showMessage("2omer", "The application is minimized to the tray.", QSystemTrayIcon.Information, 2000)
                self.minimize_notification_shown = True
            self.save_settings()
        else:
            event.accept()  # Accept the event to actually close the application

    def restore_window(self):
        self.show()  # Show the main window
        self.raise_()  # Bring the window to the foreground
        self.activateWindow()  # Make sure the window gets focus

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.restore_window()

    def control_timer(self):
        if self.is_timer_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.set_custom_times()
        if not self.timer.isActive():
            self.set_period_time()
            self.timer.start(TIMER_INTERVAL)
            self.control_button.setText("Pause")
            self.is_timer_running = True
            self.save_settings()

    def pause_timer(self):
        self.timer.stop()
        self.control_button.setText("Resume")
        self.is_timer_running = False
        self.save_settings()

    def reset_timer(self):
        self.timer.stop()
        self.init_period_values()
        self.update_timer_display()
        self.control_button.setText("Start")
        self.is_timer_running = False
        self.save_settings()

    def update_timer(self):
        self.time_left -= 1
        if self.time_left <= 0:
            self.timer.stop()
            self.show_notification()
            self.switch_period()
            self.set_period_time()
            self.timer.start(TIMER_INTERVAL)
        self.update_timer_display()

    def update_timer_display(self):
        if self.time_left is not None:
            self.setWindowTitle(f"{APP_TITLE}: {self.format_time(self.time_left)}")
            period = "Focus Period" if self.is_focus_period else "Break Period"
            self.period_label.setText(f"<b>{period}: {self.format_time(self.time_left)}</b>")
        else:
            self.setWindowTitle(APP_TITLE)
            self.period_label.setText("<b>Click to Start</b>")

    def set_custom_times(self):
        self.focus_minutes = self.focus_minutes_spinbox.value()
        self.focus_seconds = self.focus_seconds_spinbox.value()
        self.break_minutes = self.break_minutes_spinbox.value()
        self.break_seconds = self.break_seconds_spinbox.value()

    def switch_period(self):
        self.is_focus_period = not self.is_focus_period
        self.set_period_time()

    def set_period_time(self):
        self.time_left = (self.focus_minutes * 60 + self.focus_seconds) if self.is_focus_period else (self.break_minutes * 60 + self.break_seconds)

    def show_notification(self):
        period = "break" if self.is_focus_period else "focus period"
        self.tray_icon.showMessage("2omer", f"It's time for a {period}")

    def update_tooltip(self):
        self.tray_icon.setToolTip(self.format_time(self.time_left) if self.time_left is not None else APP_TITLE)

    def validate_input(self):
        focus_time = self.focus_minutes_spinbox.value() + self.focus_seconds_spinbox.value()
        break_time = self.break_minutes_spinbox.value() + self.break_seconds_spinbox.value()
        self.control_button.setEnabled(focus_time > 0 and break_time > 0)

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def save_settings(self):
        settings = {
            'focus_minutes': self.focus_minutes,
            'focus_seconds': self.focus_seconds,
            'break_minutes': self.break_minutes,
            'break_seconds': self.break_seconds,
            'auto_start': self.auto_start_action.isChecked(),
            'minimize_notification_shown': self.minimize_notification_shown
        }
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file)

    def clear_config(self):
        reply = QMessageBox.question(
            self, 'Clear Configuration',
            'Are you sure you want to clear the configuration?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                os.remove(SETTINGS_FILE)
                QMessageBox.information(self, 'Config Cleared', 'Configuration cleared successfully.', QMessageBox.Ok)
            except FileNotFoundError:
                QMessageBox.warning(self, 'Config Not Found', 'Configuration file not found.', QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}', QMessageBox.Ok)

    def toggle_auto_start(self):
        self.auto_start = self.auto_start_action.isChecked()
        self.save_settings()

    def exit_application(self):
        self.minimize_to_tray = False
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    sys.exit(app.exec_())
