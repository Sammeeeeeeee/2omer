import tkinter as tk
from tkinter import messagebox
import time

class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("20-20-20 Timer")
        self.master.geometry("300x200")
        self.master.resizable(False, False)
        
        self.focus_period = 20 * 60  # Default focus period: 20 minutes
        self.break_period = 20  # Default break period: 20 seconds
        self.time_interval = 1  # Timer update interval: 1 second
        
        self.is_break_time = False
        self.is_running = False
        
        self.timer_label = tk.Label(master, text="", font=("Arial", 24))
        self.timer_label.pack(pady=10)
        
        self.start_button = tk.Button(master, text="Start", command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.pause_button = tk.Button(master, text="Pause", command=self.pause_timer, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(master, text="Reset", command=self.reset_timer, state=tk.DISABLED)
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        self.update_timer()
        
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.run_timer()
        
    def pause_timer(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
        
    def reset_timer(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.is_break_time = False
        self.update_timer()
        
    def run_timer(self):
        if self.is_running:
            self.start_time = time.time()
            self.update_timer()

    def update_timer(self):
        elapsed_time = time.time() - self.start_time
        remaining_time = self.focus_period - elapsed_time if not self.is_break_time else self.break_period - elapsed_time

        if remaining_time <= 0:
            if not self.is_break_time:
                messagebox.showinfo("Focus Period Over", "Take a break now!")
                self.is_break_time = True
            else:
                messagebox.showinfo("Break Over", "Focus time starts now!")
                self.is_break_time = False
            self.update_timer()
        else:
            minutes = int(remaining_time / 60)
            seconds = int(remaining_time % 60)
            timer_text = f"{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=timer_text)
            self.master.after(1000, self.update_timer)  # Schedule the update after 1 second (1000 milliseconds)

def main():
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
