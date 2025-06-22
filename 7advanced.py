import tkinter as tk
from tkinter import ttk, messagebox
import random

DIFFICULTY_LEVELS = {
    "Easy": {"range": 50, "attempts": 10},
    "Medium": {"range": 100, "attempts": 7},
    "Hard": {"range": 500, "attempts": 10},
}

class GuessingGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("400x450")
        self.root.resizable(False, False)

        # Style
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # Game State
        self.secret_number = 0
        self.attempts_left = 0
        self.high_scores = {level: float('inf') for level in DIFFICULTY_LEVELS}

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Difficulty Selection ---
        difficulty_frame = ttk.LabelFrame(main_frame, text="Difficulty", padding="10")
        difficulty_frame.pack(fill="x", pady=5)
        
        self.difficulty_var = tk.StringVar(value="Medium")
        for level in DIFFICULTY_LEVELS:
            ttk.Radiobutton(
                difficulty_frame, text=level, variable=self.difficulty_var, value=level,
                command=self.start_new_game
            ).pack(side="left", padx=10, expand=True)

        # --- Game Info ---
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=10)
        
        self.info_label = ttk.Label(info_frame, text="", anchor="center")
        self.info_label.pack(fill="x")
        self.attempts_label = ttk.Label(info_frame, text="", anchor="center")
        self.attempts_label.pack(fill="x")
        
        # --- Guess Input ---
        guess_frame = ttk.Frame(main_frame)
        guess_frame.pack(pady=10)
        
        ttk.Label(guess_frame, text="Your Guess:").pack(side="left")
        self.guess_var = tk.StringVar()
        self.guess_entry = ttk.Entry(guess_frame, textvariable=self.guess_var, width=10)
        self.guess_entry.pack(side="left", padx=5)
        self.guess_button = ttk.Button(guess_frame, text="Guess", command=self.check_guess)
        self.guess_button.pack(side="left")

        # --- Feedback ---
        self.feedback_label = ttk.Label(main_frame, text="Good luck!", font=("Helvetica", 12, "italic"), anchor="center")
        self.feedback_label.pack(fill="x", pady=10)

        # --- Controls & High Score ---
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=10)

        self.new_game_button = ttk.Button(bottom_frame, text="New Game", command=self.start_new_game)
        self.new_game_button.pack(side="left", expand=True)
        
        self.highscore_label = ttk.Label(bottom_frame, text="", anchor="center")
        self.highscore_label.pack(side="right", expand=True)

        self.start_new_game()

    def start_new_game(self):
        self.guess_var.set("")
        self.guess_entry.config(state="normal")
        self.guess_button.config(state="normal")
        
        difficulty = self.difficulty_var.get()
        settings = DIFFICULTY_LEVELS[difficulty]
        max_range = settings["range"]
        self.attempts_left = settings["attempts"]
        
        self.secret_number = random.randint(1, max_range)
        
        self.info_label.config(text=f"I'm thinking of a number between 1 and {max_range}.")
        self.update_attempts_display()
        self.update_highscore_display()
        self.feedback_label.config(text="A new game has begun!")
        
    def check_guess(self):
        try:
            guess = int(self.guess_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            return

        self.attempts_left -= 1
        
        if guess == self.secret_number:
            self.handle_win()
        elif guess < self.secret_number:
            self.feedback_label.config(text=f"'{guess}' is too low! Try again.")
        else:
            self.feedback_label.config(text=f"'{guess}' is too high! Try again.")
            
        if self.attempts_left == 0 and guess != self.secret_number:
            self.handle_loss()
        
        self.update_attempts_display()
        self.guess_var.set("")

    def handle_win(self):
        attempts_taken = DIFFICULTY_LEVELS[self.difficulty_var.get()]['attempts'] - self.attempts_left
        self.feedback_label.config(text=f"Correct! You guessed it in {attempts_taken} tries!")
        
        if attempts_taken < self.high_scores[self.difficulty_var.get()]:
            self.high_scores[self.difficulty_var.get()] = attempts_taken
            self.update_highscore_display()
            self.feedback_label.config(text=f"New high score for {self.difficulty_var.get()}!")

        self.end_game()

    def handle_loss(self):
        self.feedback_label.config(text=f"Game Over! The number was {self.secret_number}.")
        self.end_game()
        
    def end_game(self):
        self.guess_entry.config(state="disabled")
        self.guess_button.config(state="disabled")

    def update_attempts_display(self):
        self.attempts_label.config(text=f"You have {self.attempts_left} attempts remaining.")

    def update_highscore_display(self):
        difficulty = self.difficulty_var.get()
        score = self.high_scores[difficulty]
        if score == float('inf'):
            self.highscore_label.config(text=f"High Score: None")
        else:
            self.highscore_label.config(text=f"High Score: {score} guesses")

if __name__ == "__main__":
    root = tk.Tk()
    app = GuessingGameApp(root)
    root.mainloop()
