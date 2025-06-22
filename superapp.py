"""
Advanced Todo List Manager
-------------------------
A feature-rich todo list application with:
- Add, edit, delete todo items with priority levels
- Mark items as complete/incomplete
- Set due dates and track overdue items
- Save data persistently to JSON
- Search and filter functionality
- Color-coded priority system
- Statistics dashboard

To run: Simply execute 'python superapp.py'
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox
import json
from datetime import datetime, date
import os

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Todo Manager")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.todos = []
        self.filename = "todos.json"
        
        # UI Elements
        self.create_widgets()
        self.load_todos()
        self.update_stats()
        
    def create_widgets(self):
        # Stats frame
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack()
        
        # Input frame
        input_frame = ttk.LabelFrame(self.root, text="Add New Todo", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Todo text
        ttk.Label(input_frame, text="Task:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.todo_input = ttk.Entry(input_frame, width=30)
        self.todo_input.grid(row=0, column=1, padx=5)
        
        # Priority
        ttk.Label(input_frame, text="Priority:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = Combobox(input_frame, textvariable=self.priority_var, values=["High", "Medium", "Low"], width=10)
        priority_combo.grid(row=0, column=3, padx=5)
        
        # Due date
        ttk.Label(input_frame, text="Due Date:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.due_date = ttk.Entry(input_frame, width=12)
        self.due_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.due_date.grid(row=0, column=5, padx=5)
        
        ttk.Button(input_frame, text="Add Todo", command=self.add_todo).grid(row=0, column=6, padx=10)
        
        # Bind Enter key
        self.todo_input.bind('<Return>', lambda e: self.add_todo())
        
        # Search and filter frame
        filter_frame = ttk.LabelFrame(self.root, text="Search & Filter", padding="10")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_todos)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(20,5))
        self.filter_var = tk.StringVar(value="All")
        self.filter_var.trace('w', self.search_todos)
        filter_combo = Combobox(filter_frame, textvariable=self.filter_var, values=["All", "Pending", "Complete", "Overdue", "High Priority"], width=12)
        filter_combo.pack(side=tk.LEFT, padx=5)
        
        # Todo list
        list_frame = ttk.LabelFrame(self.root, text="Todo List", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(list_frame, columns=('Priority', 'Status', 'Due Date', 'Created'), show='tree headings')
        self.tree.heading('#0', text='Task')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Due Date', text='Due Date')
        self.tree.heading('Created', text='Created')
        
        self.tree.column('#0', width=250)
        self.tree.column('Priority', width=80)
        self.tree.column('Status', width=80)
        self.tree.column('Due Date', width=100)
        self.tree.column('Created', width=100)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Toggle Status", command=self.toggle_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit", command=self.edit_todo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_todo).pack(side=tk.LEFT, padx=5)
        
    def load_todos(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.todos = json.load(f)
        self.refresh_list()
                
    def save_todos(self):
        with open(self.filename, 'w') as f:
            json.dump(self.todos, f)
            
    def add_todo(self):
        todo_text = self.todo_input.get().strip()
        due_date_text = self.due_date.get().strip()
        
        if todo_text:
            try:
                datetime.strptime(due_date_text, '%Y-%m-%d')
                
                todo = {
                    'text': todo_text,
                    'priority': self.priority_var.get(),
                    'status': 'Pending',
                    'due_date': due_date_text,
                    'created': datetime.now().strftime('%Y-%m-%d')
                }
                self.todos.append(todo)
                self.save_todos()
                self.refresh_list()
                self.update_stats()
                self.todo_input.delete(0, tk.END)
                self.due_date.delete(0, tk.END)
                self.due_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
        else:
            messagebox.showwarning("Warning", "Please enter a todo item")
            
    def toggle_status(self):
        selected_item = self.tree.selection()
        if selected_item:
            idx = self.tree.index(selected_item)
            self.todos[idx]['status'] = 'Complete' if self.todos[idx]['status'] == 'Pending' else 'Pending'
            self.save_todos()
            self.refresh_list()
            self.update_stats()
            
    def edit_todo(self):
        selected_item = self.tree.selection()
        if selected_item:
            idx = self.tree.index(selected_item)
            todo = self.todos[idx]
            
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Todo")
            
            edit_entry = ttk.Entry(edit_window, width=40)
            edit_entry.insert(0, todo['text'])
            edit_entry.pack(padx=10, pady=10)
            
            def save_edit():
                new_text = edit_entry.get().strip()
                if new_text:
                    self.todos[idx]['text'] = new_text
                    self.save_todos()
                    self.refresh_list()
                    edit_window.destroy()
                    
            ttk.Button(edit_window, text="Save", command=save_edit).pack(pady=10)
            
    def delete_todo(self):
        selected_item = self.tree.selection()
        if selected_item:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
                idx = self.tree.index(selected_item)
                del self.todos[idx]
                self.save_todos()
                self.refresh_list()
                self.update_stats()
                
    def search_todos(self, *args):
        search_term = self.search_var.get().lower()
        filter_type = self.filter_var.get()
        self.refresh_list(search_term, filter_type)
        
    def refresh_list(self, search_term='', filter_type='All'):
        self.tree.delete(*self.tree.get_children())
        
        for todo in self.todos:
            if search_term and search_term not in todo['text'].lower():
                continue
                
            if filter_type == 'Pending' and todo['status'] != 'Pending':
                continue
            elif filter_type == 'Complete' and todo['status'] != 'Complete':
                continue
            elif filter_type == 'High Priority' and todo.get('priority', 'Medium') != 'High':
                continue
            elif filter_type == 'Overdue':
                try:
                    due_date = datetime.strptime(todo.get('due_date', '9999-12-31'), '%Y-%m-%d').date()
                    if due_date >= date.today() or todo['status'] == 'Complete':
                        continue
                except:
                    continue
            
            tags = []
            if todo.get('priority') == 'High':
                tags.append('high_priority')
            elif todo['status'] == 'Complete':
                tags.append('completed')
            
            try:
                due_date = datetime.strptime(todo.get('due_date', '9999-12-31'), '%Y-%m-%d').date()
                if due_date < date.today() and todo['status'] == 'Pending':
                    tags.append('overdue')
            except:
                pass
            
            self.tree.insert('', tk.END, 
                           text=todo['text'],
                           values=(todo.get('priority', 'Medium'), 
                                 todo['status'], 
                                 todo.get('due_date', 'N/A'),
                                 todo.get('created', 'N/A')),
                           tags=tags)
        
        self.tree.tag_configure('high_priority', background='#ffcccc')
        self.tree.tag_configure('completed', background='#ccffcc')
        self.tree.tag_configure('overdue', background='#ffaaaa', foreground='red')
    
    def update_stats(self):
        total = len(self.todos)
        completed = len([t for t in self.todos if t['status'] == 'Complete'])
        pending = total - completed
        
        overdue = 0
        for todo in self.todos:
            if todo['status'] == 'Pending':
                try:
                    due_date = datetime.strptime(todo.get('due_date', '9999-12-31'), '%Y-%m-%d').date()
                    if due_date < date.today():
                        overdue += 1
                except:
                    pass
        
        stats_text = f"Total: {total} | Completed: {completed} | Pending: {pending} | Overdue: {overdue}"
        self.stats_label.config(text=stats_text)

if __name__ == '__main__':
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()