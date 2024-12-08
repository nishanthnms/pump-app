import tkinter as tk
from tkinter import messagebox,ttk
import psycopg2

content_frame = None

def open_new_product_input(root):  # Pass 'root' as a parameter here
    from dashboard import show_dashboard

    global content_frame

    # Clear existing content (including the stock listing)
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
            widget.destroy()

    content_frame = tk.Frame(root, bg="#f4f6f7")
    content_frame.pack(fill="both", expand=True)

    title_label = tk.Label(content_frame, text="Enter New Product Details", font=("Helvetica", 18, "bold"), bg="#f4f6f7", fg="#2c3e50")
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Create labeled entries for product details
    name_entry = create_labeled_entry("Product Name:", 1)
    code_entry = create_labeled_entry("Product Code:", 2)
    price_entry = create_labeled_entry("Unit Price:", 3)
    stock_entry = create_labeled_entry("Stock Quantity:", 4)

    # Submit Button to save new product details
    submit_button = tk.Button(content_frame, text="Submit", command=lambda: save_product(name_entry, code_entry, price_entry, stock_entry, root), bg="#27ae60", fg="#ffffff", font=("Helvetica", 12, "bold"))
    submit_button.grid(row=6, column=1, padx=10, pady=20, sticky="ew")

    # Back Button to return to the dashboard
    back_button = tk.Button(content_frame, text="Back", command=lambda: show_dashboard(root), bg="#c0392b", fg="#ffffff", font=("Helvetica", 12, "bold"))
    back_button.grid(row=6, column=0, padx=10, pady=20, sticky="ew")

def create_labeled_entry(label_text, row):
    label = tk.Label(content_frame, text=label_text, font=("Helvetica", 12), bg="#f4f6f7", fg="#34495e")
    label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
    
    entry = tk.Entry(content_frame, font=("Helvetica", 12), bg="#ecf0f1", fg="#2c3e50", bd=2, relief="solid", width=50)
    entry.grid(row=row, column=1, padx=10, pady=10, sticky="w")
    
    return entry

def save_product(name_entry, code_entry, price_entry, stock_entry, root):
    from dashboard import show_dashboard

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
        show_dashboard(root)

    except Exception as e:
        messagebox.showerror("Database Error", f"Error saving product: {e}")

def open_view_stock(root):  
    """
    Display product inventory listing with Edit and Update options.
    """
    # Clear the existing widgets except the menu
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
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
            tk.Label(row_frame, text=stock, font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=10, anchor="w").grid(row=0, column=3, padx=5)

            # Add Edit button
            edit_button = tk.Button(row_frame, text="Edit", command=lambda p_id=product_id: open_edit_product_form(root, p_id), bg="#f39c12")
            edit_button.grid(row=0, column=4, padx=5)

            # Add Update button
            update_button = tk.Button(row_frame, text="Update", command=lambda p_id=product_id: update_stock(root, p_id), bg="#27ae60")
            update_button.grid(row=0, column=5, padx=5)

        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching stock data: {e}")

def open_edit_product_form(root, product_id):
    global content_frame

    # Clear existing content (including the stock listing)
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
            widget.destroy()

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
    price_entry = create_labeled_entry("Unit Price:", str(unit_price), 3)
    stock_entry = create_labeled_entry("Stock Quantity:", str(stock), 4)

    # Save changes to the database
    def save_edited_product():
        updated_name = name_entry.get()
        updated_code = code_entry.get()
        updated_price = price_entry.get()
        updated_stock = stock_entry.get()

        if not updated_name or not updated_code or not updated_price or not updated_stock:
            messagebox.showerror("Input Error", "All fields must be filled!")
            return

        try:
            conn = psycopg2.connect(
                dbname="pump_stock_management",
                user="local_user",
                password="123",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()

            # Update product details in the database
            cursor.execute('''UPDATE product
                              SET product_name = %s, product_code = %s, unit_price = %s, stock = %s
                              WHERE id = %s''',
                           (updated_name, updated_code, updated_price, updated_stock, product_id))
            
            conn.commit()
            cursor.close()
            conn.close()

            # Success message and redirect to stock view
            messagebox.showinfo("Success", "Product details updated successfully!")
            open_view_stock(root)

        except Exception as e:
            messagebox.showerror("Error", f"Error updating product: {e}")
    # Back button
    back_button = tk.Button(content_frame, text="Back", command=lambda: open_view_stock(root), bg="#e74c3c")
    back_button.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

    # Save button
    save_button = tk.Button(content_frame, text="Save Changes", command=save_edited_product, bg="#3498db")
    save_button.grid(row=6, column=2, padx=10, pady=20, sticky="ew")

def update_stock(root, product_id):
    global content_frame

    # Clear existing content (including the stock listing)
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
            widget.destroy()

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

            messagebox.showinfo("Success", "Stock quantity updated successfully!")
            open_view_stock(root)  # Show the updated stock list
        # Back button
        back_button = tk.Button(content_frame, text="Back", command=lambda: open_view_stock(root), bg="#e74c3c")
        back_button.grid(row=6, column=1, sticky="ew")

        # Update stock button
        update_button = tk.Button(content_frame, text="Update Stock", command=save_stock, bg="#27ae60")
        update_button.grid(row=6, column=2, sticky="ew")

    except Exception as e:
        messagebox.showerror("Error", f"Error retrieving product details: {e}")

def create_labeled_entry(label_text, row):
    label = tk.Label(content_frame, text=label_text, font=("Helvetica", 12), bg="#f4f6f7", fg="#34495e")
    label.grid(row=row, column=0, padx=10, pady=10, sticky="w")

    entry = tk.Entry(content_frame, font=("Helvetica", 12), bg="#ecf0f1", fg="#2c3e50", bd=2, relief="solid", width=50)
    entry.grid(row=row, column=1, padx=10, pady=10, sticky="w")

    return entry
