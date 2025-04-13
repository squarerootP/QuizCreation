from tkinter import Tk, Label, Button, StringVar, Frame, messagebox, Checkbutton, IntVar, ttk, PhotoImage, Menu, Toplevel
import random
import re
import pickle
import os
from tkinter import font as tkfont

class QuizWindow:
    def __init__(self, master, question_dict):
        self.master = master
        self.master.title("Quiz Master")
        self.master.geometry("1000x700")  # Slightly larger window for better spacing
        self.master.configure(bg="#f5f7fa")  # Lighter, more modern background
        
        # Set application icon (if available)
        try:
            self.master.iconbitmap("quiz_icon.ico")
        except:
            pass
        
        # Configure custom fonts
        self.custom_font = tkfont.Font(family="Segoe UI", size=11)
        self.header_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.question_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.option_font = tkfont.Font(family="Segoe UI", size=13)
        self.result_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        
        # Configure a theme with more modern styling
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a more modern theme if available
        self.style.configure("TFrame", background="#f5f7fa")
        self.style.configure("TButton", font=("Segoe UI", 11, "bold"), borderwidth=1)
        self.style.configure("TCheckbutton", background="#f5f7fa")
        
        # Create menu bar with modern styling
        self.menu_bar = Menu(self.master)
        self.master.config(menu=self.menu_bar)
        
        # Add File menu with icons (if available)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Save Progress", command=self.save_checkpoint, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Load Progress", command=self.load_checkpoint, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Review Incorrect Questions", command=self.review_incorrect_questions)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.master.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Add Help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        # Center window on screen
        self.center_window()
        
        # Bind fullscreen toggle
        self.master.bind("<F11>", self.toggle_fullscreen)
        self.fullscreen = False
        
        # Checkpoint path
        self.checkpoint_path = r"quiz_checkpoint.dat"
        # Path for incorrect questions
        self.incorrect_questions_path = r"incorrect_questions.txt"
        
        # Quiz state
        self.question_dict = question_dict
        self.score = 0
        self.question_index = 0
        self.total_questions = len(question_dict)
        self.current_question = StringVar()
        self.progress_text = StringVar()
        self.selected_answers = []
        self.incorrect_questions = []
        self.result_var = StringVar()
        self.result_var.set("")
        self.answered_questions = set()  # Keep track of which questions have been answered

        # Main container with shadow effect
        self.main_frame = Frame(self.master, bg="#f5f7fa")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Header with progress - more modern styling
        self.header_frame = Frame(self.main_frame, bg="#e8eef7", padx=10, pady=10)
        self.header_frame.pack(fill="x", pady=10)
        
        # Progress indicator with percentage
        self.progress_frame = Frame(self.header_frame, bg="#e8eef7")
        self.progress_frame.pack(side="left", padx=10)
        
        self.progress_label = Label(
            self.progress_frame, 
            textvariable=self.progress_text,
            font=self.custom_font,
            bg="#e8eef7",
            fg="#333333"
        )
        self.progress_label.pack(side="top", anchor="w")
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            orient="horizontal", 
            length=200, 
            mode="determinate"
        )
        self.progress_bar.pack(side="top", pady=5, anchor="w")
        
        # Score display with improved styling
        self.score_frame = Frame(self.header_frame, bg="#e8eef7")
        self.score_frame.pack(side="right", padx=10)
        
        self.score_label = Label(
            self.score_frame,
            text=f"Score: {self.score}/{self.total_questions}",
            font=self.custom_font,
            bg="#e8eef7",
            fg="#333333"
        )
        self.score_label.pack(side="top")
        
        self.score_percentage = Label(
            self.score_frame,
            text=f"({0:.1f}%)" if self.total_questions == 0 else f"({(self.score/self.total_questions)*100:.1f}%)",
            font=("Segoe UI", 9),
            bg="#e8eef7",
            fg="#555555"
        )
        self.score_percentage.pack(side="top")
        
        # Question section with card-like styling
        self.question_frame = Frame(self.main_frame, bg="#ffffff", bd=1, relief="solid", padx=15, pady=15)
        self.question_frame.pack(fill="x", pady=10)
        
        # Question number label
        self.question_number = Label(
            self.question_frame,
            text=f"Question {self.question_index + 1}",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#666666"
        )
        self.question_number.pack(anchor="w", pady=(0, 5))
        
        # Question text with better wrapping
        self.question_label = Label(
            self.question_frame, 
            textvariable=self.current_question, 
            wraplength=900, 
            font=self.question_font,
            bg="#ffffff",
            fg="#222222",
            justify="left"
        )
        self.question_label.pack(anchor="w")

        # Options section with modern card styling
        self.options_frame = Frame(self.main_frame, bg="#f5f7fa", bd=0)
        self.options_frame.pack(fill="both", expand=True, pady=10)
        
        # Result feedback with improved styling
        self.result_frame = Frame(self.main_frame, bg="#f5f7fa", padx=10, pady=5)
        self.result_frame.pack(fill="x", pady=5)
        
        self.result_label = Label(
            self.result_frame, 
            textvariable=self.result_var, 
            font=self.result_font,
            bg="#f5f7fa"
        )
        self.result_label.pack(pady=5)
        
        # Controls with modern button styling
        self.controls_frame = Frame(self.main_frame, bg="#f5f7fa")
        self.controls_frame.pack(fill="x", pady=10)
        
        # Button frame
        self.button_frame = Frame(self.controls_frame, bg="#f5f7fa")
        self.button_frame.pack(side="right", padx=10)

        self.prev_button = Button(
            self.button_frame, 
            text="← Previous",
            command=self.prev_question,
            bg="#9e9e9e",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            relief="flat",
            activebackground="#8e8e8e",
            activeforeground="white"
        )
        self.prev_button.pack(side="left", padx=5)

        self.submit_button = Button(
            self.button_frame, 
            text="Submit Answer",
            command=self.submit_answer,
            bg="#4caf50",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            relief="flat",
            activebackground="#43a047",
            activeforeground="white"
        )
        self.submit_button.pack(side="left", padx=5)

        self.next_button = Button(
            self.button_frame, 
            text="Next →",
            command=self.next_question,
            bg="#2196f3",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            relief="flat",
            activebackground="#1e88e5",
            activeforeground="white"
        )
        self.next_button.pack(side="left", padx=5)
        
        # Keyboard shortcuts info - more subtle placement
        self.shortcut_frame = Frame(self.controls_frame, bg="#f5f7fa")
        self.shortcut_frame.pack(side="left", padx=10)
        
        self.shortcut_label = Label(
            self.shortcut_frame,
            text="Press ? for keyboard shortcuts",
            font=("Segoe UI", 8),
            bg="#f5f7fa",
            fg="#888888"
        )
        self.shortcut_label.pack(side="left")

        # Set up keyboard shortcuts
        self.master.bind("<Right>", lambda event: self.next_question())
        self.master.bind("<Left>", lambda event: self.prev_question())
        self.master.bind("1", lambda event: self.toggle_option(0))
        self.master.bind("2", lambda event: self.toggle_option(1))
        self.master.bind("3", lambda event: self.toggle_option(2))
        self.master.bind("4", lambda event: self.toggle_option(3))
        self.master.bind("<Return>", lambda event: self.submit_answer())
        self.master.bind("<space>", lambda event: self.submit_answer())
        self.master.bind("<Control-s>", lambda event: self.save_checkpoint())
        self.master.bind("<Control-o>", lambda event: self.load_checkpoint())
        self.master.bind("?", lambda event: self.show_shortcuts())

        # Now that all UI elements are created, update the progress text and bar
        self.update_progress_text()
        self.load_question()
    
    def center_window(self):
        """Center the window on the screen"""
        self.master.update_idletasks()
        
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = 1000
        window_height = 700
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y-60}")
    
    def update_progress_text(self):
        self.progress_text.set(f"Question {self.question_index + 1} of {self.total_questions}")
        if hasattr(self, 'question_number'):
            self.question_number.config(text=f"Question {self.question_index + 1}")
        self.update_progress_bar()
        
    def update_progress_bar(self):
        progress = (self.question_index / self.total_questions) * 100 if self.total_questions > 0 else 0
        self.progress_bar["value"] = progress
    
    def update_score_display(self):
        self.score_label.config(text=f"Score: {self.score}/{self.total_questions}")
        percentage = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
        self.score_percentage.config(text=f"({percentage:.1f}%)")

    def toggle_option(self, index):
        """Toggle the checkbox at the given index if it exists"""
        if hasattr(self, 'answer_vars') and index < len(self.answer_vars):
            current_value = self.answer_vars[index].get()
            self.answer_vars[index].set(1 - current_value)  # Toggle between 0 and 1
            
            # Visual feedback when toggling
            if current_value == 0:
                self.option_frames[index].config(bg="#e3f2fd")  # Light blue when selected
                self.checkbuttons[index].config(bg="#e3f2fd")
            else:
                self.option_frames[index].config(bg="#f8f9fa")  # Default background
                self.checkbuttons[index].config(bg="#f8f9fa")
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        self.master.attributes("-fullscreen", self.fullscreen)
        return "break"
    
    def show_shortcuts(self):
        """Show keyboard shortcuts in a popup"""
        shortcuts_window = Toplevel(self.master)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("400x450")
        shortcuts_window.configure(bg="#ffffff")
        shortcuts_window.resizable(False, False)
        
        # Center the window
        shortcuts_window.update_idletasks()
        width = shortcuts_window.winfo_width()
        height = shortcuts_window.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        shortcuts_window.geometry(f'+{x}+{y}')
        
        # Header
        header_frame = Frame(shortcuts_window, bg="#2196f3", padx=10, pady=10)
        header_frame.pack(fill="x")
        
        header_label = Label(
            header_frame,
            text="Keyboard Shortcuts",
            font=("Segoe UI", 14, "bold"),
            bg="#2196f3",
            fg="white"
        )
        header_label.pack()
        
        # Content
        content_frame = Frame(shortcuts_window, bg="#ffffff", padx=20, pady=15)
        content_frame.pack(fill="both", expand=True)
        
        shortcuts = [
            ("1-4", "Select answer options"),
            ("Enter / Space", "Submit answer"),
            ("→", "Next question"),
            ("←", "Previous question"),
            ("Ctrl+S", "Save progress"),
            ("Ctrl+O", "Load progress"),
            ("F11", "Toggle fullscreen"),
            ("?", "Show this help")
        ]
        
        for key, description in shortcuts:
            shortcut_frame = Frame(content_frame, bg="#ffffff", pady=5)
            shortcut_frame.pack(fill="x")
            
            key_label = Label(
                shortcut_frame,
                text=key,
                font=("Segoe UI", 11, "bold"),
                bg="#ffffff",
                fg="#2196f3",
                width=12,
                anchor="w"
            )
            key_label.pack(side="left")
            
            desc_label = Label(
                shortcut_frame,
                text=description,
                font=("Segoe UI", 11),
                bg="#ffffff",
                fg="#333333",
                anchor="w"
            )
            desc_label.pack(side="left", fill="x", expand=True)
        
        # Close button
        close_button = Button(
            shortcuts_window,
            text="Close",
            command=shortcuts_window.destroy,
            bg="#2196f3",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=5,
            relief="flat"
        )
        close_button.pack(pady=15)
        
        shortcuts_window.transient(self.master)
        shortcuts_window.grab_set()
        
    def show_about(self):
        """Show about information"""
        about_window = Toplevel(self.master)
        about_window.title("About Quiz Master")
        about_window.geometry("400x300")
        about_window.configure(bg="#ffffff")
        about_window.resizable(False, False)
        
        # Center the window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f'+{x}+{y}')
        
        # Header
        header_frame = Frame(about_window, bg="#2196f3", padx=10, pady=10)
        header_frame.pack(fill="x")
        
        header_label = Label(
            header_frame,
            text="Quiz Master",
            font=("Segoe UI", 14, "bold"),
            bg="#2196f3",
            fg="white"
        )
        header_label.pack()
        
        # Content
        content_frame = Frame(about_window, bg="#ffffff", padx=20, pady=15)
        content_frame.pack(fill="both", expand=True)
        
        about_text = """
        Quiz Master is an interactive learning application
        designed to help you test your knowledge.
        
        Version 2.0
        
        Created with Python and Tkinter
        """
        
        about_label = Label(
            content_frame,
            text=about_text,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#333333",
            justify="center"
        )
        about_label.pack(pady=20)
        
        # Close button
        close_button = Button(
            about_window,
            text="Close",
            command=about_window.destroy,
            bg="#2196f3",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=5,
            relief="flat"
        )
        close_button.pack(pady=15)
        
        about_window.transient(self.master)
        about_window.grab_set()
    
    def load_question(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        self.result_var.set("")  # Clear previous result
        self.update_progress_text()

        if self.question_index < len(self.question_dict):
            question = list(self.question_dict.keys())[self.question_index]
            self.current_question.set(question)
            self.selected_answers = []

            options = self.question_dict[question][0]  # answer_options
            self.answer_vars = []
            self.checkbuttons = []  # Store references to checkbuttons
            self.option_frames = []  # Store references to option frames
            
            # Options container with modern styling
            options_container = Frame(self.options_frame, bg="#f5f7fa")
            options_container.pack(fill="both", expand=True, padx=15, pady=10)
            
            # Create a 2x2 grid for options with improved styling
            grid_frame = Frame(options_container, bg="#f5f7fa")
            grid_frame.pack(expand=True, fill="both", pady=10)
            
            # Configure grid with equal weight to all columns and rows
            grid_frame.columnconfigure(0, weight=1)
            grid_frame.columnconfigure(1, weight=1)
            grid_frame.rowconfigure(0, weight=1)
            grid_frame.rowconfigure(1, weight=1)
            
            # Layout options in a 2x2 grid
            positions = [(0, 0), (0, 1), (1, 0), (1, 1)]  # (row, column)
            
            for i, option in enumerate(options):
                if i < 4:  # Only handle up to 4 options
                    var = IntVar()
                    self.answer_vars.append(var)
                    
                    # Each option gets its own frame with modern card styling
                    option_frame = Frame(
                        grid_frame, 
                        bg="#f8f9fa", 
                        bd=1, 
                        relief="solid",
                        padx=15,
                        pady=15,
                        highlightbackground="#e0e0e0",
                        highlightthickness=1
                    )
                    
                    row, col = positions[i]
                    option_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                    self.option_frames.append(option_frame)
                    
                    # Option letter with circle background
                    letter_frame = Frame(
                        option_frame,
                        bg="#e3f2fd",
                        width=30,
                        height=30,
                        bd=0
                    )
                    letter_frame.pack(side="left", padx=(0, 10))
                    letter_frame.pack_propagate(False)  # Prevent frame from shrinking
                    
                    option_letter = chr(65 + i)  # A, B, C, D for options
                    letter_label = Label(
                        letter_frame,
                        text=option_letter,
                        font=("Segoe UI", 12, "bold"),
                        bg="#e3f2fd",
                        fg="#1976d2"
                    )
                    letter_label.place(relx=0.5, rely=0.5, anchor="center")
                    
                    # Create checkbutton with improved styling
                    check = Checkbutton(
                        option_frame,
                        text=option,
                        variable=var,
                        wraplength=350,
                        bg="#f8f9fa",
                        activebackground="#e3f2fd",
                        padx=5,
                        pady=5,
                        anchor="w",
                        justify="left",
                        font=self.option_font,
                        cursor="hand2"
                    )
                    check.pack(side="left", expand=True, fill="both")
                    self.checkbuttons.append(check)
                    
                    # Bind hover effects for better interactivity
                    option_frame.bind("<Enter>", lambda e, frame=option_frame, btn=check: 
                                     [frame.config(bg="#e3f2fd"), btn.config(bg="#e3f2fd")])
                    option_frame.bind("<Leave>", lambda e, frame=option_frame, btn=check: 
                                     [frame.config(bg="#f8f9fa"), btn.config(bg="#f8f9fa")])
                    
                    # Bind click on the entire frame to toggle the checkbox
                    option_frame.bind("<Button-1>", lambda e, idx=i: self.toggle_option(idx))
                    
                    # If this question was previously answered, show the selection
                    if question in self.answered_questions:
                        correct_answers = self.question_dict[question][1]
                        if not isinstance(correct_answers, list):
                            correct_answers = [str(correct_answers)]
                        else:
                            correct_answers = [str(ans) for ans in correct_answers]
                        
                        # Remove any empty strings
                        correct_answers = [ans for ans in correct_answers if ans.strip()]
                        
                        # If this option was selected and is correct
                        if var.get() == 1 and options[i] in correct_answers:
                            option_frame.config(bg="#e8f5e9")  # Light green
                            check.config(bg="#e8f5e9")
                        # If this option was selected but is incorrect
                        elif var.get() == 1 and options[i] not in correct_answers:
                            option_frame.config(bg="#ffebee")  # Light red
                            check.config(bg="#ffebee")
                        # If this option was not selected but is correct
                        elif var.get() == 0 and options[i] in correct_answers:
                            option_frame.config(bg="#e1f5fe")  # Light blue
                            check.config(bg="#e1f5fe")
        else:
            self.show_results()

    def submit_answer(self):
        user_answers = [var.get() for var in self.answer_vars]
        selected_options = [
            self.question_dict[list(self.question_dict.keys())[self.question_index]][0][i]
            for i, val in enumerate(user_answers) if val == 1
        ]
        
        current_question = list(self.question_dict.keys())[self.question_index]
        correct_answers = self.question_dict[current_question][1]  # correct_options
        
        # Ensure correct_answers is treated as a list of strings
        if not isinstance(correct_answers, list):
            correct_answers = [str(correct_answers)]
        else:
            correct_answers = [str(ans) for ans in correct_answers]
            
        # Remove any empty strings
        correct_answers = [ans for ans in correct_answers if ans.strip()]

        # Reset styling for all option frames and checkbuttons
        for i, frame in enumerate(self.option_frames):
            frame.config(bg="#f8f9fa")
            self.checkbuttons[i].config(bg="#f8f9fa")

        if set(selected_options) == set(correct_answers):
            self.score += 1
            self.update_score_display()
            self.result_var.set("✓ Correct!")
            self.result_label.config(fg="#4caf50")  # Green for correct
            
            # Play success sound if available
            try:
                self.master.bell()  # Simple bell sound
            except:
                pass
            
            # Highlight correct answers in green
            for i, val in enumerate(user_answers):
                if val == 1:
                    self.option_frames[i].config(bg="#e8f5e9")  # Light green background
                    self.checkbuttons[i].config(bg="#e8f5e9")
                    
            # If this question was previously marked incorrect, remove it from the list
            if current_question in self.incorrect_questions:
                self.incorrect_questions.remove(current_question)
        else:
            # Add to incorrect questions only if not already there
            if current_question not in self.incorrect_questions:
                self.incorrect_questions.append(current_question)
                
                # Save incorrect question to file
                self.save_incorrect_question(current_question)
                
            self.result_var.set("✗ Incorrect! Try again or press Next to continue.")
            self.result_label.config(fg="#f44336")  # Red for incorrect
            
            # Colorize feedback with improved colors
            options = self.question_dict[current_question][0]
            for i, val in enumerate(user_answers):
                if val == 1 and options[i] not in correct_answers:
                    self.option_frames[i].config(bg="#ffebee")  # Light red for incorrect selection
                    self.checkbuttons[i].config(bg="#ffebee")
                elif val == 1 and options[i] in correct_answers:
                    self.option_frames[i].config(bg="#e8f5e9")  # Light green for correct selection
                    self.checkbuttons[i].config(bg="#e8f5e9")
                elif val == 0 and options[i] in correct_answers:
                    # Light blue outline for missed correct answers
                    self.option_frames[i].config(bg="#e1f5fe")
                    self.checkbuttons[i].config(bg="#e1f5fe")
        
        # Add the current question to answered questions set
        self.answered_questions.add(current_question)

    def save_incorrect_question(self, question):
        """Save an incorrectly answered question to a file"""
        try:
            # Create the options text in the right format
            options = self.question_dict[question][0]
            correct_answers = self.question_dict[question][1]
            
            options_text = ""
            for i, option in enumerate(options):
                option_letter = chr(65 + i)  # A, B, C, D
                options_text += f"{option_letter}: {option}\n"
            
            # Format the question with the same convention as data.txt
            formatted_question = f"{question}\n{options_text}&&&&\n"
            for ans in correct_answers:
                formatted_question += f"{ans}\n"
            
            # Append %%%% at the end
            formatted_question += "%%%%\n"
            
            # Check if file exists to determine if we need to add a new line
            if os.path.exists(self.incorrect_questions_path):
                # Check if this question already exists in the file
                with open(self.incorrect_questions_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if question in content:
                        return  # Don't add duplicate questions
                
                # Append to the file
                with open(self.incorrect_questions_path, 'a', encoding='utf-8') as f:
                    f.write(formatted_question)
            else:
                # Create the file and write to it
                with open(self.incorrect_questions_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_question)
        except Exception as e:
            print(f"Error saving incorrect question: {str(e)}")

    def review_incorrect_questions(self):
        """Load and review incorrectly answered questions"""
        # Check if the file exists
        if not os.path.exists(self.incorrect_questions_path):
            messagebox.showinfo("No Incorrect Questions", "You haven't answered any questions incorrectly yet.")
            return
        
        try:
            # Load the incorrect questions from the file
            with open(self.incorrect_questions_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            # Parse the questions
            questions = data.split(r"%%%%")
            review_dict = {}
            
            for question in questions:
                if not question.strip():
                    continue
                    
                # Split the question into lines
                lines = question.strip().split('\n')
                if not lines:
                    continue
                
                # First line is the question text
                cur_ques = lines[0].strip()
                
                # Find options and answers
                options_section = []
                answers_section = []
                in_answers = False
                
                for line in lines[1:]:  # Skip the question text line
                    if '&&&&' in line:
                        in_answers = True
                        continue
                    
                    if in_answers:
                        if line.strip():
                            answers_section.append(line.strip())
                    else:
                        options_section.append(line.strip())
                
                # Extract options using regex
                ans_opts = []
                for option_line in options_section:
                    if not option_line.strip():
                        continue
                    
                    option_match = re.match(r'([A-D]):\s*(.*)', option_line)
                    if option_match:
                        ans_opts.append(option_match.group(2).strip())
                
                # If we have options and answers, add to the dictionary
                if ans_opts and answers_section:
                    review_dict[cur_ques] = (ans_opts, answers_section)
            
            if not review_dict:
                messagebox.showinfo("No Questions", "No valid questions found in the incorrect questions file.")
                return
            
            # Open a new window with the review quiz
            self.open_review_window(review_dict)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load incorrect questions: {str(e)}")
            # Print detailed error info for debugging
            import traceback
            traceback.print_exc()

    def open_review_window(self, review_dict):
        """Open a new window to review incorrect questions"""
        review_window = Toplevel(self.master)
        review_window.title("Review Incorrect Questions")
        review_window.geometry("1000x750")
        review_window.configure(bg="#f5f7fa")
        
        # Create a simpler review quiz that won't affect the main window
        review_quiz = ReviewQuizWindow(review_window, review_dict)
        
        # Don't wait for the window - this prevents the main window from being affected
        review_window.grab_set()
        
        # Override the close button to only close this window
        review_window.protocol("WM_DELETE_WINDOW", review_window.destroy)

    def next_question(self):
        self.question_index += 1
        self.load_question()

    def prev_question(self):
        """Navigate to the previous question"""
        if self.question_index > 0:
            self.question_index -= 1
            self.load_question()

    def save_checkpoint(self):
        """Save the current progress to a file"""
        checkpoint_data = {
            'question_index': self.question_index,
            'score': self.score,
            'incorrect_questions': self.incorrect_questions,
            'answered_questions': list(self.answered_questions)
        }
        try:
            with open(self.checkpoint_path, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            messagebox.showinfo("Checkpoint Saved", "Your progress has been saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save checkpoint: {str(e)}")
    
    def load_checkpoint(self):
        """Load progress from a saved checkpoint file"""
        if not os.path.exists(self.checkpoint_path):
            messagebox.showinfo("No Checkpoint", "No saved progress found.")
            return
            
        try:
            with open(self.checkpoint_path, 'rb') as f:
                checkpoint_data = pickle.load(f)
                
            self.question_index = checkpoint_data.get('question_index', 0)
            self.score = checkpoint_data.get('score', 0)
            self.incorrect_questions = checkpoint_data.get('incorrect_questions', [])
            self.answered_questions = set(checkpoint_data.get('answered_questions', []))
            
            self.update_score_display()
            self.load_question()
            messagebox.showinfo("Checkpoint Loaded", "Your saved progress has been loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load checkpoint: {str(e)}")
    
    def show_results(self):
        # Create a nicer results window with modern styling
        results_window = Toplevel(self.master)
        results_window.title("Quiz Results")
        results_window.geometry("700x600")
        results_window.configure(bg="#ffffff")
        
        # Center the window
        results_window.update_idletasks()
        width = results_window.winfo_width()
        height = results_window.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        results_window.geometry(f'+{x}+{y}')
        
        # Results header with gradient background
        header_frame = Frame(results_window, bg="#2196f3", padx=20, pady=20)
        header_frame.pack(fill="x")
        
        header_label = Label(
            header_frame,
            text="Quiz Completed!",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#2196f3"
        )
        header_label.pack()
        
        # Score information with card styling
        score_frame = Frame(results_window, bg="#ffffff", padx=30, pady=20, bd=1, relief="solid")
        score_frame.pack(fill="x", padx=20, pady=20)
        
        percentage = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
        
        # Score with large font
        score_label = Label(
            score_frame,
            text=f"{self.score}/{self.total_questions}",
            font=("Segoe UI", 36, "bold"),
            bg="#ffffff",
            fg="#2196f3"
        )
        score_label.pack(pady=5)
        
        # Percentage with medium font
        percentage_label = Label(
            score_frame,
            text=f"{percentage:.1f}%",
            font=("Segoe UI", 18),
            bg="#ffffff",
            fg="#333333"
        )
        percentage_label.pack(pady=5)
        
        # Performance message
        if percentage >= 90:
            message = "Excellent! You've mastered this material."
        elif percentage >= 75:
            message = "Great job! You have a good understanding."
        elif percentage >= 60:
            message = "Good work! Keep practicing to improve."
        else:
            message = "Keep studying! You'll improve with practice."
        
        performance_label = Label(
            score_frame,
            text=message,
            font=("Segoe UI", 12),
            bg="#ffffff",
            fg="#555555"
        )
        performance_label.pack(pady=10)
        
        # Incorrect questions section with scrollable area
        if self.incorrect_questions:
            incorrect_frame = Frame(results_window, bg="#ffffff", padx=20, pady=10)
            incorrect_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            incorrect_header = Label(
                incorrect_frame,
                text="Questions to Review:",
                font=("Segoe UI", 14, "bold"),
                bg="#ffffff",
                fg="#f44336"
            )
            incorrect_header.pack(anchor="w", pady=10)
            
            # Create a canvas with scrollbar for the review questions
            canvas = Canvas(incorrect_frame, bg="#ffffff", highlightthickness=0)
            scrollbar = ttk.Scrollbar(incorrect_frame, orient="vertical", command=canvas.yview)
            
            review_frame = Frame(canvas, bg="#ffffff")
            
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            canvas.create_window((0, 0), window=review_frame, anchor="nw", tags="review_frame")
            review_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
            for i, question in enumerate(self.incorrect_questions):
                question_card = Frame(
                    review_frame,
                    bg="#ffffff",
                    padx=15,
                    pady=10,
                    bd=1,
                    relief="solid",
                    highlightbackground="#e0e0e0",
                    highlightthickness=1
                )
                question_card.pack(fill="x", pady=5, padx=5)
                
                q_number = Label(
                    question_card,
                    text=f"{i+1}.",
                    font=("Segoe UI", 11, "bold"),
                    bg="#ffffff",
                    fg="#f44336",
                    anchor="nw"
                )
                q_number.pack(side="left", padx=(0, 5), anchor="n")
                
                q_text = Label(
                    question_card,
                    text=question,
                    wraplength=550,
                    justify="left",
                    bg="#ffffff",
                    anchor="w",
                    font=("Segoe UI", 11)
                )
                q_text.pack(side="left", fill="x", expand=True, anchor="w")
                
                correct_answers = self.question_dict[question][1]
                if not isinstance(correct_answers, list):
                    correct_answers = [correct_answers]
                
                answers_text = ", ".join(correct_answers)
                
                a_label = Label(
                    question_card,
                    text=f"Correct Answer(s): {answers_text}",
                    wraplength=550,
                    justify="left",
                    bg="#ffffff",
                    fg="#4caf50",
                    anchor="w",
                    font=("Segoe UI", 10)
                )
                a_label.pack(anchor="w", pady=3, padx=(20, 0))
        else:
            perfect_frame = Frame(results_window, bg="#ffffff", padx=20, pady=20)
            perfect_frame.pack(fill="x", pady=20)
            
            perfect_label = Label(
                perfect_frame,
                text="Perfect Score! You answered all questions correctly.",
                font=("Segoe UI", 14),
                bg="#ffffff",
                fg="#4caf50"
            )
            perfect_label.pack(pady=10)
            
            # Add a trophy or celebration icon if available
            try:
                trophy_img = PhotoImage(file="trophy.png")
                trophy_label = Label(perfect_frame, image=trophy_img, bg="#ffffff")
                trophy_label.image = trophy_img  # Keep a reference
                trophy_label.pack(pady=10)
            except:
                pass
        
        # Buttons frame
        buttons_frame = Frame(results_window, bg="#ffffff", padx=20, pady=15)
        buttons_frame.pack(fill="x", pady=10)
        
        # Review button - only show if there are incorrect questions
        if self.incorrect_questions:
            review_button = Button(
                buttons_frame,
                text="Review Incorrect Questions",
                command=lambda: [results_window.destroy(), self.review_incorrect_questions()],
                bg="#ff9800",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                padx=15,
                pady=8,
                relief="flat",
                activebackground="#fb8c00",
                activeforeground="white"
            )
            review_button.pack(side="left", padx=5)
        
        # Close button
        close_button = Button(
            buttons_frame,
            text="Finish",
            command=lambda: [results_window.destroy(), self.master.quit()],
            bg="#e91e63",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            activebackground="#d81b60",
            activeforeground="white"
        )
        close_button.pack(side="right", padx=5)
        
        # Restart button
        restart_button = Button(
            buttons_frame,
            text="Restart Quiz",
            command=lambda: [results_window.destroy(), self.restart_quiz()],
            bg="#4caf50",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            relief="flat",
            activebackground="#43a047",
            activeforeground="white"
        )
        restart_button.pack(side="right", padx=5)
        
        # Make sure the window stays on top and becomes the focus
        results_window.transient(self.master)
        results_window.grab_set()
        self.master.wait_window(results_window)
    
    def restart_quiz(self):
        """Restart the quiz from the beginning"""
        self.question_index = 0
        self.score = 0
        self.incorrect_questions = []
        self.answered_questions = set()
        self.update_score_display()
        self.load_question()

class ReviewQuizWindow(QuizWindow):
    """A specialized version of QuizWindow for reviewing incorrect questions"""
    
    def __init__(self, master, question_dict):
        # Initialize with the parent class
        super().__init__(master, question_dict)
        
        # Override the close behavior to only close this window
        self.master.protocol("WM_DELETE_WINDOW", self.close_review)
        
        # Update title and add a note
        self.master.title("Review Incorrect Questions")
        
        # Add a review mode indicator
        self.review_label = Label(
            self.header_frame,
            text="REVIEW MODE",
            font=("Segoe UI", 10, "bold"),
            bg="#e8eef7",
            fg="#f44336"
        )
        self.review_label.pack(side="right", padx=10, pady=5)
    
    def close_review(self):
        """Custom close method that only closes this window"""
        self.master.destroy()
    
    def show_results(self):
        """Override to only close the review window, not the main app"""
        results_window = Toplevel(self.master)
        results_window.title("Review Results")
        results_window.geometry("600x500")
        results_window.configure(bg="#ffffff")
        
        # Center the window
        results_window.update_idletasks()
        width = results_window.winfo_width()
        height = results_window.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        results_window.geometry(f'+{x}+{y}')
        
        # Results header
        header_frame = Frame(results_window, bg="#2196f3", padx=20, pady=20)
        header_frame.pack(fill="x")
        
        header_label = Label(
            header_frame,
            text="Review Completed!",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#2196f3"
        )
        header_label.pack()
        
        # Score information
        score_frame = Frame(results_window, bg="#ffffff", padx=30, pady=20)
        score_frame.pack(fill="x", pady=20)
        
        score_label = Label(
            score_frame,
            text=f"Your Score: {self.score}/{self.total_questions}",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff"
        )
        score_label.pack(pady=5)
        
        percentage = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
        percentage_label = Label(
            score_frame,
            text=f"Percentage: {percentage:.1f}%",
            font=("Segoe UI", 14),
            bg="#ffffff"
        )
        percentage_label.pack(pady=5)
        
        # Performance message
        if percentage >= 90:
            message = "Excellent! You've mastered these questions."
        elif percentage >= 75:
            message = "Great job! Keep up the good work."
        elif percentage >= 60:
            message = "Good progress! Keep practicing."
        else:
            message = "Keep studying! You'll improve with practice."
        
        performance_label = Label(
            score_frame,
            text=message,
            font=("Segoe UI", 12),
            bg="#ffffff",
            fg="#555555"
        )
        performance_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = Frame(results_window, bg="#ffffff", padx=20, pady=15)
        buttons_frame.pack(fill="x", pady=20)
        
        # Close button - only close the review windows, not the main app
        close_button = Button(
            buttons_frame,
            text="Close",
            command=lambda: [results_window.destroy(), self.master.destroy()],
            bg="#e91e63",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief="flat"
        )
        close_button.pack(side="right", padx=5)
        
        # Restart review button
        restart_button = Button(
            buttons_frame,
            text="Restart Review",
            command=lambda: [results_window.destroy(), self.restart_quiz()],
            bg="#4caf50",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            relief="flat"
        )
        restart_button.pack(side="right", padx=5)
        
        # Make window modal to its parent
        results_window.transient(self.master)
        results_window.grab_set()
        self.master.wait_window(results_window)

if __name__ == "__main__":
    with open(r"data.txt", "r", encoding='utf-8') as f:
        data = f.read()
    
    # Split into individual questions
    questions = data.split(r"%%%%")
    question_dict = {}
    
    for question in questions:
        if not question.strip():
            continue
            
        # Extract the question (first line)
        lines = question.split(r"A: ", 1)
        if len(lines) < 2:
            continue
        
        cur_ques = lines[0].strip()
        
        # Join all lines for regex processing
        question_text = "A: " + lines[1]
        
        # Find all options using regex
        option_pattern = r'([A-D]):\s*(.*?)(?=\s*[A-D]:\s*|\s*&&&&|\Z)'
        options_matches = re.findall(option_pattern, question_text, re.DOTALL)
        
        # Extract options
        ans_opts = [match[1].strip() for match in options_matches]
        
        # Find the correct answer(s)
        answer_pattern = r'&&&&\s*(.*?)(?=\Z)'
        answer_match = re.search(answer_pattern, question_text, re.DOTALL)
        
        if answer_match:
            # Get all answers (might be multiple lines)
            answers_text = answer_match.group(1)
            # Split by lines and clean
            cor_ans = [ans.strip() for ans in answers_text.splitlines() if ans.strip()]
        else:
            # If no match found, raise exception
            raise Exception(f"No correct answer found for question: {cur_ques}")
        
        # Store in dictionary
        question_dict[cur_ques] = (ans_opts, cor_ans)
    
    # Debug: Print first few questions
    i = 0
    for key, value in question_dict.items():
        print(f"Question: {key}")
        print(f"Options: {value[0]}")
        print(f"Correct answers: {value[1]}")
        print("-" * 50)
        i += 1
        if i == 2:
            break
    
    root = Tk()
    quiz_app = QuizWindow(root, question_dict)
    root.mainloop()