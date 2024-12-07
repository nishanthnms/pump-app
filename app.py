import psycopg2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# IP = 103.175.88.44
# username = nishanthnms1994na
# password = vZ8Y0QMH65sytlfD
# id - mongosh "mongodb+srv://pumpcluster.ubst4.mongodb.net/" --apiVersion 1 --username nishanthnms1994na


# Function to create the PostgreSQL database and tables (make sure your PostgreSQL server is running)
def create_db():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname="pump_stock_management",  # Replace with your DB name
            user="local_user",       # Replace with your PostgreSQL username
            password="123",  # Replace with your PostgreSQL password
            host="localhost",       # Assuming PostgreSQL is running locally
            port="5432"             # Default PostgreSQL port
        )
        cursor = conn.cursor()

        # Create a table for user authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY NOT NULL,
                password TEXT  NOT NULL,
                email VARCHAR(255) UNIQUE,
                user_type TEXT,       
                is_active BOOLEAN DEFAULT TRUE,       
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     
            )
        ''')

        # Create a table for stock data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product(
                id SERIAL PRIMARY KEY,
                product_name TEXT NOT NULL,
                product_code VARCHAR(250) UNIQUE, 
                unit_price NUMERIC(10, 2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,   
                is_active BOOLEAN DEFAULT TRUE,        
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    
            )
        ''')

        # Create a table for bank data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank_details(
                id SERIAL PRIMARY KEY,
                bank_name TEXT NOT NULL,            
                account_number VARCHAR(20) UNIQUE,  
                ifsc_code VARCHAR(11) NOT NULL,     
                branch TEXT NOT NULL,   
                is_active BOOLEAN DEFAULT TRUE,      
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert initial data into users table if not exists
        cursor.execute("INSERT INTO users (username, password, email, user_type) VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO NOTHING", ('admin', 'admin', 'admin@gmail.com', 'manager'))
        cursor.execute("INSERT INTO product (product_name, product_code, unit_price, stock) VALUES (%s, %s, %s, %s) ON CONFLICT (product_code) DO NOTHING", ('Petrol', 'PTRL001', '104', '1400'))
        cursor.execute("INSERT INTO product (product_name, product_code, unit_price, stock) VALUES (%s, %s, %s, %s) ON CONFLICT (product_code) DO NOTHING", ('Deisel', 'DESL001', '95', '1000'))
        cursor.execute("INSERT INTO product (product_name, product_code, unit_price, stock) VALUES (%s, %s, %s, %s) ON CONFLICT (product_code) DO NOTHING", ('Oil', 'OIL001', '499', '50'))


        # Commit changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        import traceback;traceback.print_exc()
        messagebox.showerror("Database Error", f"Error creating database: {e}")

# Function to connect to the PostgreSQL database
def db_connect():
    return psycopg2.connect(
        dbname="pump_stock_management",
        user="local_user",       
        password="123",         
        host="localhost",       
        port="5432"
    )



# Function to handle login button click
def login():
    username = entry_username.get()
    password = entry_password.get()

    # Validate user credentials using the database
    try:
        # Connect to PostgreSQL database
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
            # If credentials are correct, hide login window and open dashboard
            error_label.config(text="")
            open_dashboard(conn)
            root.withdraw()  # Hide the login window
        else:
            # If credentials are incorrect, display error message on the login screen
            error_label.config(text="Invalid username or password", fg="red")
        
        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")

# Function to open the dashboard window
def open_dashboard(conn):
    global dashboard 
    try:
        # Create a new Toplevel window (the dashboard)
        dashboard = tk.Toplevel(root)
        dashboard.title("Dashboard")
        dashboard.geometry("800x500")  # Window size
        dashboard.config(bg="#ecf0f1")  # Dashboard background color

        # Create a frame for the cards (total petrol and diesel)
        card_frame = tk.Frame(dashboard, bg="#ecf0f1")
        card_frame.pack(pady=20)

        # Fetch the stock data (petrol, diesel, and total stock) from the database
        cursor = conn.cursor()
        # Fetch all products (you can add more filters as needed)
        cursor.execute("SELECT product_name, product_code, stock FROM product WHERE is_active=TRUE")
        products = cursor.fetchall()

        # Create a frame for the cards (total petrol, diesel, etc.)
        card_frame = tk.Frame(dashboard, bg="#ecf0f1")
        card_frame.pack(pady=20)

        # Loop through each product and create a card
        for i, product in enumerate(products):
            product_name, product_code, stock = product

            # Create a frame for each product card
            card = tk.Frame(card_frame, width=200, height=150, bd=5, relief="solid", padx=10, pady=10)

            # Add product name as the card's title
            card_label = tk.Label(card, text=product_name, font=("Helvetica", 14, "bold"))
            card_label.pack(pady=10)

            # Format the stock value as "Liters" for petrol and diesel or general units for others
            if product_name.lower() in ["petrol", "diesel"] or product_code.startswith("PTRL") or product_code.startswith("DESL"):
                stock_label = f"{stock} Liters"
            else:
                stock_label = f"{stock} Units"

            # Display the stock value on the card
            stock_value = tk.Label(card, text=stock_label, font=("Helvetica", 16))
            stock_value.pack()

            # Position the card in a grid
            row = i // 3  # Create 3 columns of cards
            col = i % 3
            card.grid(row=row, column=col, padx=20)

            # Pack the card
            card.pack_propagate(False)  # Prevent the card from resizing to fit its content

        # Close the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")

    # Create menu bar for Stock Management and Report
    menubar = tk.Menu(dashboard)

    # Stock Management Menu
    stock_menu = tk.Menu(menubar, tearoff=0)
    stock_menu.add_command(label="View Stocks", command=open_view_products)
    stock_menu.add_command(label="Add New Product", command=open_add_product_form)
    stock_menu.add_separator()
    # stock_menu.add_command(label="Exit", command=dashboard.quit)
    menubar.add_cascade(label="Stock Management", menu=stock_menu)

    # Report Menu
    report_menu = tk.Menu(menubar, tearoff=0)
    report_menu.add_command(label="View Report")
    report_menu.add_command(label="Generate Report")
    menubar.add_cascade(label="Report", menu=report_menu)

    # Logout Menu
    report_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_command(label="Logout", command=dashboard.quit)

    # Configuring the menubar
    dashboard.config(menu=menubar)


# Function to create the Add Product form
def open_add_product_form():
    global add_product_window, entry_product_name, entry_product_code, entry_unit_price, entry_stock

    # Hide the dashboard window when Add Product form is opened
    dashboard.withdraw()

    # Create a new window for adding product
    add_product_window = tk.Toplevel(root)
    add_product_window.title("Add Product")
    add_product_window.geometry("400x400")
    add_product_window.config(bg="#ecf0f1")

    # Labels and Entry fields for product details
    label_product_name = tk.Label(add_product_window, text="Product Name:", bg="#ecf0f1", font=("Helvetica", 12))
    label_product_name.grid(row=0, column=0, pady=10, sticky="w")
    entry_product_name = tk.Entry(add_product_window, font=("Helvetica", 12), width=25)
    entry_product_name.grid(row=0, column=1, pady=10)

    label_product_code = tk.Label(add_product_window, text="Product Code:", bg="#ecf0f1", font=("Helvetica", 12))
    label_product_code.grid(row=1, column=0, pady=10, sticky="w")
    entry_product_code = tk.Entry(add_product_window, font=("Helvetica", 12), width=25)
    entry_product_code.grid(row=1, column=1, pady=10)

    label_unit_price = tk.Label(add_product_window, text="Unit Price:", bg="#ecf0f1", font=("Helvetica", 12))
    label_unit_price.grid(row=2, column=0, pady=10, sticky="w")
    entry_unit_price = tk.Entry(add_product_window, font=("Helvetica", 12), width=25)
    entry_unit_price.grid(row=2, column=1, pady=10)

    label_stock = tk.Label(add_product_window, text="Stock:", bg="#ecf0f1", font=("Helvetica", 12))
    label_stock.grid(row=3, column=0, pady=10, sticky="w")
    entry_stock = tk.Entry(add_product_window, font=("Helvetica", 12), width=25)
    entry_stock.grid(row=3, column=1, pady=10)

    # Save button to save the product details
    save_button = tk.Button(add_product_window, text="Save Product", font=("Helvetica", 12, "bold"), 
                            bg="#3498db", fg="white", command=save_product)
    save_button.grid(row=4, column=0, columnspan=2, pady=20)


# Function to handle saving the product details into the database
def save_product():
    product_name = entry_product_name.get()
    product_code = entry_product_code.get()
    unit_price = entry_unit_price.get()
    stock = entry_stock.get()

    # Validate inputs
    if not product_name or not product_code or not unit_price or not stock:
        messagebox.showerror("Input Error", "Please fill all fields")
        return

    try:
        # Connect to the database and insert product
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO product (product_name, product_code, unit_price, stock)
                          VALUES (%s, %s, %s, %s)''', 
                       (product_name, product_code, unit_price, stock))
        
        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        # Show success message and redirect to View Products
        messagebox.showinfo("Success", "Product added successfully!")
        add_product_window.destroy()  # Close the Add Product window
        open_view_products()  # Open the View Products window

    except Exception as e:
        messagebox.showerror("Database Error", f"Error saving product: {e}")

# Function to display all products in the View Products section
def open_view_products():
    global view_window  # Declare view_window as global

    # Hide the dashboard window when Add Product form is opened
    dashboard.withdraw()

    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, product_name, product_code, unit_price, stock FROM product WHERE is_active=TRUE")
        products = cursor.fetchall()

        # Create a new Toplevel window for the View Products section
        view_window = tk.Toplevel(root)
        view_window.title("View Products")
        view_window.geometry("800x500")
        view_window.config(bg="#ecf0f1")

        # Create a treeview to display products
        from tkinter import ttk
        global tree

        tree = ttk.Treeview(view_window, columns=("Product Name", "Product Code", "Unit Price", "Stock", "Actions"), show="headings")
        tree.heading("#1", text="Product Name")
        tree.heading("#2", text="Product Code")
        tree.heading("#3", text="Unit Price")
        tree.heading("#4", text="Stock")
        tree.heading("#5", text="Actions")
        
        # Set column widths
        tree.column("#1", width=150)
        tree.column("#2", width=100)
        tree.column("#3", width=100)
        tree.column("#4", width=100)
        tree.column("#5", width=150)

        # Add a scrollbar to the treeview
        scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Function to handle actions (Edit and Update Stock)
        def handle_action(product_id, action_type):
            if action_type == "edit":
                open_edit_product_form(product_id)
            elif action_type == "update_stock":
                update_stock(product_id)

        # Insert rows into the Treeview and create action buttons in the Actions column
        for product in products:
            product_id, product_name, product_code, unit_price, stock = product
            tree.insert("", "end", values=(product_name, product_code, unit_price, stock, f"Edit | Update Stock"))

        # Bind a single event to handle clicks
        def on_treeview_click(event):
            item_id = tree.identify_row(event.y)  # Get the clicked row
            column = tree.identify_column(event.x)  # Get the clicked column
            if not item_id:
                return  # Click was outside a row

            # Get the product information from the clicked row
            item_values = tree.item(item_id, "values")
            if column == "#5":  # Actions column
                action_text = item_values[4]  # Get the "Actions" text
                product_id = products[int(item_id.split("I")[1]) - 1][0]  # Match the product_id
                if "Edit" in action_text:
                    handle_action(product_id, "edit")
                elif "Update Stock" in action_text:
                    handle_action(product_id, "update_stock")

        # Bind a single click event to the treeview
        tree.bind("<Button-1>", on_treeview_click)

        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", f"Error fetching product data: {e}")



        # Load Edit and Stock Update Icons (ensure you have icon files or use any image)
        # edit_icon = Image.open("edit_icon.png")  # Use actual icon path
        # edit_icon = edit_icon.resize((20, 20), Image.ANTIALIAS)
        # edit_icon = ImageTk.PhotoImage(edit_icon)

        # stock_icon = Image.open("stock_icon.png")  # Use actual icon path
        # stock_icon = stock_icon.resize((20, 20), Image.ANTIALIAS)
        # stock_icon = ImageTk.PhotoImage(stock_icon)



# Function to open the Edit Product form
def open_edit_product_form(product_id):
    # Create a new Toplevel window for editing a product
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Product")
    edit_window.geometry("400x300")
    edit_window.config(bg="#ecf0f1")

    # Fetch product details from the database
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, product_code, unit_price FROM product WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    product_name, product_code, unit_price = product

    # Labels and entry fields
    tk.Label(edit_window, text="Product Name:", bg="#ecf0f1").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    name_entry = tk.Entry(edit_window)
    name_entry.insert(0, product_name)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(edit_window, text="Product Code:", bg="#ecf0f1").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    code_entry = tk.Entry(edit_window)
    code_entry.insert(0, product_code)
    code_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(edit_window, text="Unit Price:", bg="#ecf0f1").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    price_entry = tk.Entry(edit_window)
    price_entry.insert(0, unit_price)
    price_entry.grid(row=2, column=1, padx=10, pady=10)

    # Update button
    def update_product():
        new_name = name_entry.get()
        new_code = code_entry.get()
        new_price = price_entry.get()

        # Update the product in the database
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE product
            SET product_name = %s, product_code = %s, unit_price = %s
            WHERE id = %s
        """, (new_name, new_code, new_price, product_id))
        conn.commit()
        cursor.close()
        conn.close()

        tk.messagebox.showinfo("Success", "Product updated successfully!")
        edit_window.destroy()
        # Refresh the product listing by destroying the existing view_window and re-opening
        if 'view_window' in globals() and view_window.winfo_exists():
            view_window.destroy()
        # Refresh the product listing
        open_view_products()

    tk.Button(edit_window, text="Update", command=update_product, bg="#3498db", fg="white").grid(row=3, column=0, columnspan=2, pady=20)


# Function to update the stock of the product
def update_stock(product_id):
    # Create a new Toplevel window for updating stock
    stock_window = tk.Toplevel(root)
    stock_window.title("Update Stock")
    stock_window.geometry("300x200")
    stock_window.config(bg="#ecf0f1")

    # Fetch current stock value
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM product WHERE id = %s", (product_id,))
    stock = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    tk.Label(stock_window, text="Current Stock:", bg="#ecf0f1").pack(pady=10)
    tk.Label(stock_window, text=f"{stock}", bg="#ecf0f1", font=("Arial", 14)).pack(pady=5)

    tk.Label(stock_window, text="New Stock Value:", bg="#ecf0f1").pack(pady=10)
    stock_entry = tk.Entry(stock_window)
    stock_entry.pack(pady=5)

    # Update button
    def update_stock_value():
        new_stock = stock_entry.get()
        if not new_stock.isdigit():
            tk.messagebox.showerror("Error", "Stock value must be a number!")
            return

        # Update the stock in the database
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE product
            SET stock = %s
            WHERE id = %s
        """, (new_stock, product_id))
        conn.commit()
        cursor.close()
        conn.close()

        tk.messagebox.showinfo("Success", "Stock updated successfully!")
        stock_window.destroy()
        # Refresh the product listing by destroying the existing view_window and re-opening
        if 'view_window' in globals() and view_window.winfo_exists():
            view_window.destroy()
        # Refresh the product listing
        open_view_products()

    tk.Button(stock_window, text="Update Stock", command=update_stock_value, bg="#3498db", fg="white").pack(pady=20)


# def refresh_product_listing(tree):
#     # Clear existing rows in the TreeView
#     for row in tree.get_children():
#         tree.delete(row)

#     # Fetch updated product data
#     conn = db_connect()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, product_name, product_code, unit_price, stock FROM product WHERE is_active=TRUE")
#     products = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     # Insert updated rows into the TreeView
#     for product in products:
#         product_id, product_name, product_code, unit_price, stock = product
#         tree.insert("", "end", values=(product_name, product_code, unit_price, stock, "Edit | Update Stock"))


# Main window
root = tk.Tk()
root.title("Login Interface")
root.geometry("400x300")  # Window size
root.resizable(True, True)  # Disable resizing and maximization


# Create a frame for the login form
frame = tk.Frame(root, bg="#ecf0f1", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame in the window

# Title label
title_label = tk.Label(frame, text="Login", font=("Helvetica", 24, "bold"), bg="#ecf0f1", fg="#34495e")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Username Label and Entry
username_label = tk.Label(frame, text="Username:", font=("Helvetica", 12), bg="#ecf0f1", fg="#34495e")
username_label.grid(row=1, column=0, pady=10, sticky="e")

entry_username = tk.Entry(frame, font=("Helvetica", 12), width=20, bd=2, relief="solid", fg="#34495e")
entry_username.grid(row=1, column=1, pady=10)

# Password Label and Entry
password_label = tk.Label(frame, text="Password:", font=("Helvetica", 12), bg="#ecf0f1", fg="#34495e")
password_label.grid(row=2, column=0, pady=10, sticky="e")

entry_password = tk.Entry(frame, font=("Helvetica", 12), width=20, bd=2, relief="solid", fg="#34495e", show="*")
entry_password.grid(row=2, column=1, pady=10)

# Error label for invalid credentials
error_label = tk.Label(frame, text="", font=("Helvetica", 12), fg="red", bg="#ecf0f1")
error_label.grid(row=5, column=0, columnspan=2, pady=5)

# Login Button
login_button = tk.Button(frame, text="Login", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", width=15, height=2, command=login)
login_button.grid(row=3, column=0, columnspan=2, pady=20)


# Initialize the database (only needed once)
create_db()

# Start the main loop
root.mainloop()