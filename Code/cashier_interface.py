import tkinter as tk
from tkinter import ttk, messagebox 
from PIL import ImageTk, Image ,ImageOps
from datetime import datetime
import sqlite3
import traceback
from path_utils import get_image_path
from db_utils import get_connection
import os


class DeleteProductDialog(tk.Toplevel):
    def __init__(self, parent, product_names):
        super().__init__(parent)
        self.title("Delete Product")
        self.geometry("300x150")

        self.product_names = product_names

        self.selected_product = tk.StringVar()
        self.selected_product.set(product_names[0])  # Set default selection

        self.label = tk.Label(self, text="Select a product to delete:")
        self.label.pack(pady=5)

        self.product_dropdown = ttk.Combobox(self, textvariable=self.selected_product, values=product_names)
        self.product_dropdown.pack(pady=5)

        self.confirm_button = tk.Button(self, text="Confirm", command=self.confirm_delete)
        self.confirm_button.pack(pady=5)

    def confirm_delete(self):
        selected_product = self.selected_product.get()
        confirmation = messagebox.askokcancel("Confirmation", f"Are you sure you want to delete {selected_product}?")
        if confirmation:
            self.destroy()


class CashierInterface(tk.Tk):
    def __init__(self, account_name, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
            self.title("Cashier Interface")
            self.geometry("1920x1080")  # Set the size of the window

            # Database connection setup
            self.conn = get_connection()
            self.cursor = self.conn.cursor()

            # Create a frame for the main content
            self.main_frame = tk.Frame(self)
            self.main_frame.pack(fill=tk.BOTH, expand=True)

            self.account_name = account_name
            # Create a frame to contain both the circle and label
            self.employee_frame = tk.Frame(self.main_frame)
            self.employee_frame.pack(pady=5, padx=10, anchor=tk.W)  # Anchor to the left side

            # Create and pack the online indicator (circle)
            self.online_indicator = tk.Label(self.employee_frame, text="•", font=("Arial", 20), fg="green")
            self.online_indicator.pack(side=tk.LEFT)

            # Create and pack the employee label
            self.employee_label = tk.Label(self.employee_frame, text=f"Nhân viên: {account_name}", font=("Arial", 12, "bold"))
            self.employee_label.pack(side=tk.LEFT)

            self.logout_button = tk.Button(self.main_frame, text="Đăng xuất", command=self.logout)
            self.logout_button.pack(side=tk.BOTTOM, pady=10)
            
            # Create a frame for the product list
            self.product_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
            self.product_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Create a frame for the invoice
            self.invoice_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
            self.invoice_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Create a search icon and entry at the top of the product frame
            search_frame = tk.Frame(self.product_frame)
            search_frame.pack(fill=tk.X, pady=(10, 0))

            # Add New Product button
            add_product_button = tk.Button(search_frame, text="Add New Product", command=self.add_new_product)
            add_product_button.pack(side=tk.LEFT, padx=(10, 0))

            # Delete Product button
            delete_product_button = tk.Button(search_frame, text="Delete Product", command=self.delete_product_prompt)
            delete_product_button.pack(side=tk.LEFT, padx=(10, 0))

            # Search icon and entry
            self.search_entry = tk.Entry(search_frame, width=30)
            self.search_entry.pack(side=tk.LEFT, padx=(10, 0))
            search_button = tk.Button(search_frame, text="Search", command=self.filter_products)
            search_button.pack(side=tk.LEFT, padx=(5, 10))

            # Category dropdown
            category_label = tk.Label(search_frame, text="Category")
            category_label.pack(side=tk.RIGHT, padx=(0, 5))

            self.category_var = tk.StringVar()
            self.category_dropdown = ttk.Combobox(search_frame, textvariable=self.category_var)
            self.update_category_dropdown()
            self.category_dropdown.current(0)  # Set default selection to 'All'
            self.category_dropdown.pack(side=tk.RIGHT)
            self.category_dropdown.bind("<<ComboboxSelected>>", self.filter_products)

            # Create a label for the product list
            self.product_label = tk.Label(self.product_frame, text="Available Products", font=("Arial", 14, "bold"))
            self.product_label.pack(pady=(10, 0))

            # Create a canvas for the product blocks
            self.canvas = tk.Canvas(self.product_frame)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Create a frame to contain the product blocks inside the canvas
            self.product_grid_frame = tk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.product_grid_frame, anchor="nw")

            # Create a vertical scrollbar for the canvas
            self.scrollbar = tk.Scrollbar(self.product_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            # Bind mouse wheel to canvas
            self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

            # Bind the canvas to the scrollbar
            self.canvas.bind("<Configure>", self.on_canvas_configure)

            # Load products into the product grid
            self.load_products()

            # Create a label for the invoice
            self.invoice_label = tk.Label(self.invoice_frame, text="Invoice", font=("Arial", 14, "bold"))
            self.invoice_label.pack(pady=(10, 0))

            # Create a frame for invoice details
            self.invoice_details_frame = tk.Frame(self.invoice_frame)
            self.invoice_details_frame.pack(fill=tk.BOTH, expand=True)

            # Create a frame for the total and pay button
            self.invoice_summary_frame = tk.Frame(self.invoice_frame)
            self.invoice_summary_frame.pack(fill=tk.X, pady=10)

            # Create a label for the total amount
            self.total_label = tk.Label(self.invoice_summary_frame, text="Total: $0.00", font=("Arial", 12, "bold"))
            self.total_label.pack(side=tk.RIGHT, padx=10)

            # Create a Pay button
            self.pay_button = tk.Button(self.invoice_summary_frame, text="Pay", bg="lightgreen", font=("Arial", 12, "bold"), command=self.make_payment)
            self.pay_button.pack(side=tk.LEFT, padx=10)

            # Create a list to store cart items
            self.cart = []

            # Thêm hàm logout vào sự kiện WM_DELETE_WINDOW
            self.protocol("WM_DELETE_WINDOW", self.on_close)


        except Exception as e:
            print(f"Error initializing CashierInterface: {e}")
            traceback.print_exc()
        
    def load_products(self, category=None):
        """Load products from the database and display them in the product grid"""
        try:
            # Clear existing products in the grid
            for widget in self.product_grid_frame.winfo_children():
                widget.destroy()
            
            # Configure grid columns to expand properly
            for i in range(5):  # Create 5 columns for products
                self.product_grid_frame.columnconfigure(i, weight=1)
        
            # Query database for products with explicit column selection
            if category and category != "All":
                self.cursor.execute("SELECT id, name, price, image_path, details, category, quantity FROM products WHERE category=?", (category,))
            else:
                self.cursor.execute("SELECT id, name, price, image_path, details, category, quantity FROM products") 
                products = self.cursor.fetchall()
            
            # Calculate the number of products per row (use 5 for better space utilization)
            products_per_row = 5
            
            # Display each product in the grid
            for i, product in enumerate(products):
                # Calculate row and column position
                row = i // products_per_row
                col = i % products_per_row
                
                # Create a frame for each product with consistent size
                product_frame = tk.Frame(self.product_grid_frame, width=170, height=260, 
                                         relief=tk.RAISED, borderwidth=1, bg='#f5f5f5')
                product_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
                product_frame.pack_propagate(False)  # Force frame to keep its size
                
                # Product ID and details - with explicit indices
                product_id = product[0]  # id
                name = product[1]        # name
                price = product[2]       # price
                image_path = product[3]  # image_path
                
                # Handle image path and display with consistent size
                try:
                    if isinstance(image_path, (str, bytes)) and image_path:
                        try:
                            # Try direct path first
                            image = Image.open(image_path)
                        except (FileNotFoundError, OSError):
                            # If that fails, try using just the filename from the path
                            filename = os.path.basename(image_path.replace('\\', '/'))
                            image = Image.open(get_image_path(filename))
                    else:
                        # Use a default image if the path is invalid
                        image = Image.open(get_image_path('white_image.png'))
                
                    # Resize and center the image
                    image = ImageOps.contain(image, (120, 120))
                    photo = ImageTk.PhotoImage(image)
                    
                    # Store the photo reference to prevent garbage collection
                    if not hasattr(self, 'photos'):
                        self.photos = []
                    self.photos.append(photo)
                    
                    # Create image container with fixed height
                    img_container = tk.Frame(product_frame, height=120, bg='#f5f5f5')
                    img_container.pack(fill='x', pady=(5, 0))
                    img_container.pack_propagate(False)
                    
                    # Center the image in its container
                    image_label = tk.Label(img_container, image=photo, bg='#f5f5f5')
                    image_label.pack(expand=True)
                    
                except Exception as e:
                    print(f"Error loading image for product {product_id}: {name} - {e}")
                    # Add placeholder if image fails
                    img_container = tk.Frame(product_frame, height=120, bg='#f5f5f5')
                    img_container.pack(fill='x', pady=(5, 0))
                    img_container.pack_propagate(False)
                    
                    placeholder = tk.Label(img_container, text="[No Image]", width=15, height=5, bg='#f5f5f5')
                    placeholder.pack(expand=True)
                
                # FIXED INDENTATION: The following code is now properly indented inside the product loop
                # Product name with fixed height and ellipsis for long names
                name_container = tk.Frame(product_frame, height=30, bg='#f5f5f5')
                name_container.pack(fill='x')
                name_container.pack_propagate(False)
                
                # Limit name length for display
                display_name = name if len(name) < 20 else name[:17] + "..."
                name_label = tk.Label(name_container, text=display_name, wraplength=160, bg='#f5f5f5', font=("Arial", 9, "bold"))
                name_label.pack(pady=2)
                
                # Price with consistent formatting
                price_container = tk.Frame(product_frame, height=20, bg='#f5f5f5')
                price_container.pack(fill='x')
                price_container.pack_propagate(False)
                
                price_label = tk.Label(price_container, text=f"${float(price):.2f}", bg='#f5f5f5', fg='#e74c3c', font=("Arial", 10, "bold"))
                price_label.pack(pady=2)
                
                # Button container with fixed height
                button_container = tk.Frame(product_frame, height=50, bg='#f5f5f5')
                button_container.pack(fill='x', pady=5)
                button_container.pack_propagate(False)
                
                # Add to Cart button
                add_button = tk.Button(button_container, text="Add to Cart", bg='#2ecc71', fg='white',
                                      command=lambda p=product: self.add_to_cart(p))
                add_button.pack(fill='x', pady=2, padx=5)
                
                # Details button
                details_button = tk.Button(button_container, text="Details", bg='#3498db', fg='white',
                                          command=lambda p=product: self.show_details(p))
                details_button.pack(fill='x', pady=2, padx=5)
            
            # Update the canvas scrollregion
            self.product_grid_frame.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
                
        except Exception as e:
            print(f"Error loading products: {e}")
            import traceback
            traceback.print_exc()


    def update_category_dropdown(self):
        try:
            # Fetch existing categories from the database
            self.cursor.execute("SELECT DISTINCT category FROM products")
            categories = [row[0] for row in self.cursor.fetchall()]  # Changed from c.fetchall() to self.cursor.fetchall()
            if 'All' not in categories:
                categories.insert(0, 'All')
            self.category_dropdown['values'] = categories
            # Only set current index if we have values
            if self.category_dropdown['values']:
                self.category_dropdown.current(0)
        except Exception as e:
            print(f"Error updating category dropdown: {e}")
            traceback.print_exc()

    def add_to_cart(self, product):
        try:
            # Ensure price is converted to a float
            product_price = float(product[2])

            # Check if the product is already in the cart
            for item in self.cart:
                if item["name"] == product[1]:
                    item["quantity"] += 1
                    self.update_invoice()
                    return

            # Check if product has quantity field (index 6 in your SELECT query)
            if len(product) > 6 and product[6] is not None:
                quantity = product[6]
            else:
                # Default quantity if not specified
                quantity = 1
                
            # Check if we have enough in stock
            if quantity > 0:
                # Add new product to the cart
                self.cart.append({"name": product[1], "price": product_price, "quantity": 1})
                self.update_invoice()
            else:
                # Show message if out of stock
                messagebox.showwarning("Out of Stock", f"The product '{product[1]}' is out of stock.")

        except Exception as e:
            print(f"Error adding product to cart: {e}")
            traceback.print_exc()



    def update_invoice(self):
        try:
            # Clear the current invoice details
            for widget in self.invoice_details_frame.winfo_children():
                widget.destroy()

            # Display each item in the cart
            total_amount = 0
            for item in self.cart:
                item_frame = tk.Frame(self.invoice_details_frame)
                item_frame.pack(fill=tk.X, pady=2)

                name_label = tk.Label(item_frame, text=item["name"], font=("Arial", 12))
                name_label.pack(side=tk.LEFT, padx=5)

                quantity_label = tk.Label(item_frame, text=f"Qty: {item['quantity']}", font=("Arial", 12))
                quantity_label.pack(side=tk.LEFT, padx=5)

                # Create a Remove button for each item
                remove_button = tk.Button(item_frame, text="Remove", bg="lightcoral", command=lambda i=item: self.remove_from_cart(i))
                remove_button.pack(side=tk.RIGHT, padx=5)

                # Ensure item['price'] is converted to a float for calculation
                item_price = float(item['price'])
                price_label = tk.Label(item_frame, text=f"${item_price * item['quantity']:.2f}", font=("Arial", 12))
                price_label.pack(side=tk.RIGHT, padx=5)

                total_amount += item_price * item['quantity']

            # Update the total amount label
            self.total_label.config(text=f"Total: ${total_amount:.2f}")

        except Exception as e:
            print(f"Error updating invoice: {e}")
            traceback.print_exc()


    def remove_from_cart(self, item):
        # Remove the item from the cart
        self.cart.remove(item)
    
        # Update the invoice after removal
        self.update_invoice()

    def show_details(self, product):
        try:
            messagebox.showinfo("Product Details", f"Product: {product[1]}\nDetails: {product[4] if product[4] else 'No details available'}")
        except Exception as e:
            print(f"Error showing product details: {e}")
            traceback.print_exc()

    def make_payment(self):
        try:
             # Kiểm tra xem giỏ hàng có rỗng không
            if not self.cart:
                messagebox.showwarning("Empty Cart", "Your cart is empty. Please add items to your cart before making payment.")
                return   
            # Kiểm tra số lượng sản phẩm trong giỏ hàng trước khi thanh toán
            for item in self.cart:
                self.cursor.execute("SELECT quantity FROM products WHERE name=?", (item["name"],))
                current_quantity = self.cursor.fetchone()[0]
                if item["quantity"] > current_quantity:
                    messagebox.showwarning("Out of Stock", f"The product '{item['name']}' is out of stock.")
                    return

            # Create a new window for the payment receipt
            receipt_window = tk.Toplevel(self)
            receipt_window.title("Payment Receipt")
            receipt_window.geometry("400x800")


            # Create and pack receipt details
            header_label = tk.Label(receipt_window, text="HDK MILK", font=("Arial", 18, "bold"))
            header_label.pack(pady=5)

            company_label = tk.Label(receipt_window, text="HDK MILK milk distribution company\nTel: 0338819483", font=("Arial", 12))
            company_label.pack(pady=5)

            time_label = tk.Label(receipt_window, text=f"Payment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 12))
            time_label.pack(pady=5)
            
            employee_label = tk.Label(receipt_window, text=f"Cashier: {self.account_name}", font=("Arial", 12))
            employee_label.pack(pady=5)

            shift = self.get_shift()
            shift_label = tk.Label(receipt_window, text=f"Shift: {shift}", font=("Arial", 12))
            shift_label.pack(pady=5)

            separator = tk.Label(receipt_window, text="--------------------------------------------------", font=("Arial", 12))
            separator.pack(pady=5)

            order_header = tk.Label(receipt_window, text="{:<20} {:<10} {:<10}".format("Order", "Quantity", "Amount"), font=("Arial", 12))
            order_header.pack(pady=5)
            

            # Hiển thị từng sản phẩm trong giỏ hàng trên biên nhận
            for item in self.cart:
                item_label = tk.Label(receipt_window, text="{:<20} {:<10} ${:<10.2f}".format(item['name'], item['quantity'], item['price'] * item['quantity']), font=("Arial", 12))
                item_label.pack(pady=2)

            # Lưu giao dịch vào cơ sở dữ liệu
            total_amount = sum(item["price"] * item["quantity"] for item in self.cart)
            total_label = tk.Label(receipt_window, text="{:<20} {:<10} ${:<10.2f}".format("Total", "", total_amount), font=("Arial", 12, "bold"))
            total_label.pack(pady=10)
            self.log_transaction(total_amount) 

            # Update product quantities in the database
            self.update_product_quantities()

            # Clear the cart and update the invoice
            self.cart.clear()
            self.update_invoice()

            # Clear the cart and update the invoice
            self.cart.clear()
            self.update_invoice()

            # Reload products after payment
            self.load_products()

        except Exception as e:
            print(f"Error making payment: {e}")
            traceback.print_exc()

    def update_product_quantities(self):
        try:
            for item in self.cart:
                # Fetch the current quantity of the product
                self.cursor.execute("SELECT quantity FROM products WHERE name=?", (item["name"],))
                current_quantity = self.cursor.fetchone()[0]
                
                 # Calculate the new quantity after sale
                new_quantity = max(current_quantity - item["quantity"], 0)  # Đảm bảo số lượng không âm

                # Update the product quantity in the database
                self.cursor.execute("UPDATE products SET quantity=? WHERE name=?", (new_quantity, item["name"]))
                self.conn.commit()
                
        except Exception as e:
            print(f"Error updating product quantities: {e}")
            traceback


    def log_transaction(self, amount):
        try:
            # Lấy ngày hiện tại
            transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Thêm dữ liệu giao dịch vào bảng transactions
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (date, amount) VALUES (?, ?)
            ''', (transaction_date, amount))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging transaction: {e}")

    def get_shift(self):
        try:
            current_hour = datetime.now().hour
            if 6.30 <= current_hour < 12:
                return "Morning"
            elif 12 <= current_hour < 18:
                return "Afternoon"
            elif 18 <= current_hour < 23:
                return "Evening"
            else:
                return "Night"
        except Exception as e:
            print(f"Error getting shift: {e}")
            traceback.print_exc()

    def add_new_product(self):
        try:
            add_product_window = tk.Toplevel(self)
            add_product_window.title("Add New Product")
            add_product_window.geometry("400x600")

            name_label = tk.Label(add_product_window, text="Product Name:")
            name_label.pack(pady=5)
            name_entry = tk.Entry(add_product_window)
            name_entry.pack(pady=5)

            category_label = tk.Label(add_product_window, text="Category:")
            category_label.pack(pady=5)
            category_entry = tk.Entry(add_product_window)
            category_entry.pack(pady=5)

            price_label = tk.Label(add_product_window, text="Price:")
            price_label.pack(pady=5)
            price_entry = tk.Entry(add_product_window)
            price_entry.pack(pady=5)

            image_path_label = tk.Label(add_product_window, text="Image Path:")
            image_path_label.pack(pady=5)
            image_path_entry = tk.Entry(add_product_window)
            image_path_entry.pack(pady=5)

            details_label = tk.Label(add_product_window, text="Details:")
            details_label.pack(pady=5)
            details_text = tk.Text(add_product_window, height=5)
            details_text.pack(pady=5)

            def save_product():
                try:
                    name = name_entry.get().strip()
                    category = category_entry.get().strip()
                    price = price_entry.get().strip()
                    image_path = image_path_entry.get().strip()
                    details = details_text.get("1.0", tk.END).strip()

                    if not name or not category or not price:
                        messagebox.showerror("Input Error", "Product name, category, and price are required.")
                        return

                    price = float(price)

                    if not image_path:
                        # Create a white image if no image path is provided
                        white_image = Image.new("RGB", (135, 120), (255, 255, 255))
                        white_image_path = "white_image.png"
                        white_image.save(white_image_path)
                        image_path = white_image_path

                    self.cursor.execute("INSERT INTO products (name, category, price, image_path, details) VALUES (?, ?, ?, ?, ?)",
                  (name, category, price, image_path, details))
                    self.conn.commit()

                    # Check if the new category needs to be added to the dropdown
                    self.update_category_dropdown()

                    add_product_window.destroy()
                    self.load_products()  # Refresh the product grid after adding new product

                except ValueError:
                    messagebox.showerror("Input Error", "Price must be a valid number.")
                except Exception as e:
                    print(f"Error saving new product: {e}")
                    traceback.print_exc()

            save_button = tk.Button(add_product_window, text="Save", command=save_product)
            save_button.pack(pady=20)

        except Exception as e:
            print(f"Error adding new product: {e}")
            traceback.print_exc()


    def filter_products(self, event=None):
        try:
            # Reload products based on search and category filters
            self.load_products()
        except Exception as e:
            print(f"Error filtering products: {e}")
            traceback.print_exc()

    def delete_product_prompt(self):
        """Create a dialog to select and delete a product"""
        try:
            # Get all products from the database
            self.cursor.execute("SELECT id, name FROM products")
            products = self.cursor.fetchall()
            
            if not products:
                messagebox.showinfo("No Products", "There are no products to delete.")
                return
                
            # Create a dialog to select which product to delete
            product_names = [product[1] for product in products]
            product_ids = [product[0] for product in products]
            
            # Create dialog window
            delete_dialog = tk.Toplevel(self)
            delete_dialog.title("Delete Product")
            delete_dialog.geometry("300x250")
            delete_dialog.resizable(False, False)
            
            # Create listbox with products
            tk.Label(delete_dialog, text="Select a product to delete:", font=("Arial", 10, "bold")).pack(pady=5)
            product_listbox = tk.Listbox(delete_dialog, width=40, height=10)
            product_listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
            
            # Add scrollbar
            scrollbar = tk.Scrollbar(product_listbox)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            product_listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=product_listbox.yview)
            
            # Add products to listbox
            for name in product_names:
                product_listbox.insert(tk.END, name)
            
            def confirm_delete():
                if not product_listbox.curselection():
                    messagebox.showwarning("No Selection", "Please select a product to delete")
                    return
                    
                selected_index = product_listbox.curselection()[0]
                selected_product_id = product_ids[selected_index]
                selected_product_name = product_names[selected_index]
                
                # Confirm deletion
                confirm = messagebox.askyesno("Confirm Deletion", 
                                              f"Are you sure you want to delete {selected_product_name}?")
                
                if confirm:
                    self.cursor.execute("DELETE FROM Products WHERE id = ?", (selected_product_id,))
                    self.conn.commit()
                    
                    messagebox.showinfo("Success", "Product deleted successfully")
                    delete_dialog.destroy()
                    
                    # Refresh the product list and category dropdown
                    self.load_products()
                    self.update_category_dropdown()
            
            # Add buttons frame
            button_frame = tk.Frame(delete_dialog)
            button_frame.pack(pady=10, fill=tk.X)
            
            # Add delete button
            tk.Button(button_frame, text="Delete", command=confirm_delete, 
                      bg="#ff6b6b", fg="white", width=10).pack(side=tk.LEFT, padx=20)
            
            # Add cancel button
            tk.Button(button_frame, text="Cancel", command=delete_dialog.destroy, 
                      width=10).pack(side=tk.RIGHT, padx=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error preparing product deletion: {e}")
            import traceback
            traceback.print_exc()

    def delete_product(self, product_id):
        try:
            conn = sqlite3.connect('supermarket.db')
            c = conn.cursor()

            # Execute the DELETE statement
            c.execute("DELETE FROM Products WHERE id=?", (product_id,))

            # Commit the transaction
            conn.commit()
        
        except sqlite3.Error as e:
            print("Error deleting product:", e)

        finally:
            if conn:
                conn.close()

    def filter_products(self, event=None):
        try:
            # Reload products based on search and category filters
            self.load_products()
        except Exception as e:
            print(f"Error filtering products: {e}")
            traceback.print_exc()

    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def logout(self):
        try:
            # Lấy thời gian đăng nhập cuối cùng từ cơ sở dữ liệu
            query = "SELECT login_time FROM cashier_activity WHERE cashier_username = ? AND logout_time IS NULL ORDER BY id DESC LIMIT 1"
            self.cursor.execute(query, (self.account_name,))
            last_login_time = self.cursor.fetchone()[0]

            # Lấy thời gian đăng xuất hiện tại
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Tính toán active_hours từ thời gian đăng nhập và đăng xuất
            login_datetime = datetime.strptime(last_login_time, "%Y-%m-%d %H:%M:%S")
            logout_datetime = datetime.strptime(logout_time, "%Y-%m-%d %H:%M:%S")
            duration_minutes = (logout_datetime - login_datetime).total_seconds() / 60
            active_hours = f"{int(duration_minutes // 60):02}:{int(duration_minutes % 60):02}"

            # Cập nhật thời gian đăng xuất và active_hours vào cơ sở dữ liệu
            update_query = "UPDATE cashier_activity SET logout_time = ?, active_hours = ? WHERE cashier_username = ? AND logout_time IS NULL"
            self.cursor.execute(update_query, (logout_time, active_hours, self.account_name))
            self.conn.commit()

            # Đóng cửa sổ hiện tại của giao diện thu ngân
            self.destroy()
            
            # Mở lại giao diện đăng nhập từ Supermarket.py
            from SuperMaket_Interface import LoginScreen
            LoginScreen().mainloop()

        except Exception as e:
            print(f"Error logging out: {e}")
            traceback.print_exc()
        finally:
            # Đóng chương trình
            self.destroy()

    def on_close(self):
        try:
            # Lấy thời gian đăng nhập cuối cùng từ cơ sở dữ liệu
            query = "SELECT login_time FROM cashier_activity WHERE cashier_username = ? AND logout_time IS NULL ORDER BY id DESC LIMIT 1"
            self.cursor.execute(query, (self.account_name,))
            last_login_time = self.cursor.fetchone()[0]

            # Lấy thời gian đăng xuất hiện tại
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Tính toán active_hours từ thời gian đăng nhập và đăng xuất
            login_datetime = datetime.strptime(last_login_time, "%Y-%m-%d %H:%M:%S")
            logout_datetime = datetime.strptime(logout_time, "%Y-%m-%d %H:%M:%S")
            duration_minutes = (logout_datetime - login_datetime).total_seconds() / 60
            active_hours = f"{int(duration_minutes // 60):02}:{int(duration_minutes % 60):02}"

            # Cập nhật thời gian đăng xuất và active_hours vào cơ sở dữ liệu
            update_query = "UPDATE cashier_activity SET logout_time = ?, active_hours = ? WHERE cashier_username = ? AND logout_time IS NULL"
            self.cursor.execute(update_query, (logout_time, active_hours, self.account_name))
            self.conn.commit()

            # Đóng cửa sổ hiện tại của giao diện thu ngân
            self.destroy()
            
            # Mở lại giao diện đăng nhập từ SuperMaket_Interface.py
            from SuperMaket_Interface import LoginScreen
            LoginScreen().mainloop()

        except Exception as e:
            print(f"Error logging out: {e}")
            traceback.print_exc()
        finally:
            # Đóng chương trình
            self.destroy()


if __name__ == "__main__":
    try:
        app = CashierInterface()
        app.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


