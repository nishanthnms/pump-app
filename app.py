import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox

from hupper import start_reloader

if __name__ == "__main__":
    start_reloader('new.__main__')


# Function to create the PostgreSQL database and tables
def create_db():
    try:
        conn = psycopg2.connect(
            dbname="pump_stock_managements",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY NOT NULL,
                password TEXT NOT NULL,
                email VARCHAR(255) UNIQUE,
                user_type TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create product table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product (
                id SERIAL PRIMARY KEY,
                product_name TEXT NOT NULL,
                product_code VARCHAR(250) UNIQUE,
                unit_price NUMERIC(10, 2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert initial data
        cursor.execute(
            "INSERT INTO users (username, password, email, user_type) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
            ('admin', 'admin', 'admin@gmail.com', 'manager')
        )

        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error creating database: {e}")

# Function to handle login
def login():
    username = entry_username.get()
    password = entry_password.get()

    try:
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            error_label.config(text="")
            show_dashboard()  # Show the dashboard after login
        else:
            error_label.config(text="Invalid username or password", fg="red")

        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")


# Function to show the dashboard in the same window
def show_dashboard():
    global content_frame

    root.title("Pump Management - Dashboard")

    # Clear the current content (login form or previous frame)
    for widget in root.winfo_children():
        widget.destroy()

    # Create a frame for the dashboard
    content_frame = tk.Frame(root, bg="#ecf0f1")
    content_frame.pack(fill="both", expand=True)

    # Create the menu bar for the dashboard
    menu_bar = tk.Menu(root)

    # Dashboard menu
    menu_bar.add_command(label="Home", command=lambda: show_dashboard())

    # Stock Management menu
    stock_menu = tk.Menu(menu_bar, tearoff=0)
    stock_menu.add_command(label="Add New Product", command=open_new_product_input)
    stock_menu.add_command(label="View Stock", command=open_view_stock)
    # stock_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="Stock Management", menu=stock_menu)

    # Report menu
    report_menu = tk.Menu(menu_bar, tearoff=0)
    report_menu.add_command(label="Show Greeting", command=display_greeting)
    menu_bar.add_cascade(label="Report", menu=report_menu)

    root.config(menu=menu_bar)

    # Display the dashboard content
    open_dashboard()

# Function to display the dashboard content in the current frame
def open_dashboard():
    global content_frame
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )

        # Clear previous content
        for widget in content_frame.winfo_children():
            widget.destroy()

        # Create a frame for the cards
        card_frame = tk.Frame(content_frame, bg="#ecf0f1")
        card_frame.pack(pady=20)

        # Fetch stock data
        cursor = conn.cursor()
        cursor.execute("SELECT product_name, product_code, stock FROM product WHERE is_active=TRUE")
        products = cursor.fetchall()

        # Loop through products and create cards
        for i, product in enumerate(products):
            product_name, product_code, stock = product

            # Create a frame for each product card
            card = tk.Frame(card_frame, width=200, height=150, bd=5, relief="solid", bg="#ffffff")
            card.grid(row=i // 3, column=i % 3, padx=15, pady=15)
            card.pack_propagate(False)  # Prevent auto-resizing

            # Add product name as card title
            title_label = tk.Label(card, text=product_name, font=("Helvetica", 14, "bold"), bg="#ffffff")
            title_label.pack(pady=10)

            # Format stock value
            if product_name.lower() in ["petrol", "diesel"] or product_code.startswith(("PTRL", "DESL")):
                stock_text = f"{stock} Liters"
            else:
                stock_text = f"{stock} Units"

            # Display stock value
            stock_label = tk.Label(card, text=stock_text, font=("Helvetica", 12), bg="#ffffff")
            stock_label.pack()

        # Close database connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Unable to fetch dashboard data: {e}")
# Function to open new product input form
def open_new_product_input():
    global content_frame

    # Destroy any existing content frame
    if content_frame:
        content_frame.destroy()

    content_frame = tk.Frame(root, bg="#f4f6f7")  # Set background color
    content_frame.pack(fill="both", expand=True)

    # Add a title label for "Create New Product"
    title_label = tk.Label(content_frame, text="Enter New Product Details", font=("Helvetica", 18, "bold"), bg="#f4f6f7", fg="#2c3e50")
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Create entry fields for product name, code, price, and stock
    def create_labeled_entry(label_text, row):
        label = tk.Label(content_frame, text=label_text, font=("Helvetica", 12), bg="#f4f6f7", fg="#34495e")
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        
        # Create entry field with fixed width
        entry = tk.Entry(content_frame, font=("Helvetica", 12), bg="#ecf0f1", fg="#2c3e50", bd=2, relief="solid", 
                        insertbackground="black", width=50)
        entry.grid(row=row, column=1, padx=10, pady=10, sticky="w")
        
        return entry

    name_entry = create_labeled_entry("Product Name:", 1)
    code_entry = create_labeled_entry("Product Code:", 2)
    price_entry = create_labeled_entry("Unit Price:", 3)
    stock_entry = create_labeled_entry("Stock Quantity:", 4)

    # Add a separator between fields and buttons
    separator = ttk.Separator(content_frame, orient="horizontal")
    separator.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

    # Submit Button to save new product details
    def save_product():
        product_name = name_entry.get()
        product_code = code_entry.get()
        unit_price = price_entry.get()
        stock = stock_entry.get()

        # Validate inputs
        if not product_name or not product_code or not unit_price or not stock:
            messagebox.showerror("Input Error", "Please fill all fields")
            return

        try:
            # Connect to the database and insert product
            conn = psycopg2.connect(
                dbname="pump_stock_management",
                user="local_user",
                password="123",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO product (product_name, product_code, unit_price, stock)
                              VALUES (%s, %s, %s, %s)''',
                           (product_name, product_code, unit_price, stock))
            
            # Commit the transaction and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            # Show success message
            messagebox.showinfo("Success", "Product added successfully!")

            # Redirect to the dashboard
            show_dashboard()

        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving product: {e}")

    # Save Button
    submit_button = tk.Button(content_frame, text="Submit", font=("Helvetica", 12, "bold"), bg="#2ecc71", fg="white", 
                              activebackground="#27ae60", relief="flat", command=save_product)
    submit_button.grid(row=6, column=1, padx=10, pady=20, sticky="ew")

    # Back Button placed in the same row as Submit
    def go_back():
        show_dashboard()

    back_button = tk.Button(content_frame, text="Back", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", 
                            activebackground="#2980b9", relief="flat", command=go_back)
    back_button.grid(row=6, column=0, padx=10, pady=20, sticky="ew")

    # Ensure proper column weight to stretch the entry fields and buttons
    content_frame.grid_columnconfigure(1, weight=1)
    
def open_edit_product_page(product_id):
    """
    Navigate to a separate page to edit product details.
    """
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    open_edit_product_form(product_id)


def open_update_stock_page(product_id):
    """
    Navigate to a separate page to update stock.
    """
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    update_stock(product_id)


def open_view_stock():
    """
    Display product inventory listing with Edit and Update options.
    """
    # Clear the existing widgets from the root window
    for widget in root.winfo_children():
        widget.destroy()

    try:
        # Connect to the database and fetch product details
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, product_name, product_code, unit_price, stock FROM product WHERE is_active=TRUE")
        products = cursor.fetchall()

        # Add a title label
        title_label = tk.Label(
            root,
            text="Product Inventory",
            font=("Helvetica", 20, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=10
        )
        title_label.pack(fill="x")

        # Create a header for the product list
        header_frame = tk.Frame(root, bg="#34495e", padx=10, pady=5)
        header_frame.pack(fill="x", padx=10)

        headers = ["Product Name", "Product Code", "Unit Price", "Stock", "Edit", "Update"]
        column_widths = [20, 20, 15, 10, 10, 10]

        for i, header in enumerate(headers):
            tk.Label(
                header_frame,
                text=header,
                font=("Helvetica", 12, "bold"),
                bg="#34495e",
                fg="#ecf0f1",
                width=column_widths[i],
                anchor="w"
            ).grid(row=0, column=i, padx=5)

        # Create rows for each product
        for index, product in enumerate(products):
            product_id, product_name, product_code, unit_price, stock = product

            # Alternate row colors
            bg_color = "#ecf0f1" if index % 2 == 0 else "#bdc3c7"

            row_frame = tk.Frame(root, bg=bg_color, padx=10, pady=5)
            row_frame.pack(fill="x", padx=10)

            # Add product details
            tk.Label(row_frame, text=product_name, font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=20, anchor="w").grid(row=0, column=0, padx=5)
            tk.Label(row_frame, text=product_code, font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=20, anchor="w").grid(row=0, column=1, padx=5)
            tk.Label(row_frame, text=f"{unit_price:.2f}", font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=15, anchor="w").grid(row=0, column=2, padx=5)
            tk.Label(row_frame, text=str(stock), font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=10, anchor="w").grid(row=0, column=3, padx=5)

            # Add Edit and Update buttons
            edit_button = tk.Button(
                row_frame,
                text="Edit",
                font=("Helvetica", 10, "bold"),
                bg="#3498db",
                fg="white",
                width=10,
                command=lambda pid=product_id: open_edit_product_page(pid)  # Navigate to Edit page
            )
            edit_button.grid(row=0, column=4, padx=5)

            update_button = tk.Button(
                row_frame,
                text="Update",
                font=("Helvetica", 10, "bold"),
                bg="#27ae60",
                fg="white",
                width=10,
                command=lambda pid=product_id: open_update_stock_page(pid)  # Navigate to Update Stock page
            )
            update_button.grid(row=0, column=5, padx=5)

        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", f"Error fetching product data: {e}")



def open_edit_product_form(product_id):
    global content_frame

    if content_frame:
        content_frame.destroy()

    content_frame = tk.Frame(root, bg="#f4f6f7")  # Set background color
    content_frame.pack(fill="both", expand=True)

    # Fetch product details
    conn = psycopg2.connect(
        dbname="pump_stock_management",
        user="local_user",
        password="123",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, product_code, unit_price, stock FROM product WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        messagebox.showerror("Error", "Product not found!")
        return

    product_name, product_code, unit_price, stock = product

    # Add a title label for Edit Product
    title_label = tk.Label(content_frame, text="Edit Product Details", font=("Helvetica", 18, "bold"), bg="#f4f6f7", fg="#2c3e50")
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    def create_labeled_entry(label_text, initial_value, row):
        label = tk.Label(content_frame, text=label_text, font=("Helvetica", 12), bg="#f4f6f7", fg="#34495e")
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        
        # Create entry field with fixed width (100px)
        entry = tk.Entry(content_frame, font=("Helvetica", 12), bg="#ecf0f1", fg="#2c3e50", bd=2, relief="solid", 
                        insertbackground="black", width=50)  # Set width to 100px (approx 15 characters)
        entry.insert(0, initial_value)
        entry.grid(row=row, column=1, padx=10, pady=10, sticky="w")  # Set sticky="w" to avoid stretching
        
        return entry

    name_entry = create_labeled_entry("Product Name:", product_name, 1)
    code_entry = create_labeled_entry("Product Code:", product_code, 2)
    price_entry = create_labeled_entry("Unit Price:", unit_price, 3)
    stock_entry = create_labeled_entry("Stock Quantity:", stock, 4)


    # Add a separator between fields and buttons
    separator = ttk.Separator(content_frame, orient="horizontal")
    separator.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

    # Save Changes button
    def save_changes():
        new_name = name_entry.get()
        new_code = code_entry.get()
        new_price = price_entry.get()
        new_stock = stock_entry.get()

        if not new_name or not new_code or not new_price or not new_stock:
            messagebox.showerror("Input Error", "Please fill all fields")
            return

        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute(''' 
            UPDATE product
            SET product_name = %s, product_code = %s, unit_price = %s, stock = %s
            WHERE id = %s
        ''', (new_name, new_code, new_price, new_stock, product_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Product updated successfully!")
        open_view_stock()

    save_button = tk.Button(content_frame, text="Save Changes", font=("Helvetica", 12, "bold"), bg="#2ecc71", fg="white", 
                            activebackground="#27ae60", relief="flat", command=save_changes)
    save_button.grid(row=6, column=1, padx=10, pady=20, sticky="ew")

    # Back button placed in the same row as Save Changes
    def go_back():
        open_view_stock()

    back_button = tk.Button(content_frame, text="Back", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", 
                            activebackground="#2980b9", relief="flat", command=go_back)
    back_button.grid(row=6, column=0, padx=10, pady=20, sticky="ew")

    # Ensure proper column weight to stretch the entry fields and buttons
    content_frame.grid_columnconfigure(1, weight=1)

    
# Update Stock Form
def update_stock(product_id):
    global content_frame

    if content_frame:
        content_frame.destroy()

    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True)

    # Fetch product details (name, code, and current stock) from the database
    try:
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute('''
            SELECT product_name, product_code, stock 
            FROM product 
            WHERE id = %s
        ''', (product_id,))
        product_details = cursor.fetchone()

        if not product_details:
            messagebox.showerror("Error", "Product not found.")
            return

        product_name, product_code, current_stock = product_details
        cursor.close()
        conn.close()

        # Add title and product details to the form
        tk.Label(content_frame, text="Update Stock Quantity", font=("Helvetica", 16, "bold"), bg="#ecf0f1").pack(pady=10)
        
        # Display product details
        tk.Label(content_frame, text=f"Product Name: {product_name}").pack(pady=5)
        tk.Label(content_frame, text=f"Product Code: {product_code}").pack(pady=5)
        tk.Label(content_frame, text=f"Current Stock: {current_stock}").pack(pady=5)
        
        # Add entry to update stock quantity
        tk.Label(content_frame, text="New Stock Quantity:").pack(pady=5)
        stock_entry = tk.Entry(content_frame)
        stock_entry.pack(pady=5)

        # Save the updated stock quantity
        def save_stock():
            new_stock = stock_entry.get()
            if not new_stock or not new_stock.isdigit():
                messagebox.showerror("Input Error", "Please enter a valid stock quantity")
                return

            conn = psycopg2.connect(
                dbname="pump_stock_management",
                user="local_user",
                password="123",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE product
                SET stock = %s
                WHERE id = %s
            ''', (new_stock, product_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Stock updated successfully!")
            open_view_stock()

        tk.Button(content_frame, text="Save", font=("Helvetica", 12), bg="#3498db", fg="white", command=save_stock).pack(pady=20)

    except Exception as e:
        messagebox.showerror("Database Error", f"Error fetching product data: {e}")



# Function to display a greeting
def display_greeting():
    global content_frame

    if content_frame:
        content_frame.destroy()

    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True)

    tk.Label(content_frame, text="Hi, how are you?", font=("Helvetica", 16)).pack(pady=20)


# Create root window
root = tk.Tk()
root.title("Login")
root.geometry("700x600")

# Create login form
frame = tk.Frame(root, bg="#ecf0f1", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

title_label = tk.Label(frame, text="Login", font=("Helvetica", 24, "bold"), bg="#ecf0f1", fg="#34495e")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

username_label = tk.Label(frame, text="Username:", font=("Helvetica", 12), bg="#ecf0f1", fg="#34495e")
username_label.grid(row=1, column=0, pady=10, sticky="e")

entry_username = tk.Entry(frame, font=("Helvetica", 12), width=20, bd=2, relief="solid", fg="#34495e")
entry_username.grid(row=1, column=1, pady=10)

password_label = tk.Label(frame, text="Password:", font=("Helvetica", 12), bg="#ecf0f1", fg="#34495e")
password_label.grid(row=2, column=0, pady=10, sticky="e")

entry_password = tk.Entry(frame, font=("Helvetica", 12), width=20, bd=2, relief="solid", fg="#34495e", show="*")
entry_password.grid(row=2, column=1, pady=10)

error_label = tk.Label(frame, text="", font=("Helvetica", 12), fg="red", bg="#ecf0f1")
error_label.grid(row=3, column=0, columnspan=2, pady=5)

login_button = tk.Button(frame, text="Login", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", width=15, height=2, command=login)
login_button.grid(row=4, column=0, columnspan=2, pady=20)

# Bind the Enter key to the login function
root.bind('<Return>', lambda event: login())

root.mainloop()
