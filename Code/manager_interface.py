import tkinter as tk
from tkinter import Toplevel, Entry, Button, Label, Frame, messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
from db_utils import get_connection
import os

class ManagerInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Supermarket Management System")
        self.geometry("800x600")  # Increased size of the window

        # Thiết lập màu sắc và kích thước
        self.bg_color = "#f0f0f0"
        self.btn_color = "#4CAF50"
        self.btn_fg_color = "#ffffff"
        self.entry_bg_color = "#ffffff"
        self.entry_fg_color = "#000000"
        self.label_bg_color = "#cccccc"
        self.label_fg_color = "#000000"
        self.font = ("Arial", 12)

        # Logout Button
        self.logout_button = ttk.Button(self, text="Logout", command=self.logout)
        self.logout_button.place(relx=0.9, rely=0.1, anchor="center")

        self.configure(bg=self.bg_color)
        self.create_main_buttons()

        # Database connection
        self.connect_to_database()

    def connect_to_database(self):
        try:
            self.conn = get_connection()
            self.cursor = self.conn.cursor()
            # Check if the products table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            if not self.cursor.fetchone():
                raise sqlite3.DatabaseError("The 'products' table does not exist.")
            # Check if the transactions table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
            if not self.cursor.fetchone():
                raise sqlite3.DatabaseError("The 'transactions' table does not exist.")
        except sqlite3.DatabaseError as e:
            messagebox.showerror("Database Error", f"Database connection failed: {e}")
            self.destroy()

    def create_main_buttons(self):
        Button(self, text="Quản lý Nhân viên", command=self.nhan_vien, bg=self.btn_color, fg=self.btn_fg_color, font=self.font, width=30).pack(pady=20)
        Button(self, text="Quản lý Hàng hóa", command=self.hang_hoa, bg=self.btn_color, fg=self.btn_fg_color, font=self.font, width=30).pack(pady=20)
        Button(self, text="Tra soát Giao dịch", command=self.giao_dich, bg=self.btn_color, fg=self.btn_fg_color, font=self.font, width=30).pack(pady=20)

    def _on_mouse_wheel(self, event, canvas):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel_to_scrollbar(self, canvas):
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def create_scrollable_frame(self, parent):
        container = tk.Frame(parent, bg=self.bg_color)
        canvas = tk.Canvas(container, bg=self.bg_color)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Kích hoạt cuộn chuột bất kỳ trong cửa sổ
        self._bind_mousewheel_to_scrollbar(canvas)

        return scrollable_frame

    def logout(self):
        # Đóng cửa sổ giao diện quản trị viên và thoát
        self.destroy()
        from SuperMaket_Interface import LoginScreen
        LoginScreen().mainloop()

    

    def nhan_vien(self):
        # Tạo cửa sổ mới
        new_window = tk.Toplevel(self)
        new_window.title("Quản lý Nhân viên")
        new_window.geometry("1000x600")
        new_window.configure(bg=self.bg_color)

        # Tạo khung cuộn
        frame = self.create_scrollable_frame(new_window)
        # Gắn sự kiện cuộn chuột
        frame.bind_all("<MouseWheel>", lambda event: self._on_mouse_wheel(event, frame))


        # Các cột
        columns = ["Tên nhân viên", "Giờ đăng nhập", "Giờ đăng xuất", "Giờ hoạt động"]

        # Hiển thị các cột ở hàng đầu tiên
        for col_index, col_name in enumerate(columns):
            label = tk.Label(frame, text=col_name, bg=self.label_bg_color, fg=self.label_fg_color, font=self.font, borderwidth=2, relief="groove", width=20, anchor="center")
            label.grid(row=0, column=col_index, padx=5, pady=5, sticky='nsew')

        # Đảm bảo các cột căn đều
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Truy vấn dữ liệu từ cơ sở dữ liệu
        self.cursor.execute("SELECT cashier_username, login_time, logout_time, active_hours FROM cashier_activity")
        data = self.cursor.fetchall()

        # Hiển thị dữ liệu từ cơ sở dữ liệu
        for row_index, row_data in enumerate(data, start=1):
            for col_index, value in enumerate(row_data):
                label = tk.Label(frame, text=value, bg=self.label_bg_color, fg=self.label_fg_color, font=self.font, borderwidth=2, relief="groove", width=20, anchor="center")
                label.grid(row=row_index, column=col_index, padx=5, pady=5, sticky='nsew')
                
                # Add double-click event to the employee name
                if col_index == 0:
                    label.bind("<Double-1>", lambda e, name=value: self.show_total_hours(name))

        # Thêm nút đóng bên dưới khung cuộn
        close_button = tk.Button(new_window, text="Đóng", command=new_window.destroy, bg=self.btn_color, fg=self.btn_fg_color, font=self.font)
        close_button.pack(pady=10)

    def show_total_hours(self, cashier_username):
        # Truy vấn tất cả giờ hoạt động của nhân viên từ cơ sở dữ liệu
        self.cursor.execute("SELECT active_hours FROM cashier_activity WHERE cashier_username=?", (cashier_username,))
        data = self.cursor.fetchall()

        # Chuyển đổi tất cả giờ hoạt động thành tổng số phút
        total_minutes = 0
        for entry in data:
            hours, minutes = map(int, entry[0].split(':'))
            total_minutes += hours * 60 + minutes

        # Chuyển đổi tổng số phút thành định dạng giờ:phút
        total_hours = total_minutes // 60
        total_minutes = total_minutes % 60
        total_time_formatted = f"{total_hours:02}:{total_minutes:02}"

        # Tính tổng số tiền phải trả
        wage_per_hour = 25000
        wage_per_minute = wage_per_hour / 60
        total_payment = total_minutes * wage_per_minute + total_hours * wage_per_hour
        
        # Tạo cửa sổ thông báo tùy chỉnh
        payment_window = tk.Toplevel(self)
        payment_window.title("Tổng số giờ hoạt động và số tiền phải trả")
        payment_window.geometry("400x200")
        
        label = tk.Label(payment_window, text=f"Nhân viên {cashier_username} đã làm việc tổng cộng {total_time_formatted} giờ.\n"
                                              f"Tổng số tiền phải trả: {total_payment:,.0f} VND.",
                         font=self.font, wraplength=300)
        label.pack(pady=20)

        # Button Thanh toán
        pay_button = tk.Button(payment_window, text="Thanh toán", command=lambda: self.thanh_toan(cashier_username, payment_window), bg=self.btn_color, fg=self.btn_fg_color, font=self.font)
        pay_button.pack(side="left", padx=10, pady=10)

        # Button OK
        ok_button = tk.Button(payment_window, text="OK", command=payment_window.destroy, bg=self.btn_color, fg=self.btn_fg_color, font=self.font)
        ok_button.pack(side="right", padx=10, pady=10)

    def thanh_toan(self, cashier_username, payment_window):
        # Xóa dữ liệu làm việc của nhân viên từ cơ sở dữ liệu
        self.cursor.execute("DELETE FROM cashier_activity WHERE cashier_username=?", (cashier_username,))
        self.conn.commit()
        
        # Đóng cửa sổ thông báo thanh toán
        payment_window.destroy()
        
        # Hiển thị thông báo xác nhận thanh toán
        messagebox.showinfo("Thanh toán thành công", f"Đã thanh toán và xóa dữ liệu cho nhân viên {cashier_username}.")

    
    def hang_hoa(self):
        new_window = Toplevel(self)
        new_window.title("Quản lý Hàng hóa")
        new_window.geometry("1000x600")
        new_window.configure(bg=self.bg_color)

        frame = self.create_scrollable_frame(new_window)

        columns = ["ID", "Tên sản phẩm", "Giá", "Số lượng"]
        for col_index, col_name in enumerate(columns):
            label = Label(frame, text=col_name, borderwidth=2, relief="groove", bg=self.label_bg_color, fg=self.label_fg_color, font=self.font)
            label.grid(row=0, column=col_index, padx=5, pady=5, sticky='nsew')

        # Fetch data from the products table
        self.cursor.execute("SELECT id, name, price, quantity FROM products")
        products = self.cursor.fetchall()

        self.entries = []
        for i, product in enumerate(products, start=1):
            entry_row = []
            for j, value in enumerate(product):
                entry = Entry(frame, bg=self.entry_bg_color, fg=self.entry_fg_color, font=self.font)
                entry.insert(0, value)
                entry.grid(row=i, column=j, padx=5, pady=5)
                if j == 0:  # ID should not be editable
                    entry.config(state='readonly')
                entry_row.append(entry)
            self.entries.append(entry_row)

        Button(frame, text="Cập nhật", command=self.update_products, bg=self.btn_color, fg=self.btn_fg_color, font=self.font).grid(row=len(products) + 1, columnspan=4, pady=10)
        Button(frame, text="Đóng", command=new_window.destroy, bg=self.btn_color, fg=self.btn_fg_color, font=self.font).grid(row=len(products) + 2, columnspan=4, pady=10)

    def update_products(self):
        try:
            for entry_row in self.entries:
                product_id = entry_row[0].get()
                name = entry_row[1].get()
                price = entry_row[2].get()
                quantity = entry_row[3].get()
                self.cursor.execute("""
                    UPDATE products
                    SET name = ?, price = ?, quantity = ?
                    WHERE id = ?
                """, (name, price, quantity, product_id))
            self.conn.commit()
            messagebox.showinfo("Thông báo", "Cập nhật thành công")
        except sqlite3.DatabaseError as e:
            messagebox.showerror("Database Error", f"Failed to update products: {e}")

    def giao_dich(self):
        new_window = Toplevel(self)
        new_window.title("Tra soát Giao dịch")
        new_window.geometry("1000x600")
        new_window.configure(bg=self.bg_color)

        # Create date filter widgets
        filter_frame = Frame(new_window, bg=self.bg_color)
        filter_frame.pack(pady=10)

        Label(filter_frame, text="Từ ngày:", bg=self.bg_color, fg=self.label_fg_color, font=self.font).pack(side="left")
        self.from_date = DateEntry(filter_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.from_date.pack(side="left", padx=5)

        Label(filter_frame, text="Đến ngày:", bg=self.bg_color, fg=self.label_fg_color, font=self.font).pack(side="left", padx=5)
        self.to_date = DateEntry(filter_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.to_date.pack(side="left", padx=5)

        search_button = Button(filter_frame, text="Tra cứu", command=self.search_transactions, bg=self.btn_color, fg=self.btn_fg_color, font=self.font)
        search_button.pack(side="left", padx=10)

        self.transaction_frame = self.create_scrollable_frame(new_window)

        # Display all transactions by default
        self.display_all_transactions()

        # Thêm nút đóng bên dưới khung cuộn
        close_button = tk.Button(new_window, text="Đóng", command=new_window.destroy, bg=self.btn_color, fg=self.btn_fg_color, font=self.font)
        close_button.pack(pady=10)
    
    def display_all_transactions(self):
        # Clear existing content in the transaction frame
        for widget in self.transaction_frame.winfo_children():
            widget.destroy()

        # Define column headers
        columns = ["ID", "Date", "Amount"]

        # Display column headers
        for col_index, col_name in enumerate(columns):
            label = Label(self.transaction_frame, text=col_name, bg=self.label_bg_color, fg=self.label_fg_color, font=self.font, borderwidth=2, relief="groove", width=20, anchor="center")
            label.grid(row=0, column=col_index, padx=5, pady=5, sticky='nsew')

        # Fetch all transactions from the database
        self.cursor.execute("SELECT id, date, amount FROM transactions")
        transactions = self.cursor.fetchall()

        # Display transactions
        for row_index, transaction in enumerate(transactions, start=1):
            for col_index, value in enumerate(transaction):
                label = Label(self.transaction_frame, text=value, bg=self.label_bg_color, fg=self.label_fg_color, font=self.font, borderwidth=2, relief="groove", width=20, anchor="center")
                label.grid(row=row_index, column=col_index, padx=5, pady=5, sticky='nsew')

    def search_transactions(self):
        from_date = self.from_date.get_date()
        to_date = self.to_date.get_date()


        for widget in self.transaction_frame.winfo_children():
            widget.destroy()

        columns = ["ID", "Date", "Amount"]
        for col_index, col_name in enumerate(columns):
            label = Label(self.transaction_frame, text=col_name, bg=self.label_bg_color, fg=self.label_fg_color, font=self.font, borderwidth=2, relief="groove", width=20, anchor="center")
            label.grid(row=0, column=col_index, padx=5, pady=5, sticky='nsew')

        query = "SELECT id, date, amount FROM transactions WHERE date BETWEEN ? AND ?"
        self.cursor.execute(query, (from_date, to_date))
        transactions = self.cursor.fetchall()

        for row_index, transaction in enumerate(transactions, start=1):
            for col_index, value in enumerate(transaction):
                label = Label(self.transaction_frame, text=value, bg=self.label_bg_color, fg=self.label_fg_color, font=self.font, borderwidth=2, relief="groove", width=20, anchor="center")
                label.grid(row=row_index, column=col_index, padx=5, pady=5, sticky='nsew')

    



# Running the application
if __name__ == "__main__":
    app = ManagerInterface()
    app.mainloop()
