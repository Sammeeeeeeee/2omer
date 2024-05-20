# 20omer
Customizable 20/20/20 timer, written in Python, using PyQt5 with a focus on reliability and user experience.

<p align="center">
  <img src="https://img.shields.io/github/v/release/Sammeeeeeeee/20omer" alt="GitHub Release">  
  <img src="https://img.shields.io/github/release-date/Sammeeeeeeee/20omer" alt="GitHub Release Date">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Code">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-PyQt5-orange?style=for-the-badge&logo=python" alt="Made with PyQt5">
  <img src="https://img.shields.io/github/license/Sammeeeeeeee/20omer?style=for-the-badge" alt="License">
</p>

## 20omer Timer App
A simple and portable [20-20-20](https://www.rnib.org.uk/your-eyes/how-to-keep-your-eyes-healthy/eye-safety/#:~:text=Taking%20frequent%20breaks%20from%20the,cause%20you%20to%20need%20spectacles.) timer tool to help remind you to rest your eyes when using your PC, built using PyQt5 in Python with plyer notifications for Windows. 

You can customize focus period and break period durations. It features a countdown timer and notifies you when each period ends. Configuration can be saved (or not).

## Usage
![Screenshot](https://github.com/Sammeeeeeeee/20omer/assets/139072031/f1e1e60c-ac17-4699-8eb8-5cccc8834dcc)
- Upon launching the application for the first time, you will get the option to create a configuration file or not. If you do not, it will ask you every time (this is because it checks if the file exists, and if not, it offers). It saves the file in your user's home directory. 
- You can set custom focus and break periods by entering durations into the input fields.
- Click the "Start" button to begin the timer countdown.
- You can pause the timer at any time by clicking the "Pause" button.
- When a focus or break period ends, you will get a notification, and the timer will automatically switch to the next period.
- You can monitor time left in the system tray.
- You can clear the config from the system tray as well. 

## Installation
This isn't designed to be installed. To keep it simple, just set it to auto-start and forget about it. However, we haven't ruled out the option of creating an installer. You can add it to your startup by:
- Press Windows logo key  + R, type shell:startup, then select OK.
- Add a shortcut to 20omer. 

### Easy: Run the EXE
Find the latest release [here](https://github.com/Sammeeeeeeee/20omer/releases "Releases"). Download and run.

### Build

1. Ensure you have Python and git installed on your system.
2. Install the PyQt5 library using pip:
   ```
   pip install PyQt5
   pip install plyer
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

<a href="https://www.flaticon.com/free-icons/time-and-date" title="Time Icon" a>
