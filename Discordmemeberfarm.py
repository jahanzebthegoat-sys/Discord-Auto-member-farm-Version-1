import sys
import time
from datetime import datetime
import customtkinter as ctk
import pyautogui
import pyperclip

# Enable high-DPI scaling for crisp text on modern screens
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Fail-safe: slam mouse cursor to any corner to instantly abort
pyautogui.FAILSAFE = True

# App Appearance Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class FarmerCenterV9(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Farmer Center Pro v9.0")
        self.geometry("680x520")
        self.resizable(False, False)
        self.attributes('-topmost', True)  # Always keep window on top

        # State Variables
        self.user_name = ""
        self.target_coords = None
        self.is_running = False
        self.target_interval = 210  # Default 3.5 mins (210s)
        self.remaining_seconds = self.target_interval
        self.timer_id = None
        self.total_sent = 0

        # Start App Flow
        self.show_loading_screen()

    def clear_window(self):
        """Cleans up widgets to switch screens seamlessly."""
        for widget in self.winfo_children():
            widget.destroy()

    # =========================================================================
    # SCREEN 1: ANIMATED LOADING SCREEN
    # =========================================================================
    def show_loading_screen(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both")

        ctk.CTkLabel(frame, text="FARMER CENTER PRO", font=ctk.CTkFont(size=34, weight="bold"), text_color="#3498DB").pack(pady=(150, 5))
        ctk.CTkLabel(frame, text="Initializing Version 9.0 (Polished Build)...", font=ctk.CTkFont(size=13), text_color="#7F8C8D").pack(pady=(0, 20))

        self.progress = ctk.CTkProgressBar(frame, width=320, height=10)
        self.progress.pack()
        self.progress.set(0)

        self.load_step = 0
        self.animate_loading()

    def animate_loading(self):
        self.load_step += 0.03
        self.progress.set(self.load_step)
        if self.load_step < 1.0:
            self.after(30, self.animate_loading)
        else:
            self.show_tnc_screen()

    # =========================================================================
    # SCREEN 2: TERMS AND CONDITIONS
    # =========================================================================
    def show_tnc_screen(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=35, pady=35)

        ctk.CTkLabel(frame, text="Terms and Conditions of Use", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))

        tnc_text = (
            "Welcome to Farmer Center Pro v9.0.\n\n"
            "Please read and acknowledge the following terms before proceeding:\n"
            "1. RESPONSIBILITY: You are fully responsible for all automated actions dispatched by this tool.\n"
            "2. MOUSE & KEYBOARD CONTROL: When executing, the bot moves your mouse and pastes text into your targeted box.\n"
            "3. EMERGENCY STOP: If the bot malfunctions, violently drag your mouse cursor into ANY of the 4 corners of your screen. This triggers the PyAutoGUI fail-safe and aborts instantly.\n"
            "4. CLIPBOARD RESTORATION: Your original copied text/links will automatically be restored after each command is sent.\n\n"
            "Do you accept these terms?"
        )
        
        textbox = ctk.CTkTextbox(frame, width=540, height=200, font=ctk.CTkFont(size=12))
        textbox.pack(pady=10)
        textbox.insert("0.0", tnc_text)
        textbox.configure(state="disabled")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Decline & Exit", fg_color="#E74C3C", hover_color="#C0392B", width=130, command=self.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="I Accept", fg_color="#2ECC71", hover_color="#27AE60", width=130, command=self.show_name_screen).pack(side="left", padx=10)

    # =========================================================================
    # SCREEN 3: USER PROFILE ONBOARDING ("WHAT IS YOUR NAME?")
    # =========================================================================
    def show_name_screen(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both")

        ctk.CTkLabel(frame, text="Profile Setup", font=ctk.CTkFont(size=30, weight="bold"), text_color="#3498DB").pack(pady=(130, 10))
        ctk.CTkLabel(frame, text="What is your name?", font=ctk.CTkFont(size=16)).pack(pady=(0, 20))

        self.name_entry = ctk.CTkEntry(frame, placeholder_text="Enter your name...", width=260, height=40, font=ctk.CTkFont(size=14))
        self.name_entry.pack(pady=10)
        self.name_entry.focus()

        ctk.CTkButton(frame, text="Launch Dashboard", height=40, width=160, font=ctk.CTkFont(weight="bold"), command=self.save_name).pack(pady=20)

    def save_name(self):
        name = self.name_entry.get().strip()
        self.user_name = name if name else "Farmer"
        self.show_main_dashboard()

    # =========================================================================
    # SCREEN 4: CLEAN STREAMLINED DASHBOARD
    # =========================================================================
    def show_main_dashboard(self):
        self.clear_window()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Bar
        header = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#1A1A1A")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        ctk.CTkLabel(header, text=f"Welcome back, {self.user_name}!", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3498DB").pack(side="left", padx=20, pady=10)
        self.lbl_counter = ctk.CTkLabel(header, text="Sent: 0", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ECC71")
        self.lbl_counter.pack(side="right", padx=20, pady=10)

        # LEFT PANEL (CONFIGURATION)
        left_panel = ctk.CTkFrame(self, corner_radius=10)
        left_panel.grid(row=1, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        ctk.CTkLabel(left_panel, text="Control Setup", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        # Server ID Input
        self.entry_id = ctk.CTkEntry(left_panel, placeholder_text="Enter Server ID...", width=230, height=35)
        self.entry_id.pack(pady=6)

        # Target Capture Button
        self.btn_target = ctk.CTkButton(left_panel, text="🎯 Set Chat Box Target", fg_color="#8E44AD", hover_color="#732D91", width=230, height=35, command=self.capture_target)
        self.btn_target.pack(pady=6)
        
        self.lbl_coords = ctk.CTkLabel(left_panel, text="Target: Not Set", text_color="#E74C3C", font=ctk.CTkFont(size=11))
        self.lbl_coords.pack(pady=(0, 10))

        # Interval Selector Dropdown
        ctk.CTkLabel(left_panel, text="Interval Time:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 2))
        
        self.interval_options = [
            "1.0 Min (60s)",
            "1.5 Min (90s)",
            "2.0 Min (120s)",
            "2.5 Min (150s)",
            "3.0 Min (180s)",
            "3.5 Min / 3:30 (210s)",
            "4.0 Min (240s)",
            "4.5 Min (270s)",
            "5.0 Min (300s)",
            "5.5 Min (330s)",
            "Custom Time (Sec)"
        ]
        
        self.combo_interval = ctk.CTkOptionMenu(
            left_panel, 
            values=self.interval_options, 
            width=230,
            command=self.on_interval_selected
        )
        self.combo_interval.pack(pady=5)
        self.combo_interval.set("3.5 Min / 3:30 (210s)")

        # Custom Time Entry (hidden by default unless selected)
        self.entry_custom_sec = ctk.CTkEntry(left_panel, placeholder_text="Enter custom seconds...", width=230)

        # Test Macro Button
        ctk.CTkButton(left_panel, text="⚡ Test Macro Once", fg_color="#F39C12", hover_color="#D68910", text_color="black", font=ctk.CTkFont(weight="bold"), width=230, command=self.test_macro).pack(pady=(15, 15))

        # RIGHT PANEL (MONITOR & CONTROLS)
        right_panel = ctk.CTkFrame(self, corner_radius=10, fg_color="#212121")
        right_panel.grid(row=1, column=1, padx=(10, 20), pady=20, sticky="nsew")

        self.lbl_status = ctk.CTkLabel(right_panel, text="IDLE", font=ctk.CTkFont(size=14, weight="bold"), text_color="#7F8C8D")
        self.lbl_status.pack(pady=(20, 0))

        self.lbl_timer = ctk.CTkLabel(right_panel, text="03:30", font=ctk.CTkFont(size=56, weight="bold"), text_color="#3498DB")
        self.lbl_timer.pack(pady=(0, 5))

        self.progress = ctk.CTkProgressBar(right_panel, width=220, height=8)
        self.progress.pack(pady=(0, 10))
        self.progress.set(0)

        # Log Console
        self.console = ctk.CTkTextbox(right_panel, width=250, height=130, font=ctk.CTkFont(family="Consolas", size=11))
        self.console.pack(padx=15, pady=10, fill="both", expand=True)
        self.console.insert("0.0", "System ready.\nLock target & click Start.")
        self.console.configure(state="disabled")

        # Action Buttons
        controls = ctk.CTkFrame(right_panel, fg_color="transparent")
        controls.pack(pady=(0, 15))

        self.btn_start = ctk.CTkButton(controls, text="▶ START", fg_color="#2ECC71", hover_color="#27AE60", text_color="black", font=ctk.CTkFont(weight="bold"), width=105, command=self.start_bot)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(controls, text="⏹ STOP", fg_color="#E74C3C", hover_color="#C0392B", text_color="white", font=ctk.CTkFont(weight="bold"), width=105, state="disabled", command=self.stop_bot)
        self.btn_stop.pack(side="left", padx=5)

    def log(self, message):
        """Timestamped activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.configure(state="normal")
        self.console.insert("end", f"\n[{timestamp}] {message}")
        self.console.see("end")
        self.console.configure(state="disabled")

    def on_interval_selected(self, choice):
        """Handles interval preset selection and toggles custom time box."""
        mapping = {
            "1.0 Min (60s)": 60,
            "1.5 Min (90s)": 90,
            "2.0 Min (120s)": 120,
            "2.5 Min (150s)": 150,
            "3.0 Min (180s)": 180,
            "3.5 Min / 3:30 (210s)": 210,
            "4.0 Min (240s)": 240,
            "4.5 Min (270s)": 270,
            "5.0 Min (300s)": 300,
            "5.5 Min (330s)": 330
        }

        if choice == "Custom Time (Sec)":
            self.entry_custom_sec.pack(pady=5)
            self.log("Custom mode selected. Type seconds into box.")
        else:
            self.entry_custom_sec.pack_forget()
            seconds = mapping.get(choice, 210)
            self.target_interval = seconds
            if not self.is_running:
                self.remaining_seconds = seconds
                self.update_timer_display()
            self.log(f"Interval set to {choice}")

    def update_custom_time(self):
        """Validates custom second input."""
        if self.combo_interval.get() == "Custom Time (Sec)":
            val = self.entry_custom_sec.get().strip()
            try:
                seconds = int(val)
                if seconds < 2:
                    raise ValueError
                self.target_interval = seconds
                return True
            except ValueError:
                self.log("ERROR: Enter valid seconds (>= 2s).")
                return False
        return True

    def capture_target(self):
        """Captures chat box position with a 3-second countdown."""
        self.btn_target.configure(state="disabled")
        self.log("Hover your mouse over the chat box...")
        
        def countdown(count):
            if count > 0:
                self.btn_target.configure(text=f"Capturing in {count}...")
                self.after(1000, countdown, count - 1)
            else:
                x, y = pyautogui.position()
                self.target_coords = (x, y)
                self.btn_target.configure(text="🎯 Reset Chat Target", state="normal")
                self.lbl_coords.configure(text=f"Target Locked: (X:{x}, Y:{y})", text_color="#2ECC71")
                self.log(f"Target locked at X:{x}, Y:{y}")
                self.bell()
                
        countdown(3)

    # =========================================================================
    # CORE MACRO ENGINE (BUG FIXED)
    # =========================================================================
    def execute_macro(self):
        """Executes mouse move, focus, paste, and enter with precise micro-delays."""
        server_id = self.entry_id.get().strip()
        if not server_id:
            self.log("ERROR: Server ID missing!")
            return False
        if not self.target_coords:
            self.log("ERROR: Target chat box not locked!")
            return False

        command = f"!djoin {server_id}"

        # 1. Preserve active clipboard & mouse location
        orig_clip = pyperclip.paste()
        orig_pos = pyautogui.position()

        try:
            # 2. Stage new command
            pyperclip.copy(command)
            time.sleep(0.05)

            # 3. Teleport mouse and click target box
            x, y = self.target_coords
            pyautogui.moveTo(x, y, duration=0.08)
            pyautogui.click()

            # BUG FIX: Wait 0.20s for chat window (e.g. Discord) to gain active focus
            time.sleep(0.20)

            # 4. Inject pasted payload
            modifier = 'command' if sys.platform == 'darwin' else 'ctrl'
            pyautogui.hotkey(modifier, 'v')

            # BUG FIX: Wait 0.15s for pasted text to render before hitting enter
            time.sleep(0.15)
            pyautogui.press('enter')

            # 5. Return mouse & restore user's original clipboard
            pyautogui.moveTo(orig_pos[0], orig_pos[1], duration=0.05)
            time.sleep(0.05)
            pyperclip.copy(orig_clip)

            self.total_sent += 1
            self.lbl_counter.configure(text=f"Sent: {self.total_sent}")
            self.log(f"Command #{self.total_sent} sent: {command}")
            return True

        except Exception as e:
            self.log(f"EXECUTION ERROR: {str(e)}")
            return False

    def test_macro(self):
        if not self.update_custom_time():
            return
        self.log("Testing macro execution once...")
        self.execute_macro()

    def start_bot(self):
        if not self.update_custom_time():
            return

        if not self.entry_id.get().strip() or not self.target_coords:
            self.log("ERROR: Fill Server ID & set Target first.")
            return

        self.is_running = True
        self.remaining_seconds = self.target_interval
        
        # Lock controls during run
        self.entry_id.configure(state="disabled")
        self.btn_target.configure(state="disabled")
        self.combo_interval.configure(state="disabled")
        self.entry_custom_sec.configure(state="disabled")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        
        self.lbl_status.configure(text="ACTIVE", text_color="#2ECC71")
        self.log(f"Automation started ({self.target_interval}s interval).")
        
        # Dispatch immediately on start, then loop
        self.execute_macro()
        self.tick()

    def stop_bot(self):
        self.is_running = False
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        # Unlock controls
        self.entry_id.configure(state="normal")
        self.btn_target.configure(state="normal")
        self.combo_interval.configure(state="normal")
        self.entry_custom_sec.configure(state="normal")
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        
        self.lbl_status.configure(text="STOPPED", text_color="#E74C3C")
        self.progress.set(0)
        self.log("Automation stopped.")

    def update_timer_display(self):
        mins, secs = divmod(self.remaining_seconds, 60)
        self.lbl_timer.configure(text=f"{mins:02d}:{secs:02d}")
        
        if self.target_interval > 0:
            fill_val = 1.0 - (self.remaining_seconds / self.target_interval)
            self.progress.set(fill_val)

    def tick(self):
        if not self.is_running:
            return

        self.update_timer_display()

        if self.remaining_seconds <= 5:
            self.lbl_timer.configure(text_color="#F1C40F")
        else:
            self.lbl_timer.configure(text_color="#3498DB")

        if self.remaining_seconds <= 0:
            self.execute_macro()
            self.remaining_seconds = self.target_interval

        self.remaining_seconds -= 1
        self.timer_id = self.after(1000, self.tick)


if __name__ == "__main__":
    app = FarmerCenterV9()
    app.mainloop()