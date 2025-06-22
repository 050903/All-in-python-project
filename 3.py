import tkinter as tk
from math import sqrt, sin, cos, tan, log, pi, e

class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.geometry("300x400")
        self.expression = ""
        self.display_var = tk.StringVar(value="0")
        self.create_widgets()
    
    def create_widgets(self):
        # Display
        display = tk.Entry(self.root, textvariable=self.display_var, font=("Arial", 16), justify="right", state="readonly")
        display.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        
        # Buttons
        buttons = [
            ('C', 1, 0), ('±', 1, 1), ('%', 1, 2), ('÷', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('×', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('0', 5, 0), ('.', 5, 1), ('=', 5, 2), ('√', 5, 3)
        ]
        
        for (text, row, col) in buttons:
            btn = tk.Button(self.root, text=text, font=("Arial", 14), command=lambda t=text: self.button_click(t))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        # Configure grid weights
        for i in range(6):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
    
    def button_click(self, char):
        if char == 'C':
            self.expression = ""
            self.display_var.set("0")
        elif char == '=':
            self.calculate()
        elif char == '±':
            if self.expression and self.expression[-1].isdigit():
                self.expression = f"(-{self.expression})"
                self.display_var.set(self.expression)
        elif char == '√':
            self.expression += "sqrt("
            self.display_var.set(self.expression)
        elif char in '÷×':
            self.expression += '/' if char == '÷' else '*'
            self.display_var.set(self.expression)
        else:
            self.expression += char
            self.display_var.set(self.expression)
    
    def calculate(self):
        try:
            # Replace % with /100
            expr = self.expression.replace('%', '/100')
            result = eval(expr, {"__builtins__": {}, "sqrt": sqrt, "sin": sin, "cos": cos, "tan": tan, "log": log, "pi": pi, "e": e})
            self.display_var.set(str(result))
            self.expression = str(result)
        except:
            self.display_var.set("Error")
            self.expression = ""
    
    def run(self):
        self.root.mainloop()

Calculator().run()