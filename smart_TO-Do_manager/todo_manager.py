import json
import os

# ==========================================
# 1. OOP Structure & Data Handling
# ==========================================
class Task:
    """Represents a single task."""
    def __init__(self, task_id, title, status="Pending"):
        self.id = task_id
        self.title = title
        self.status = status

    def to_dict(self):
        """Converts the Task object to a dictionary for JSON saving."""
        return {"id": self.id, "title": self.title, "status": self.status}

class TaskManager:
    """Manages the list of tasks and file operations."""
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """Loads tasks from the JSON file (Persistent Storage)."""
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                # Reconstruct Task objects from dictionaries
                return [Task(item['id'], item['title'], item['status']) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_tasks(self):
        """Saves tasks to the JSON file."""
        with open(self.filename, 'w') as file:
            json.dump([task.to_dict() for task in self.tasks], file, indent=4)

    def add_task(self, title):
        """CREATE operation."""
        if not title.strip():
            print("❌ Error: Task title cannot be empty.")
            return
        
        # Generate a new ID based on the highest existing ID
        new_id = max([task.id for task in self.tasks], default=0) + 1
        new_task = Task(new_id, title)
        self.tasks.append(new_task)
        self.save_tasks()
        print(f"✅ Task '{title}' added successfully!")

    def view_tasks(self):
        """READ operation."""
        if not self.tasks:
            print("\n📭 Your to-do list is empty.")
            return
        
        print("\n--- 📝 YOUR TO-DO LIST ---")
        for task in self.tasks:
            status_icon = "✅" if task.status == "Completed" else "⏳"
            print(f"[{task.id}] {status_icon} {task.title}")
        print("--------------------------")

    def update_task(self, task_id, new_title):
        """UPDATE operation (Title)."""
        for task in self.tasks:
            if task.id == task_id:
                task.title = new_title
                self.save_tasks()
                print(f"✅ Task {task_id} updated to '{new_title}'.")
                return
        print(f"❌ Error: Task with ID {task_id} not found.")

    def toggle_status(self, task_id):
        """UPDATE operation (Status)."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "Completed" if task.status == "Pending" else "Pending"
                self.save_tasks()
                print(f"✅ Task {task_id} marked as {task.status}.")
                return
        print(f"❌ Error: Task with ID {task_id} not found.")

    def delete_task(self, task_id):
        """DELETE operation."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                deleted_task = self.tasks.pop(i)
                self.save_tasks()
                print(f"🗑️ Task '{deleted_task.title}' deleted.")
                return
        print(f"❌ Error: Task with ID {task_id} not found.")

# ==========================================
# 2. CLI (Command-Line Interface) & Flowchart Logic
# ==========================================

def get_valid_integer_input(prompt):
    """Input Validation & Error Handling."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def main():
    # Step 1: Start & Load Tasks
    manager = TaskManager()
    
    while True:
        # Step 2: Show Menu
        print("\n=================================")
        print("🌟 SMART TO-DO MANAGER 🌟")
        print("=================================")
        print("1. View Tasks")
        print("2. Add Task")
        print("3. Update Task Title")
        print("4. Mark Task as Complete/Pending")
        print("5. Delete Task")
        print("6. Exit")
        print("=================================")
        
        choice = input("Select an option (1-6): ").strip()

        if choice == '1':
            # Step 3: Display Updated List
            manager.view_tasks()
            
        elif choice == '2':
            # Step 3: Add
            title = input("Enter new task description: ")
            manager.add_task(title)
            
        elif choice == '3':
            # Step 3: Update
            manager.view_tasks()
            if manager.tasks:
                task_id = get_valid_integer_input("Enter the ID of the task to update: ")
                new_title = input("Enter the new task description: ")
                manager.update_task(task_id, new_title)
                
        elif choice == '4':
            # Step 3: Update (Status)
            manager.view_tasks()
            if manager.tasks:
                task_id = get_valid_integer_input("Enter the ID of the task to toggle status: ")
                manager.toggle_status(task_id)
                
        elif choice == '5':
            # Step 3: Delete
            manager.view_tasks()
            if manager.tasks:
                task_id = get_valid_integer_input("Enter the ID of the task to delete: ")
                manager.delete_task(task_id)
                
        elif choice == '6':
            # Step 4: Continue (Exit loop)
            print("👋 Goodbye! Your tasks have been saved.")
            break
            
        else:
            # Input Validation
            print("❌ Invalid choice. Please select a number between 1 and 6.")

if __name__ == "__main__":
    main()