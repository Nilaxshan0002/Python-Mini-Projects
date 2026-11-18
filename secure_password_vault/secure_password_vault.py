
import tkinter as tk
from tkinter import messagebox
import json
import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ==========================================
# 1. Security & Encryption Core
# ==========================================
class SecurityManager:
    """Handles Master Password Hashing, Key Derivation, and Encryption."""
    def __init__(self, vault_file="vault_data.json", key_file="master.key"):
        self.vault_file = vault_file
        self.key_file = key_file

    def hash_master_password(self, password):
        """Hashes the master password using SHA-256 for authentication."""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_key(self, password, salt):
        """Derives a strong encryption key from the master password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def load_vault_data(self):
        """Loads the vault JSON file."""
        if not os.path.exists(self.vault_file):
            return {"master_hash": None, "salt": None, "passwords": []}
        try:
            with open(self.vault_file, 'r') as f:
                data = json.load(f)
                # Convert salt string back to bytes
                if data["salt"]:
                    data["salt"] = base64.b64decode(data["salt"])
                return data
        except (json.JSONDecodeError, KeyError):
            return {"master_hash": None, "salt": None, "passwords": []}

    def save_vault_data(self, data):
        """Saves the vault JSON file."""
        # Convert salt bytes to string for JSON saving
        save_data = data.copy()
        if save_data["salt"]:
            save_data["salt"] = base64.b64encode(save_data["salt"]).decode('utf-8')
            
        with open(self.vault_file, 'w') as f:
            json.dump(save_data, f, indent=4)


# ==========================================
# 2. GUI Application (Tkinter)
# ==========================================
class PasswordVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Secure Password Vault")
        self.root.geometry("500x400")
        self.security = SecurityManager()
        self.vault_data = self.security.load_vault_data()
        self.cipher_suite = None # Will hold the Fernet encryption object

        self.setup_auth_screen()

    def clear_screen(self):
        """Clears the current GUI elements."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- Authentication Flowchart ---
    def setup_auth_screen(self):
        """Master Access -> Authenticate"""
        self.clear_screen()
        
        # Check if this is a first-time setup
        is_new_vault = self.vault_data["master_hash"] is None

        tk.Label(self.root, text="🔐 Secure Password Vault", font=("Arial", 18, "bold")).pack(pady=20)

        if is_new_vault:
            tk.Label(self.root, text="Create a Master Password:", font=("Arial", 12)).pack(pady=5)
        else:
            tk.Label(self.root, text="Enter Master Password:", font=("Arial", 12)).pack(pady=5)

        self.master_entry = tk.Entry(self.root, show="*", font=("Arial", 12))
        self.master_entry.pack(pady=5)

        btn_text = "Create Vault" if is_new_vault else "Unlock Vault"
        tk.Button(self.root, text=btn_text, command=self.handle_auth, font=("Arial", 12), bg="blue", fg="white").pack(pady=20)

    def handle_auth(self):
        """Validates the master password."""
        password = self.master_entry.get()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return

        if self.vault_data["master_hash"] is None:
            # First time setup
            salt = os.urandom(16)
            master_hash = self.security.hash_master_password(password)
            self.vault_data["master_hash"] = master_hash
            self.vault_data["salt"] = salt
            self.security.save_vault_data(self.vault_data)
            messagebox.showinfo("Success", "Vault created successfully!")
            self.unlock_vault(password, salt)
        else:
            # Existing vault
            if self.security.hash_master_password(password) == self.vault_data["master_hash"]:
                self.unlock_vault(password, self.vault_data["salt"])
            else:
                messagebox.showerror("Access Denied", "Incorrect Master Password.")

    def unlock_vault(self, password, salt):
        """Generates the encryption key and opens the main vault interface."""
        key = self.security.generate_key(password, salt)
        self.cipher_suite = Fernet(key)
        self.setup_main_screen()

    # --- Main Vault Interface ---
    def setup_main_screen(self):
        """GUI Display -> Controlled Retrieval"""
        self.clear_screen()
        tk.Label(self.root, text="🔓 Vault Unlocked", font=("Arial", 16, "bold"), fg="green").pack(pady=10)

        # --- Add New Password Frame ---
        frame_add = tk.LabelFrame(self.root, text="Add New Credential", padx=10, pady=10)
        frame_add.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_add, text="Website/App:").grid(row=0, column=0, sticky="w")
        self.entry_site = tk.Entry(frame_add, width=30)
        self.entry_site.grid(row=0, column=1, pady=2)

        tk.Label(frame_add, text="Username:").grid(row=1, column=0, sticky="w")
        self.entry_user = tk.Entry(frame_add, width=30)
        self.entry_user.grid(row=1, column=1, pady=2)

        tk.Label(frame_add, text="Password:").grid(row=2, column=0, sticky="w")
        self.entry_pass = tk.Entry(frame_add, width=30, show="*")
        self.entry_pass.grid(row=2, column=1, pady=2)

        tk.Button(frame_add, text="Save (Encrypt)", command=self.save_password, bg="green", fg="white").grid(row=3, column=1, pady=5, sticky="e")

        # --- View Passwords Frame ---
        frame_view = tk.LabelFrame(self.root, text="Stored Credentials", padx=10, pady=10)
        frame_view.pack(fill="both", expand=True, padx=20, pady=10)

        self.listbox = tk.Listbox(frame_view, height=8, font=("Courier", 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(frame_view, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        tk.Button(self.root, text="View/Decrypt Selected", command=self.view_selected, bg="blue", fg="white").pack(pady=5)

        self.refresh_listbox()

    # --- Data Storage & Encryption ---
    def save_password(self):
        """Protect Sensitive Data -> Secure Storage"""
        site = self.entry_site.get().strip()
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get()

        if not site or not user or not pwd:
            messagebox.showwarning("Input Validation", "All fields are required.")
            return

        # Encrypt the password
        encrypted_pwd = self.cipher_suite.encrypt(pwd.encode()).decode('utf-8')

        # Save to dictionary
        self.vault_data["passwords"].append({
            "site": site,
            "username": user,
            "password": encrypted_pwd
        })
        
        self.security.save_vault_data(self.vault_data)
        messagebox.showinfo("Success", f"Credentials for {site} saved securely.")
        
        # Clear inputs
        self.entry_site.delete(0, tk.END)
        self.entry_user.delete(0, tk.END)
        self.entry_pass.delete(0, tk.END)
        
        self.refresh_listbox()

    def refresh_listbox(self):
        """Updates the GUI list of saved passwords."""
        self.listbox.delete(0, tk.END)
        for item in self.vault_data["passwords"]:
            self.listbox.insert(tk.END, f"🌐 {item['site']} | 👤 {item['username']}")

    # --- Controlled Retrieval ---
    def view_selected(self):
        """Decrypts and displays the selected password."""
        try:
            index = self.listbox.curselection()[0]
            item = self.vault_data["passwords"][index]
            
            # Decrypt the password
            decrypted_pwd = self.cipher_suite.decrypt(item["password"].encode()).decode('utf-8')
            
            # Show in a popup
            messagebox.showinfo(
                "Decrypted Credential", 
                f"Website: {item['site']}\nUsername: {item['username']}\nPassword: {decrypted_pwd}"
            )
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select a credential from the list.")

# ==========================================
# 3. Start Application
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordVaultApp(root)
    root.mainloop()