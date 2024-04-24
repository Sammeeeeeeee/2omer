# 2omer
Customizable 20/20/20 timer, written in Python, using PyQt5 with a focus on reliability and user experience.

<p align="center">
  <img src="https://img.shields.io/github/v/release/Sammeeeeeeee/2omer" alt="GitHub Release">  
  <img src="https://img.shields.io/github/release-date/Sammeeeeeeee/2omer" alt="GitHub Release Date">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Code">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-PyQt5-orange?style=for-the-badge&logo=python" alt="Made with PyQt5">
  <img src="https://img.shields.io/github/license/Sammeeeeeeee/2omer?style=for-the-badge" alt="License">
</p>

## 2omer Timer App
Simple portable 20 20 20 timer / Pomodoro application to help remind you to rest / relax when using your PC, built using PyQt5 in Python. You can customize focus period and break period durations. It features a countdown timer and notifies you when each period ends. Configuration can be saved (or not).

## Usage
![Screenshot](https://github.com/Sammeeeeeeee/2omer/assets/139072031/f1e1e60c-ac17-4699-8eb8-5cccc8834dcc)
- Upon launching the application for the first time, you will get the option to create a configuration file or not. If you do not, it will ask you every time (this is because it checks if the file exists, and if not, it offers).
- You can set custom focus and break periods by entering durations in the provided input fields.
- Click the "Start" button to begin the timer countdown.
- You can pause the timer at any time by clicking the "Pause" button.
- When a focus or break period ends, a notification alert will pop up, and the timer will automatically switch to the next period.
- You can monitor time left in the system tray (V.2+)
- You can clear the config from the system tray. If you clear the config, it will offer to close. If you do not close, it will recreate the config file if you change the time.

## Versions
The latest version is considered good enough to not warrant needing the older versions' downloads provided here.
However, of course, if needed, they can be found in [releases](https://github.com/Sammeeeeeeee/2omer/releases).

The only version offering pop-up notifications instead of Windows's toast notifications is V1. There are no plans to bring this feature back.

## Features
- Set custom focus and break periods.
- Notification alerts at the end of each period.
- Simple and intuitive user interface.
- Portable
- Ability to save the configuration in a user accessible JSON file
- Tray icon to exit the application or clear the configuration

## Installation
This isn't designed to be installed. To be as simple as possible, just set it to auto-start and forget. However, we have not crossed out the option of creating an installer.

### Easy: Run the EXE
Find the latest release [here](https://github.com/Sammeeeeeeee/2omer/releases "Releases"). Download and run.

### Run manually

1. Ensure you have Python and git installed on your system.
2. Install PyQt5 library using pip:
   ```
   pip install PyQt5
   ```
3. Clone this repository:
   ```
   git clone https://github.com/Sammeeeeeeee/2omer.git
   ```
4. Navigate to the directory:
   ```
   cd 2omer
   ```
5. Run the application:
   ```
   python 2omer.py
   ```

## Credits

<a href="https://www.flaticon.com/free-icons/time-and-date" title="Time
