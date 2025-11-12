import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from cloud import *


def on_checkbox_toggle(task_id, var):
    try:
        # Update Firebase with the new state
        new_value = var.get()
        update_task(task_id, {"completed": new_value})
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update task status:\n{e}")


class TodoApp:
    def __init__(self, root):

        self.root = root
        self.root.title("To-Do App")
        self.root.geometry("420x480")
        self.tasks = []

        # App style
        style = ttk.Style()
        style.theme_use("vista")
        style.configure("TButton", font=("Arial", 11), padding=5)
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TCheckbutton", font=("Arial", 12))

        # --- Top Frame (Add Task) ---
        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(fill="x")

        self.entry = ttk.Entry(top_frame, width=30, font=("Arial", 13))
        self.entry.grid(row=0, column=0, padx=(0, 10))

        ttk.Button(top_frame, text="Add", command=self.add_task).grid(row=0, column=1)

        # --- Search Bar ---
        search_frame = ttk.Frame(root, padding=(10, 0))
        search_frame.pack(fill="x")

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<KeyRelease>", self.filter_tasks)

        # --- Scrollable Area for Tasks ---
        list_frame = ttk.Frame(root, padding=(10, 5))
        list_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(list_frame, borderwidth=0)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # --- Bottom Buttons ---
        bottom_frame = ttk.Frame(root, padding=10)
        bottom_frame.pack(fill="x")

        ttk.Button(bottom_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=5)
        # Load tasks from Firebase
        self.load_tasks()

    def add_task(self):
        task_text = self.entry.get().strip()
        if not task_text:
            messagebox.showwarning("Warning", "Task cannot be empty!")
            return

        # Checking duplicate tasks
        if any(cb.cget("text").strip().lower() == task_text.lower() for cb, _, _ in self.tasks):
            messagebox.showinfo("Duplicate", f"'{task_text}' already exists!")
            return

        try:
            # Send new task to Firebase
            add_task(task_text)

            # Clear the entry
            self.entry.delete(0, "end")

            # Re-load everything from the cloud
            self.refresh_ui()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add task:\n{e}")

    @staticmethod
    def edit_task(cb):
        new_text = simpledialog.askstring("Edit Task", "Edit task:", initialvalue=cb.cget("text"))
        if new_text:
            cb.config(text=new_text)

    def delete_selected(self):
        # Find all checked items
        to_delete = [t for t in self.tasks if t[1].get()]
        if not to_delete:
            messagebox.showinfo("Info", "Check items you want to delete.")
            return

        if messagebox.askyesno("Confirm Delete", f"Delete {len(to_delete)} selected tasks?"):
            for cb, var, task_id in to_delete:
                cb.destroy()
                self.tasks.remove((cb, var, task_id))
                # Also delete from Firebase
                try:
                    delete_task(task_id)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete from cloud:\n{e}")

    def load_tasks(self):
        data = get_tasks()
        for task_id, info in data.items():
            var = tk.BooleanVar(value=info.get("completed", False))

            # callback when checkbox is clicked
            cb = ttk.Checkbutton(
                self.scroll_frame,
                text=info["text"],
                variable=var,
                style="TCheckbutton",
                command=lambda id=task_id, v=var: on_checkbox_toggle(id, v)
            )
            cb.pack(fill="x", pady=2)
            cb.bind("<Double-Button-1>", lambda e, cb=cb, id=task_id: self.edit_task(cb, id))

            self.tasks.append((cb, var, task_id))

    def filter_tasks(self, event=None):
        """Hide tasks that don't match the search text."""
        search_text = self.search_var.get().strip().lower()

        for cb, var, task_id in self.tasks:
            task_label = cb.cget("text").lower()

            # Show if it matches the search text
            if search_text in task_label:
                cb.pack(fill="x", pady=2)
            else:
                # Hide the task
                cb.pack_forget()

    def refresh_ui(self):
        for cb, _, _ in self.tasks:
            cb.destroy()
        self.tasks.clear()
        self.load_tasks()