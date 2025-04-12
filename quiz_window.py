from tkinter import Tk, Label, Button, StringVar, Frame, messagebox, Checkbutton, IntVar, ttk, PhotoImage, Menu, Toplevel
import random
import re
import pickle
import os
## preprocess data


class QuizWindow:
    def __init__(self, master, question_dict):
        self.master = master
        self.master.title("Quiz Application")
        self.master.geometry("900x700")  # Increased window size
        self.master.configure(bg="#f0f0f0")  # Set background color
        
        # Configure a theme
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 10, "bold"), borderwidth=1)
        self.style.configure("TCheckbutton", background="#f0f0f0")
        
        # Create menu bar
        self.menu_bar = Menu(self.master)
        self.master.config(menu=self.menu_bar)
        
        # Add File menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Save Progress", command=self.save_checkpoint, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Load Progress", command=self.load_checkpoint, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Review Incorrect Questions", command=self.review_incorrect_questions)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.master.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Store fixed font sizes
        self.fonts = {
            'question': ('Arial', 19, 'bold'),
            'option': ('Arial', 14),
            'result': ('Arial', 17, 'bold'),
            'shortcut': ('Arial', 8),
            'button': ('Arial', 15, 'bold'),
            'header': ('Arial', 15)
        }
        
        # Keep references to UI elements for consistency
        self.font_elements = []
        
        # Center window on screen
        self.center_window()
        
        # Remove responsive font resizing - only keep fullscreen toggle
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
        
        # Update progress text
        self.update_progress_text()

        # Main container
        self.main_frame = Frame(self.master, bg="#f0f0f0")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Header with progress
        self.header_frame = Frame(self.main_frame, bg="#e1e1e1")
        self.header_frame.pack(fill="x", pady=5)
        
        # Progress indicator
        self.progress_label = Label(
            self.header_frame, 
            textvariable=self.progress_text,
            font=("Arial", 10),
            bg="#e1e1e1"
        )
        self.progress_label.pack(side="left", padx=10, pady=5)
        
        # Score display
        self.score_label = Label(
            self.header_frame,
            text=f"Score: {self.score}/{self.total_questions}",
            font=("Arial", 10),
            bg="#e1e1e1"
        )
        self.score_label.pack(side="right", padx=10, pady=5)
        
        # Question section
        self.question_frame = Frame(self.main_frame, bg="#ffffff", bd=1, relief="solid")
        self.question_frame.pack(fill="x", pady=10, ipady=10)
        
        self.question_label = Label(
            self.question_frame, 
            textvariable=self.current_question, 
            wraplength=700, 
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            justify="left"
        )
        self.question_label.pack(padx=20, pady=15, anchor="w")

        # Options section
        self.options_frame = Frame(self.main_frame, bg="#f8f8f8", bd=1, relief="solid")
        self.options_frame.pack(fill="both", expand=True, pady=10)
        
        # Result feedback
        self.result_frame = Frame(self.main_frame, bg="#f0f0f0")
        self.result_frame.pack(fill="x", pady=5)
        
        self.result_label = Label(
            self.result_frame, 
            textvariable=self.result_var, 
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        self.result_label.pack(pady=5)
        
        # Controls
        self.controls_frame = Frame(self.main_frame, bg="#f0f0f0")
        self.controls_frame.pack(fill="x", pady=10)
        
        # Keyboard shortcuts info
        self.shortcut_frame = Frame(self.controls_frame, bg="#f0f0f0")
        self.shortcut_frame.pack(side="left", padx=10)
        
        self.shortcut_label = Label(
            self.shortcut_frame,
            text="Shortcuts: 1-4 = Select Option | ↵ = Submit | Space = Submit | → = Next | ← = Previous | Ctrl+S = Save | Ctrl+O = Load | F11 = Fullscreen",
            font=("Arial", 8),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.shortcut_label.pack(side="left")
        
        # Button frame
        self.button_frame = Frame(self.controls_frame, bg="#f0f0f0")
        self.button_frame.pack(side="right", padx=10)

        self.prev_button = Button(
            self.button_frame, 
            text="← Pre",
            command=self.prev_question,
            bg="#9e9e9e",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        )
        self.prev_button.pack(side="left", padx=5)

        self.submit_button = Button(
            self.button_frame, 
            text="Submit",
            command=self.submit_answer,
            bg="#4caf50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        )
        self.submit_button.pack(side="left", padx=5)

        self.next_button = Button(
            self.button_frame, 
            text="Next →",
            command=self.next_question,
            bg="#2196f3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        )
        self.next_button.pack(side="left", padx=5)

        # Set up keyboard shortcuts
        self.master.bind("<Right>", lambda event: self.next_question())
        self.master.bind("<Left>", lambda event: self.prev_question())
        self.master.bind("1", lambda event: self.toggle_option(0))
        self.master.bind("2", lambda event: self.toggle_option(1))
        self.master.bind("3", lambda event: self.toggle_option(2))
        self.master.bind("4", lambda event: self.toggle_option(3))
        self.master.bind("<Return>", lambda event: self.submit_answer())
        self.master.bind("<space>", lambda event: self.submit_answer())  # Space bar to submit
        self.master.bind("<Control-s>", lambda event: self.save_checkpoint())
        self.master.bind("<Control-o>", lambda event: self.load_checkpoint())

        self.load_question()
    
    def center_window(self):
        """Center the window on the screen"""
        # Update the window to ensure correct size calculations
        self.master.update_idletasks()
        
        # Get screen and window dimensions
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = 1200  # Initial window width
        window_height = 700  # Initial window height
        
        # Calculate position coordinates
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set the window position
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def update_progress_text(self):
        self.progress_text.set(f"Question {self.question_index + 1} of {self.total_questions}")
        
    def update_score_display(self):
        self.score_label.config(text=f"Score: {self.score}/{self.total_questions}")

    def toggle_option(self, index):
        """Toggle the checkbox at the given index if it exists"""
        if index < len(self.answer_vars):
            current_value = self.answer_vars[index].get()
            self.answer_vars[index].set(1 - current_value)  # Toggle between 0 and 1
            
            # Visual feedback when toggling
            if current_value == 0:
                self.checkbuttons[index].config(bg="#e0f7fa")  # Light blue when selected
            else:
                self.checkbuttons[index].config(bg="#f8f8f8")  # Default background

    def create_ui_element(self, element_type, parent, **kwargs):
        """Create UI element with fixed font size"""
        font_tuple = self.fonts.get(element_type, ('Arial', 10))
        
        if 'font' in kwargs:
            del kwargs['font']
            
        if element_type == 'label':
            element = Label(parent, font=font_tuple, **kwargs)
        elif element_type == 'button':
            element = Button(parent, font=font_tuple, **kwargs)
        elif element_type == 'checkbutton':
            element = Checkbutton(parent, font=font_tuple, **kwargs)
        else:
            return None
            
        # Add to elements list for reference
        self.font_elements.append((element, element_type))
        return element
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        self.master.attributes("-fullscreen", self.fullscreen)
        return "break"  # Prevent event from propagating
    
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
            
            # Options container with padding
            options_container = Frame(self.options_frame, bg="#f8f8f8")
            options_container.pack(fill="both", expand=True, padx=15, pady=10)
            
            # Create a 2x2 grid for options
            grid_frame = Frame(options_container, bg="#f8f8f8")
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
                    
                    # Each option gets its own frame for better styling
                    option_frame = Frame(
                        grid_frame, 
                        bg="#f0f0f0", 
                        bd=2, 
                        relief="groove",
                        padx=10,
                        pady=10
                    )
                    
                    row, col = positions[i]
                    option_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    # Create checkbutton with fixed font
                    option_letter = chr(65 + i)  # A, B, C, D for options
                    check = Checkbutton(
                        option_frame,
                        text=f"{option_letter}. {option}",
                        variable=var,
                        wraplength=300,  # Adjusted for grid layout
                        bg="#f0f0f0",
                        activebackground="#e0f7fa",
                        padx=5,
                        pady=5,
                        anchor="w",
                        justify="left",
                        font=self.fonts['option']
                    )
                    check.pack(expand=True, fill="both")
                    self.checkbuttons.append(check)
                    
                    # Bind hover effects for better interactivity
                    option_frame.bind("<Enter>", lambda e, frame=option_frame: frame.config(bg="#e8f5e9"))
                    option_frame.bind("<Leave>", lambda e, frame=option_frame: frame.config(bg="#f0f0f0"))
                    check.bind("<Enter>", lambda e, btn=check, frame=option_frame: [btn.config(bg="#e8f5e9"), frame.config(bg="#e8f5e9")])
                    check.bind("<Leave>", lambda e, btn=check, frame=option_frame: [btn.config(bg="#f0f0f0"), frame.config(bg="#f0f0f0")])
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

        # Reset styling for all checkbuttons
        for check in self.checkbuttons:
            check.config(bg="#f8f8f8")

        if set(selected_options) == set(correct_answers):
            self.score += 1
            self.update_score_display()
            self.result_var.set("✓ Correct!")
            self.result_label.config(fg="#4caf50")  # Green for correct
            
            # Highlight correct answers in green
            for i, val in enumerate(user_answers):
                if val == 1:
                    self.checkbuttons[i].config(bg="#c8e6c9")  # Light green background
                    
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
            
            # Colorize feedback
            options = self.question_dict[current_question][0]
            for i, val in enumerate(user_answers):
                if val == 1 and options[i] not in correct_answers:
                    self.checkbuttons[i].config(bg="#ffcdd2")  # Light red for incorrect selection
                elif val == 1 and options[i] in correct_answers:
                    self.checkbuttons[i].config(bg="#c8e6c9")  # Light green for correct selection
                elif val == 0 and options[i] in correct_answers:
                    # Light blue outline for missed correct answers
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
        review_window.geometry("900x700")
        review_window.configure(bg="#f0f0f0")
        
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
    
    def show_incorrect_log(self):
        """Display a window with incorrectly answered questions for revision"""
        log_window = Tk()
        log_window.title("Incorrect Questions Log")
        log_window.geometry("1000x600")  # Increased size
        log_window.configure(bg="#f0f0f0")
        
        # Header
        header_frame = Frame(log_window, bg="#f44336", padx=10, pady=15)
        header_frame.pack(fill="x")
        
        header_label = Label(
            header_frame,
            text="Questions for Review",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#f44336"
        )
        header_label.pack()
        
        # Content area
        content_frame = Frame(log_window, bg="#ffffff", padx=20, pady=15)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        if self.incorrect_questions:
            # Create a scrollable frame for questions
            canvas = Canvas(content_frame, bg="#ffffff")
            scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = Frame(canvas, bg="#ffffff")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add each question with its correct answers
            for i, question in enumerate(self.incorrect_questions):
                question_frame = Frame(scrollable_frame, bg="#ffffff", padx=10, pady=5, bd=1, relief="solid")
                question_frame.pack(fill="x", pady=5, padx=5)
                
                q_label = Label(
                    question_frame,
                    text=f"{i+1}. {question}",
                    wraplength=600,
                    justify="left",
                    bg="#ffffff",
                    anchor="w",
                    font=("Arial", 11, "bold")
                )
                q_label.pack(anchor="w", pady=5)
                
                correct_answers = self.question_dict[question][1]
                answers_text = ", ".join(correct_answers)
                
                a_label = Label(
                    question_frame,
                    text=f"Correct Answer(s): {answers_text}",
                    wraplength=600,
                    justify="left",
                    bg="#ffffff",
                    fg="#4caf50",
                    anchor="w",
                    font=("Arial", 10)
                )
                a_label.pack(anchor="w", pady=3)
        else:
            no_items_label = Label(
                content_frame,
                text="No incorrect answers recorded yet.",
                font=("Arial", 12),
                bg="#ffffff"
            )
            no_items_label.pack(pady=30)
        
        # Close button
        close_button = Button(
            log_window,
            text="Close",
            command=log_window.destroy,
            bg="#607d8b",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        close_button.pack(pady=15)
        
        # Make window modal
        log_window.transient(self.master)
        log_window.grab_set()
        self.master.wait_window(log_window)

    def show_results(self):
        # Create a nicer results window instead of a plain messagebox
        results_window = Tk()
        results_window.title("Quiz Results")
        results_window.geometry("600x500")
        results_window.configure(bg="#f0f0f0")
        
        # Results header
        header_frame = Frame(results_window, bg="#2196f3", padx=10, pady=15)
        header_frame.pack(fill="x")
        
        header_label = Label(
            header_frame,
            text="Quiz Completed!",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2196f3"
        )
        header_label.pack()
        
        # Score information
        score_frame = Frame(results_window, bg="#ffffff", padx=20, pady=15)
        score_frame.pack(fill="x", pady=10)
        
        score_label = Label(
            score_frame,
            text=f"Your Score: {self.score} out of {self.total_questions}",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        )
        score_label.pack(pady=5)
        
        percentage = (self.score / self.total_questions) * 100
        percentage_label = Label(
            score_frame,
            text=f"Percentage: {percentage:.1f}%",
            font=("Arial", 12),
            bg="#ffffff"
        )
        percentage_label.pack(pady=5)
        
        # Incorrect questions section
        if self.incorrect_questions:
            incorrect_frame = Frame(results_window, bg="#ffffff", padx=20, pady=10)
            incorrect_frame.pack(fill="both", expand=True, pady=10)
            
            incorrect_header = Label(
                incorrect_frame,
                text="Questions to Review:",
                font=("Arial", 12, "bold"),
                bg="#ffffff",
                fg="#f44336"
            )
            incorrect_header.pack(anchor="w", pady=5)
            
            review_frame = Frame(incorrect_frame, bg="#ffffff")
            review_frame.pack(fill="both", expand=True)
            
            for i, question in enumerate(self.incorrect_questions):
                q_label = Label(
                    review_frame,
                    text=f"{i+1}. {question}",
                    wraplength=550,
                    justify="left",
                    bg="#ffffff",
                    anchor="w"
                )
                q_label.pack(anchor="w", pady=3)
        else:
            perfect_frame = Frame(results_window, bg="#ffffff", padx=20, pady=20)
            perfect_frame.pack(fill="x", pady=10)
            
            perfect_label = Label(
                perfect_frame,
                text="Perfect Score! You answered all questions correctly.",
                font=("Arial", 12),
                bg="#ffffff",
                fg="#4caf50"
            )
            perfect_label.pack(pady=10)
        
        # Close button
        close_button = Button(
            results_window,
            text="Close",
            command=lambda: [results_window.destroy(), self.master.quit()],
            bg="#e91e63",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        close_button.pack(pady=20)
        
        # Make sure the window stays on top and becomes the focus
        results_window.transient(self.master)
        results_window.grab_set()
        self.master.wait_window(results_window)

class ReviewQuizWindow(QuizWindow):
    """A specialized version of QuizWindow for reviewing incorrect questions"""
    
    def __init__(self, master, question_dict):
        # Initialize with the parent class
        super().__init__(master, question_dict)
        
        # Override the close behavior to only close this window
        self.master.protocol("WM_DELETE_WINDOW", self.close_review)
        
        # Update title and add a note
        self.master.title("Review Incorrect Questions")
        note_label = Label(
            self.header_frame,
            text="REVIEW MODE",
            font=("Arial", 10, "bold"),
            bg="#e1e1e1",
            fg="#f44336"
        )
        note_label.pack(side="right", padx=10, pady=5)
    
    def close_review(self):
        """Custom close method that only closes this window"""
        self.master.destroy()
    
    def show_results(self):
        """Override to only close the review window, not the main app"""
        results_window = Toplevel(self.master)
        results_window.title("Review Results")
        results_window.geometry("600x500")
        results_window.configure(bg="#f0f0f0")
        
        # Results header
        header_frame = Frame(results_window, bg="#2196f3", padx=10, pady=15)
        header_frame.pack(fill="x")
        
        header_label = Label(
            header_frame,
            text="Review Completed!",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2196f3"
        )
        header_label.pack()
        
        # Score information
        score_frame = Frame(results_window, bg="#ffffff", padx=20, pady=15)
        score_frame.pack(fill="x", pady=10)
        
        score_label = Label(
            score_frame,
            text=f"Your Score: {self.score} out of {self.total_questions}",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        )
        score_label.pack(pady=5)
        
        percentage = (self.score / self.total_questions) * 100
        percentage_label = Label(
            score_frame,
            text=f"Percentage: {percentage:.1f}%",
            font=("Arial", 12),
            bg="#ffffff"
        )
        percentage_label.pack(pady=5)
        
        # Close button - only close the review windows, not the main app
        close_button = Button(
            results_window,
            text="Close",
            command=lambda: [results_window.destroy(), self.master.destroy()],
            bg="#e91e63",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        close_button.pack(pady=20)
        
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
        # lines = question.splitlines()
        lines = question.split(r"A: ", 1)
        if len(lines) < 2:
            continue
        # print(lines)
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