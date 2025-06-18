import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import sqlite3
from admin_interface import AdminInterface
from manager_interface import ManagerInterface
from cashier_interface import CashierInterface
from datetime import datetime
from path_utils import get_image_path 
from db_utils import get_connection

class LoginScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Supermarket Management System - Login")
        self.geometry("600x400")  

        # Connect to the SQLite database
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        # Load background image using the path utility
        self.background_image = Image.open(get_image_path("bg1.png"))
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.place(relx=0.5, rely=0.5, anchor="center")


        # Frame for role buttons
        button_frame = tk.Frame(self, highlightthickness=0)  # Remove border
        button_frame.place(relx=0.5, rely=0.4, anchor="center")  # Centered horizontally

        # Button colors and corresponding roles
        self.button_colors = {"Cashier": "LightGray", "Manager": "LightGray", "Administrator": "LightGray"}
        self.selected_role = None
        for role, color in self.button_colors.items():
            role_button = tk.Button(button_frame, text=role.upper(), bg=color, font=("Arial", 12, "bold"),
                                    width=15, height=5, command=lambda r=role: self.toggle_role_selection(r))
            role_button.pack(side="left")  # Remove padx for no spacing between buttons

        # Account Name Input
        self.account_name_var = tk.StringVar()
        self.account_name_entry = tk.Entry(self, textvariable=self.account_name_var, font=("Arial", 12), width=20)
        self.account_name_entry.place(relx=0.5, rely=0.7, anchor="center")  # Centered horizontally

        # Password Input
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(self, textvariable=self.password_var, show="*", font=("Arial", 12), width=20)
        self.password_entry.place(relx=0.5, rely=0.8, anchor="center")  # Centered horizontally
        self.password_entry.config(state="disabled")  # Password entry initially disabled

        # Login Button
        self.login_button = tk.Button(self, text="Login", font=("Arial", 12, "bold"), command=self.login)
        self.login_button.place(relx=0.5, rely=0.9, anchor="center")  # Centered horizontally

        # Binding the Enter key to login function
        self.bind("<Return>", lambda event: self.login())

        # Check and create default admin account
        self.check_default_admin()

    def toggle_role_selection(self, role):
        if self.selected_role == role:
            # Deselect the role if it's already selected
            self.selected_role = None
            self.update_button_colors()
            
        else:
            # Select the role if it's not already selected
            self.selected_role = role
            self.update_button_colors()
            self.password_entry.config(state="normal")

    def update_button_colors(self):
        for role, color in self.button_colors.items():
            # Update button color based on selection status
            if role == self.selected_role:
                new_color = "Lightgreen"  # Change color when selected
            else:
                new_color = color  # Revert to original color when not selected

            # Find the corresponding button and update its color
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    for button in widget.winfo_children():
                        if button["text"].lower() == role.lower():
                            button.config(bg=new_color)


    def authenticate(self, role, account_name, password):
        query = "SELECT * FROM accounts WHERE username = ? AND password = ? AND role = ?"
        self.cursor.execute(query, (account_name, password, role))
        account = self.cursor.fetchone()
        return account is not None

    def login(self):
        role = self.selected_role
        account_name = self.account_name_var.get()
        password = self.password_var.get()

        # Dummy validation for demonstration (replace with actual validation logic)
        if role and account_name and password:
            if self.authenticate(role, account_name, password):
                messagebox.showinfo("Login Successful", f"Logged in as {role}")
                # Redirect to respective interface based on role
                if role == "Cashier":
                    self.destroy()
                    # Pass username to the cashier interface
                    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    query = "INSERT INTO cashier_activity (cashier_username, login_time) VALUES (?, ?)"
                    self.cursor.execute(query, (account_name, login_time))
                    self.conn.commit()
                    cashier_interface = CashierInterface(account_name)
                    cashier_interface.mainloop()
                elif role == "Manager":
                    # Open manager interface
                    self.destroy()  # Close the login interface
                    manager_interface = ManagerInterface()
                    manager_interface.mainloop()
                elif role == "Administrator":
                    # Open administrator interface
                    self.destroy()  # Close the login interface
                    admin_interface = AdminInterface()  # Instantiate AdminInterface
                    admin_interface.mainloop()  # Run the administrator interface
            else:
                messagebox.showerror("Login Failed", "Invalid credentials.")
        else:
            messagebox.showerror("Login Failed", "Please select a user role, enter an account name, and enter a password.")



    def check_default_admin(self):
        query = "SELECT * FROM accounts WHERE username = 'admin' AND password = 'admin' AND role = 'Administrator'"
        self.cursor.execute(query)
        admin_account = self.cursor.fetchone()
        if not admin_account:
            query = "INSERT INTO accounts (username, password, role) VALUES ('admin', 'admin', 'Administrator')"
            self.cursor.execute(query)
            self.conn.commit()

    def __del__(self):
        # Close the database connection
        self.conn.close()

if __name__ == "__main__":
    app = LoginScreen()
    app.mainloop()
