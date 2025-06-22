import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

def generate_password(length, use_uppercase, use_lowercase, use_digits, use_special):
    """Generates a random password based on user-defined criteria."""
    character_pool = ""
    if use_uppercase:
        character_pool += string.ascii_uppercase
    if use_lowercase:
        character_pool += string.ascii_lowercase
    if use_digits:
        character_pool += string.digits
    if use_special:
        character_pool += string.punctuation

    if not character_pool:
        # This case is handled by validation in the GUI
        return None

    password = "".join(random.choices(character_pool, k=length))
    return password

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("450x450")
        self.root.resizable(False, False)

        # Style
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # --- Frame for Inputs ---
        input_frame = ttk.LabelFrame(self.root, text="Criteria", padding=(10, 5))
        input_frame.pack(padx=10, pady=10, fill="x")

        # Password Length
        ttk.Label(input_frame, text="Password Length:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.length_var = tk.StringVar(value="12")
        ttk.Entry(input_frame, textvariable=self.length_var, width=5).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Number of Passwords
        ttk.Label(input_frame, text="Number to Generate:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.num_passwords_var = tk.StringVar(value="5")
        ttk.Entry(input_frame, textvariable=self.num_passwords_var, width=5).grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Character Types
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)

        ttk.Checkbutton(input_frame, text="Uppercase (A-Z)", variable=self.use_upper).grid(row=1, column=0, columnspan=2, sticky="w", padx=5)
        ttk.Checkbutton(input_frame, text="Lowercase (a-z)", variable=self.use_lower).grid(row=2, column=0, columnspan=2, sticky="w", padx=5)
        ttk.Checkbutton(input_frame, text="Digits (0-9)", variable=self.use_digits).grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
        ttk.Checkbutton(input_frame, text="Special Chars (!@#)", variable=self.use_special).grid(row=4, column=0, columnspan=2, sticky="w", padx=5)

        # --- Generate Button ---
        ttk.Button(self.root, text="Generate Passwords", command=self.handle_generate).pack(pady=5)

        # --- Frame for Output ---
        output_frame = ttk.LabelFrame(self.root, text="Generated Passwords", padding=(10, 5))
        output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.password_listbox = tk.Listbox(output_frame, height=10)
        self.password_listbox.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.password_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.password_listbox.config(yscrollcommand=scrollbar.set)
        
        # --- Copy Button ---
        self.copy_button = ttk.Button(self.root, text="Copy Selected", command=self.copy_to_clipboard, state="disabled")
        self.copy_button.pack(pady=(0, 10))

        if not PYPERCLIP_AVAILABLE:
            self.copy_button.config(text="Copy (pip install pyperclip)")

    def handle_generate(self):
        # --- 1. Validate Inputs ---
        try:
            length = int(self.length_var.get())
            num_passwords = int(self.num_passwords_var.get())
            if length <= 0 or num_passwords <= 0:
                raise ValueError("Values must be positive.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Password length and number to generate must be positive integers.")
            return

        char_types_selected = self.use_upper.get() or self.use_lower.get() or self.use_digits.get() or self.use_special.get()
        if not char_types_selected:
            messagebox.showwarning("No Character Types", "Please select at least one character type to include.")
            return

        # --- 2. Generate Passwords ---
        self.password_listbox.delete(0, tk.END)  # Clear previous passwords
        for _ in range(num_passwords):
            password = generate_password(
                length, self.use_upper.get(), self.use_lower.get(), self.use_digits.get(), self.use_special.get()
            )
            if password:
                self.password_listbox.insert(tk.END, password)
        
        # Enable the copy button if pyperclip is installed and there are passwords
        if PYPERCLIP_AVAILABLE and self.password_listbox.size() > 0:
            self.copy_button.config(state="normal")

    def copy_to_clipboard(self):
        selected_indices = self.password_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("No Selection", "Please select a password from the list to copy.")
            return
        
        selected_password = self.password_listbox.get(selected_indices[0])
        try:
            pyperclip.copy(selected_password)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_password)
            messagebox.showinfo("Copied!", f"Password '{selected_password}' has been copied to the clipboard.")
        except Exception as e:
            messagebox.showerror("Copy Failed", f"Could not copy to clipboard.\nError: {e}")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = PasswordGeneratorApp(app_root)
    app_root.mainloop()
