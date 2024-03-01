import tkinter as tk
from tkinter import simpledialog
from tkinter.ttk import Progressbar, Button, Label, Style
import threading
import winsound

class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("20-20-20 Timer")

        # Configure style
        self.style = Style()
        self.style.theme_use('winnative')

        # Timer label
        self.timer_label = Label(master, text="", font=("Segoe UI", 24))
        self.timer_label.pack(pady=20)

        # Progress bar
        self.progressbar = Progressbar(master, orient="horizontal", mode="determinate", maximum=100)
        self.progressbar.pack(fill="x", padx=20, pady=10)

        # Customize Timer button
        self.customize_button = Button(master, text="Customize Timer", command=self.customize_timer)
        self.customize_button.pack(pady=10)

        # Start/Pause/Resume Timer button
        self.start_button = Button(master, text="Start Timer", command=self.start_pause_timer)
        self.start_button.pack(pady=10)

        # Reset Timer button
        self.reset_button = Button(master, text="Reset Timer", command=self.reset_timer)
        self.reset_button.pack(pady=10)

        # Default work time: 20 minutes
        self.work_time = 20 * 60

        # Default break time: 20 seconds
        self.break_time = 20

        # Timer status
        self.is_running = False
        self.pause = False
        self.thread = None

    def customize_timer(self):
        # Customizing work and break times
        self.work_time = simpledialog.askinteger("Work Time", "Enter work time (minutes): ", initialvalue=20) * 60
        self.break_time = simpledialog.askinteger("Break Time", "Enter break time (seconds): ", initialvalue=20)

    def start_pause_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="Pause Timer")
            self.thread = threading.Thread(target=self.run_timer)
            self.thread.start()
        else:
            self.pause = not self.pause
            if self.pause:
                self.start_button.config(text="Resume Timer")
            else:
                self.start_button.config(text="Pause Timer")

    def run_timer(self):
        while self.is_running:
            if not self.pause:
                self.countdown(self.work_time, "Work Time")
                winsound.Beep(440, 500)  # Beep to notify end of work time

                self.countdown(self.break_time, "Break Time")
                winsound.Beep(440, 500)  # Beep to notify end of break time

    def countdown(self, duration, label_text):
        while duration and self.is_running:
            mins, secs = divmod(duration, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            self.timer_label.config(text=label_text + " - " + timeformat)
            self.master.update()
            time.sleep(1)
            duration -= 1
            self.progressbar.step(1)

    def reset_timer(self):
        # Resetting the timer
        self.is_running = False
        self.pause = False
        self.start_button.config(text="Start Timer")
        self.timer_label.config(text="")
        self.progressbar.stop()
        if self.thread:
            self.thread.join()

def main():
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
