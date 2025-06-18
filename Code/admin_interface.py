import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
from path_utils import get_image_path
from db_utils import get_connection

class AdminInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Administrator Interface")
        self.geometry("800x600")  # Set the size of the window

        # Connect to the SQLite database
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        # Load the background image
        self.background_image = Image.open(get_image_path("bg2.png"))  # Replace "bg2.png" with your image file
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.place(relx=0.5, rely=0.5, anchor="center")

        # Add Account Button
        self.add_account_button = ttk.Button(self, text="Add Account", command=self.show_account_creation_window)
        self.add_account_button.place(relx=0.5, rely=0.1, anchor="center")

        # Check Your Account Treeview
        self.account_tree = ttk.Treeview(self, columns=("Creation Time", "Account Name", "Account Type", "Password"), selectmode="browse")
        self.account_tree.heading("#0", text="", anchor="center")
        self.account_tree.heading("Creation Time", text="Creation Time")
        self.account_tree.heading("Account Name", text="Account Name")
        self.account_tree.heading("Account Type", text="Account Type")
        self.account_tree.heading("Password", text="Password")
        self.account_tree.column("#0", stretch=False, width=1)
        self.account_tree.column("Creation Time", anchor="center", width=150)
        self.account_tree.column("Account Name", anchor="center", width=150)
        self.account_tree.column("Account Type", anchor="center", width=150)  # New column for account type
        self.account_tree.column("Password", anchor="center", width=150)
        self.account_tree.place(relx=0.5, rely=0.5, anchor="center", relwidth=1 , relheight=2/3)  # Span the entire width

        # Load accounts from database
        self.load_accounts()

        # Bind double click event to treeview item
        self.account_tree.bind("<Double-1>", self.on_account_double_click)

        # Bind close event to save accounts
        self.protocol("WM_DELETE_WINDOW", self.save_accounts)

        # Logout Button
        self.logout_button = ttk.Button(self, text="Logout", command=self.logout)
        self.logout_button.place(relx=0.9, rely=0.1, anchor="center")

    def logout(self):
        # Đóng cửa sổ giao diện quản trị viên và thoát
        self.destroy()
        from SuperMaket_Interface import LoginScreen
        LoginScreen().mainloop()

    def add_account(self):
        # Display account creation window
        self.show_account_creation_window()

    def show_account_creation_window(self):
        # Create a top-level window for account creation
        account_creation_window = tk.Toplevel(self)
        account_creation_window.title("Create New Account")

        # Disable interaction with main window until this window is closed
        account_creation_window.grab_set()

        # Label and Combobox for selecting account type
        ttk.Label(account_creation_window, text="Select Account Type:").pack()
        account_type_var = tk.StringVar(account_creation_window)
        account_type_combobox = ttk.Combobox(account_creation_window, textvariable=account_type_var, values=["Cashier", "Manager"])
        account_type_combobox.pack(pady=5)

        # Label and Entry for account name
        ttk.Label(account_creation_window, text="Enter Account Name:").pack()
        account_name_entry = ttk.Entry(account_creation_window)
        account_name_entry.pack(pady=5)

        # Label and Entry for password
        ttk.Label(account_creation_window, text="Enter Password:").pack()
        password_entry = ttk.Entry(account_creation_window)
        password_entry.pack(pady=5)

        # Button to create the account
        create_button = ttk.Button(account_creation_window, text="Create Account", command=lambda: self.create_account(account_type_var.get(), account_name_entry.get(), password_entry.get(), account_creation_window))
        create_button.pack(pady=5)

        # Close account creation window event
        account_creation_window.protocol("WM_DELETE_WINDOW", lambda: self.close_account_creation_window(account_creation_window))

    def create_account(self, account_type, account_name, password, account_creation_window):
        # Kiểm tra xem tên tài khoản mới có trùng với các tài khoản hiện có không
        query = "SELECT username FROM accounts WHERE username = ?"
        self.cursor.execute(query, (account_name,))
        existing_account = self.cursor.fetchone()
        if existing_account:
            messagebox.showerror("Duplicate Account", f"An account with the username '{account_name}' already exists. Please choose a different username.")
            return

        # Nếu không có tài khoản trùng lặp, thêm tài khoản mới vào cơ sở dữ liệu và cập nhật giao diện
        query = "INSERT INTO accounts (username, role, password) VALUES (?, ?, ?)"
        self.cursor.execute(query, (account_name, account_type, password))
        self.conn.commit()

        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.account_tree.insert("", "end", text="", values=(creation_time, account_name, account_type, password))
        account_creation_window.destroy()
        self.grab_release()

    def load_accounts(self):
        query = "SELECT creation_time, username, role, password FROM accounts"  # Sửa câu lệnh SELECT
        self.cursor.execute(query)
        accounts = self.cursor.fetchall()
        for account in accounts:
            self.account_tree.insert("", "end", text="", values=(account[0], account[1], account[2], account[3]))  # Điều chỉnh chỉ số cột


    def save_accounts(self):
        # Nothing to save since accounts are stored in the database
        self.destroy()

    def on_account_double_click(self, event):
        # Implement what happens when an account is double-clicked
        selected_item = self.account_tree.selection()[0]
        account_name = self.account_tree.item(selected_item, "values")[1]

        # Display notification panel with options to delete or change password
        self.show_notification_panel(account_name)

    def show_notification_panel(self, account_name):
        # Create a top-level window for the notification panel
        notification_panel = tk.Toplevel(self)
        notification_panel.title("Account Options")

        # Disable interaction with main window until this window is closed
        notification_panel.grab_set()

        # Label
        label = ttk.Label(notification_panel, text=f"What would you like to do with account '{account_name}'?")
        label.pack(pady=10)

        # Delete Account Button
        delete_button = ttk.Button(notification_panel, text="Delete Account", command=lambda: self.delete_account(account_name, notification_panel))
        delete_button.pack(pady=5)

        # Change Password Button
        change_password_button = ttk.Button(notification_panel, text="Change Password", command=lambda: self.change_password(account_name, notification_panel))
        change_password_button.pack(pady=5)

        # Close notification panel event
        notification_panel.protocol("WM_DELETE_WINDOW", lambda: self.close_notification_panel(notification_panel))

    def delete_account(self, account_name, notification_panel):
        query = "DELETE FROM accounts WHERE username = ?"
        self.cursor.execute(query, (account_name,))
        self.conn.commit()

        selected_item = self.account_tree.selection()[0]
        self.account_tree.delete(selected_item)
        notification_panel.destroy()
        self.grab_release()

    def close_change_password_window(self, window):
        # Đóng cửa sổ đổi mật khẩu và phát hành khóa chính
        window.destroy()
        self.grab_release()

    def change_password(self, account_name, notification_panel):
        # Create a top-level window for changing password
        change_password_window = tk.Toplevel(self)
        change_password_window.title("Change Password")

        # Disable interaction with main window until this window is closed
        change_password_window.grab_set()

        # Label and Entry for new password
        ttk.Label(change_password_window, text="Enter New Password:").pack()
        new_password_entry = ttk.Entry(change_password_window)
        new_password_entry.pack(pady=5)

        # Label and Entry for confirming new password
        ttk.Label(change_password_window, text="Confirm New Password:").pack()
        confirm_password_entry = ttk.Entry(change_password_window)
        confirm_password_entry.pack(pady=5)

        # Button to change the password
        change_button = ttk.Button(change_password_window, text="Change Password", command=lambda: self.update_password(account_name, new_password_entry.get(), confirm_password_entry.get(), change_password_window))
        change_button.pack(pady=5)

        # Close change password window event
        change_password_window.protocol("WM_DELETE_WINDOW", lambda: self.close_change_password_window(change_password_window))

    def update_password(self, account_name, new_password, confirm_password, change_password_window):
        if new_password != confirm_password:
            messagebox.showerror("Password Error", "New password and confirm password do not match.")
            return

        query = "UPDATE accounts SET password = ? WHERE username = ?"
        self.cursor.execute(query, (new_password, account_name))
        self.conn.commit()

        selected_item = self.account_tree.selection()[0]
        self.account_tree.set(selected_item, "Password", new_password)

        messagebox.showinfo("Password Changed", "Password has been successfully changed.")
        change_password_window.destroy()
        self.grab_release()

    def close_notification_panel(self, window):
        # Close the notification panel
        window.destroy()
        self.grab_release()  # Allow interaction with main window again

    def close_account_creation_window(self, window):
        # Close the account creation window
        window.destroy()
        self.grab_release()  # Allow interaction with main window again

if __name__ == "__main__":
    app = AdminInterface()
    app.mainloop()