import tkinter as tk
from tkinter import messagebox,ttk
import psycopg2
import functools
from datetime import datetime


content_frame = None

def open_daily_sales(root):
    from dashboard import show_dashboard
    from stock_management import open_new_product_input, open_view_stock
    from bank import open_view_bank, open_new_bank_input

    logged_user_id = getattr(root, 'logged_user_id', None)
    
    if not logged_user_id:
        messagebox.showerror("Error", "No user logged in")
        return
        
    global grand_total_row
    # Clear the existing widgets except the menu
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
            widget.destroy()

    # Create the header frame
    header_frame = tk.Frame(root, bg="#2c3e50", height=50)
    header_frame.pack(side="top", fill="x")

    # Create the logout button (top-right corner)
    logout_button = tk.Button(header_frame, text="Logout", font=("Helvetica", 12), bg="#e74c3c", fg="white", relief="flat", command=root.quit)
    logout_button.pack(side="right", padx=20, pady=10)

    # Create a frame for the sidebar (left-aligned menu)
    sidebar = tk.Frame(root, bg="#2c3e50", width=250, height=root.winfo_height(), padx=10, pady=10)
    sidebar.pack(side="left", fill="y")

    # Create a frame for the content area
    content_frame = tk.Frame(root, bg="#ecf0f1")
    content_frame.pack(side="right", fill="both", expand=True)

    # Create buttons for the sidebar menu
    home_button = tk.Button(sidebar, text="Home", font=("Helvetica", 14), bg="#34495e", fg="white", command=lambda: show_dashboard(root), anchor="w", relief="flat", padx=20)
    home_button.pack(fill="x", pady=10)

    # Stock Management Button
    stock_button = tk.Button(sidebar, text="Stock Management", font=("Helvetica", 14), bg="#34495e", fg="white", anchor="w", relief="flat", padx=20)
    stock_button.pack(fill="x", pady=10)

    # Submenu for Stock Management (Always visible)
    stock_submenu = tk.Frame(sidebar, bg="#34495e")
    stock_submenu.pack(fill="x", pady=10, padx=20)

    add_product_button = tk.Button(stock_submenu, text="Add New Product", font=("Helvetica", 12), bg="#7f8c8d", fg="white", anchor="w", relief="flat", padx=20, command=lambda: open_new_product_input(root))
    add_product_button.pack(fill="x", pady=5)

    view_stock_button = tk.Button(stock_submenu, text="View Stock", font=("Helvetica", 12), bg="#7f8c8d", fg="white", anchor="w", relief="flat", padx=20, command=lambda: open_view_stock(root))
    view_stock_button.pack(fill="x", pady=5)

    # Bank Management Button
    bank_button = tk.Button(sidebar, text="Bank Management", font=("Helvetica", 14), bg="#34495e", fg="white", anchor="w", relief="flat", padx=20)
    bank_button.pack(fill="x", pady=10)

    # Submenu for Bank Management (Always visible)
    bank_submenu = tk.Frame(sidebar, bg="#34495e")
    bank_submenu.pack(fill="x", pady=10, padx=20)

    view_bank_button = tk.Button(bank_submenu, text="View Bank", font=("Helvetica", 12), bg="#7f8c8d", fg="white", anchor="w", relief="flat", padx=20, command=lambda: open_view_bank(root))
    view_bank_button.pack(fill="x", pady=5)

    add_bank_button = tk.Button(bank_submenu, text="Add New Bank", font=("Helvetica", 12), bg="#7f8c8d", fg="white", anchor="w", relief="flat", padx=20, command=lambda: open_new_bank_input(root))
    add_bank_button.pack(fill="x", pady=5)

    # Daily Log (Sales Tracker) Button
    daily_log_button = tk.Button(sidebar, text="Daily Sales Tracker", font=("Helvetica", 14), bg="#34495e", fg="white", anchor="w", relief="flat", padx=20, command=lambda: open_daily_sales(root))
    daily_log_button.pack(fill="x", pady=10)


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
        cursor.execute("SELECT product_name, unit_price FROM product WHERE is_active = TRUE")
        products = cursor.fetchall()

        # Add a title label
        title_label = tk.Label(
            root,
            text="Daily Sales Tracker",
            font=("Helvetica", 20, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=10
        )
        title_label.pack(fill="x")

        # Create a header for the product list
        header_frame = tk.Frame(root, bg="#34495e", padx=10, pady=5)
        header_frame.pack(fill="x", padx=10)
        headers = ["Product Name", "Opening", "Closing", "Sale", "Unit Profit", "Total Profit", "Action"]
        
        for i, header in enumerate(headers):
            tk.Label(
                header_frame,
                text=header,
                font=("Helvetica", 12, "bold"),
                bg="#34495e",
                fg="#ecf0f1",
                width=15,
                anchor="w"
            ).grid(row=0, column=i, padx=10, pady=10)

        # Create rows for each product
        rows_frame = tk.Frame(root)
        rows_frame.pack(fill=tk.X, padx=10, pady=10)

        rows = []

        # grand_total_label = tk.Label(root, text="Grand Total: 0.00", font=("Helvetica", 14, "bold"), fg="green")
        # grand_total_label.pack(pady=10)

        def update_grand_total():
            """Calculate and update the grand total of Total Profit."""
            grand_total = 0
            for row in rows:
                try:
                    total_profit = float(row['total_profit'].get() or 0)
                    grand_total += total_profit
                    print(grand_total,'-----grand_total')
                except ValueError:
                    pass

            grand_total_row['total_profit'].config(state='normal')
            grand_total_row['total_profit'].delete(0, tk.END)
            grand_total_row['total_profit'].insert(0, f"{grand_total:.2f}")
            grand_total_row['total_profit'].config(state='disabled')
            # grand_total_label.config(text=f"Grand Total: {grand_total:.2f}")

        def calculate_sales(row_data):
            try:
                opening = float(row_data['opening'].get() or 0)
                closing = float(row_data['closing'].get() or 0)
                sales = opening - closing
                row_data['sale'].delete(0, tk.END)
                row_data['sale'].insert(0, f"{sales:.2f}")
                calculate_total_profit(row_data)
            except ValueError:
                pass

        def calculate_total_profit(row_data):
            """Calculate Total Profit based on Unit Profit and Sale."""
            try:
                unit_profit = float(row_data['unit_profit'].get() or 0)
                sale = float(row_data['sale'].get() or 0)
                total_profit = unit_profit * sale
                row_data['total_profit'].config(state='normal')
                row_data['total_profit'].delete(0, tk.END)
                row_data['total_profit'].insert(0, f"{total_profit:.2f}")
                row_data['total_profit'].config(state='disabled')
                update_grand_total()
            except ValueError:
                pass  # Ignore invalid input for now

        def delete_row(row_data, rows_list):
            if 'bank_name' in row_data:
                row_name = row_data['bank_name'].cget('text')
            elif 'product_name' in row_data:
                row_name = row_data['product_name'].cget('text')
            """Remove a row from the table."""
            confirm = messagebox.askyesno(
                "Confirm Deletion", 
                f"Are you sure you want to delete the row for {row_name}?"
            )
            
            if confirm:
                for widget in row_data.values():
                    widget.destroy()
                if row_data in rows_list:
                    rows_list.remove(row_data)
                if 'total_profit' in row_data:
                    update_grand_total()

        def submit_data():
            """Save all data to the database."""
            try:
                conn = psycopg2.connect(
                    dbname="pump_stock_management",
                    user="local_user",
                    password="123",
                    host="localhost",
                    port="5432"
                )
                cursor = conn.cursor()

                # 1. Save Daily Sales Tracker data to sales_log
                for row in rows:
                    product_name = row['product_name'].cget("text")
                    cursor.execute(
                        "SELECT id FROM product WHERE product_name = %s AND is_active = TRUE",
                        (product_name,)
                    )
                    product_result = cursor.fetchone()
                    
                    if not product_result:
                        raise Exception(f"Product not found: {product_name}")
                    opening = float(row['opening'].get() or 0)
                    closing = float(row['closing'].get() or 0)
                    sale = float(row['sale'].get() or 0)
                    unit_profit = float(row['unit_profit'].get() or 0)
                    total_profit = float(row['total_profit'].get() or 0)

                    cursor.execute(
                        """
                        INSERT INTO sale_log 
                        (product_id, opening_stock, closing_stock, sale, unit_profit, total_profit, added_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (product_result[0], opening, closing, sale, unit_profit, total_profit, logged_user_id)
                    )

                # 2. Save Bank Data to bank_log
                for row in rows2:
                    bank_name = row['bank_name'].cget("text")
                    cursor.execute(
                        "SELECT id FROM bank WHERE bank_name = %s AND is_active = TRUE",
                        (bank_name,)
                    )
                    bank_result = cursor.fetchone()
                    
                    if not bank_result:
                        raise Exception(f"Product not found: {bank_name}")
                    opening = float(row['opening'].get() or 0)
                    withdraw = float(row['withdraw'].get() or 0)
                    deposit = float(row['deposit'].get() or 0)
                    closing = float(row['closing'].get() or 0)
                    comments = row['comments'].get("1.0", tk.END).strip()
                    log_date = datetime.now().date()

                    cursor.execute(
                        """
                        INSERT INTO bank_log 
                        (bank_id, opening_balance, withdraw, deposit, closing_balance, comments, log_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (bank_result[0], opening, withdraw, deposit, closing, comments, log_date)
                    )

                # 3. Save Collection Data to collection_log
                inhand_amount = float(rows_frame3.grid_slaves(row=0, column=1)[0].get() or 0)
                bank_amount = float(rows_frame3.grid_slaves(row=1, column=1)[0].get() or 0)
                
                cursor.execute(
                    """
                    INSERT INTO collection_log 
                    (inhand_amount, bank_amount, added_by)
                    VALUES (%s, %s, %s)
                    """,
                    (inhand_amount, bank_amount, logged_user_id)
                )

                conn.commit()
                messagebox.showinfo("Success", "Data saved successfully!")
                
            except Exception as e:
                import traceback;traceback.print_exc()
                conn.rollback()  # Rollback in case of error
                messagebox.showerror("Database Error", f"Error saving data: {e}")
            finally:
                conn.close()

        for product in products:
            product_name = product[0]  # Extract product name from tuple
            unit_price = product[1]  # Extract unit price from tuple
            row_data = {
                "product_name": tk.Label(rows_frame, text=product_name, width=20, anchor="w"),
                "opening": tk.Entry(rows_frame, width=25),
                "closing": tk.Entry(rows_frame, width=25),
                "sale": tk.Entry(rows_frame, width=25),
                "unit_profit": tk.Entry(rows_frame, text=unit_price, width=25),
                "total_profit": tk.Entry(rows_frame, width=25, state='disabled'),
            }
            row_data['unit_profit'].delete(0, tk.END)  # Clear any existing text first
            row_data['unit_profit'].insert(0, f"{unit_price:.2f}")

            row_data['delete'] = tk.Button(
                rows_frame, 
                text="❌ Delete", 
                fg="red",
                command=lambda r=row_data: delete_row(r, rows)  # Use lambda with default argument
            )


            row_data['product_name'].grid(row=len(rows), column=0, padx=5, pady=5)
            row_data['opening'].grid(row=len(rows), column=1, padx=5, pady=5)
            row_data['closing'].grid(row=len(rows), column=2, padx=5, pady=5)
            row_data['sale'].grid(row=len(rows), column=3, padx=5, pady=5)
            row_data['unit_profit'].grid(row=len(rows), column=4, padx=5, pady=5)
            row_data['total_profit'].grid(row=len(rows), column=5, padx=5, pady=5)
            row_data['delete'].grid(row=len(rows), column=6, padx=5, pady=5)

            # Set default Total Profit to 0.00
            row_data['total_profit'].config(state='normal')
            row_data['total_profit'].insert(0, "0.00")
            row_data['total_profit'].config(state='disabled')

            # Add event to auto-calculate Sale
            row_data['opening'].bind('<KeyRelease>', lambda e, r=row_data: calculate_sales(r))
            row_data['closing'].bind('<KeyRelease>', lambda e, r=row_data: calculate_sales(r))

            # Add events to auto-calculate Total Profit
            row_data['sale'].bind('<KeyRelease>', lambda e, r=row_data: calculate_total_profit(r))
            row_data['unit_profit'].bind('<KeyRelease>', lambda e, r=row_data: calculate_total_profit(r))

            rows.append(row_data)

        # Create Grand Total Row
        grand_total_row = {
            "product_name": tk.Label(rows_frame, text="GRAND TOTAL", width=20, anchor="w", font=("Arial", 10, "bold")),
            "opening": tk.Label(rows_frame, text="", width=25),
            "closing": tk.Label(rows_frame, text="", width=25),
            "sale": tk.Label(rows_frame, text="", width=25),
            "unit_profit": tk.Label(rows_frame, text="", width=25),
            "total_profit": tk.Entry(rows_frame, width=25, state='disabled', font=("Arial", 10, "bold"))
        }

        # No delete button for grand total row
        grand_total_row['product_name'].grid(row=len(rows), column=0, padx=5, pady=5)
        grand_total_row['opening'].grid(row=len(rows), column=1, padx=5, pady=5)
        grand_total_row['closing'].grid(row=len(rows), column=2, padx=5, pady=5)
        grand_total_row['sale'].grid(row=len(rows), column=3, padx=5, pady=5)
        grand_total_row['unit_profit'].grid(row=len(rows), column=4, padx=5, pady=5)
        grand_total_row['total_profit'].grid(row=len(rows), column=5, padx=5, pady=5)

        # Initialize grand total to 0.00
        grand_total_row['total_profit'].config(state='normal')
        grand_total_row['total_profit'].insert(0, "0.00")
        grand_total_row['total_profit'].config(state='disabled')

        # Add a second section title ***********************
        cursor.execute("SELECT bank_name FROM bank WHERE is_active = TRUE")
        bank = cursor.fetchall()

        title_label2 = tk.Label(
            root,
            text="Bank Data",
            font=("Helvetica", 20, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=10
        )
        title_label2.pack(fill="x")

        # Create a header for the second table

        header_frame2 = tk.Frame(root, bg="#34495e", padx=10, pady=5)
        header_frame2.pack(fill="x", padx=10)
        headers2 = ["Bank Name", "Withdraw", "Deposit", "Opening", "Closing", "Comments", "Action"]
        
        for i, header in enumerate(headers2):
            tk.Label(
                header_frame2,
                text=header,
                font=("Helvetica", 12, "bold"),
                bg="#34495e",
                fg="#ecf0f1",
                width=15,
                anchor="w"
            ).grid(row=0, column=i, padx=5, pady=5)

        # Create rows for the second table
        rows_frame2 = tk.Frame(root)
        rows_frame2.pack(fill=tk.X, padx=10, pady=5)

        rows2 = []

        for bank_data in bank:
            bank_name = bank_data[0]  # Extract product name from tuple
            row_data_second = {
                "bank_name": tk.Label(rows_frame2, text=bank_name, width=20, anchor="w"),
                "opening": tk.Entry(rows_frame2, width=25),
                "withdraw": tk.Entry(rows_frame2, width=30),
                "deposit": tk.Entry(rows_frame2, width=30),
                "closing": tk.Entry(rows_frame2, width=25),
                "balance": tk.Entry(rows_frame2, width=25),
                "comments": tk.Text(rows_frame2, width=30, height=1),
            }

            row_data_second['delete'] = tk.Button(
                rows_frame2, 
                text="❌ Delete", 
                fg="red",
                command=lambda r=row_data_second: delete_row(r, rows2)  # Use lambda with default argument
            )

            row_data_second['bank_name'].grid(row=i, column=0, padx=5, pady=5)
            row_data_second['opening'].grid(row=i, column=1, padx=5, pady=5)
            row_data_second['withdraw'].grid(row=i, column=2, padx=5, pady=5)
            row_data_second['deposit'].grid(row=i, column=3, padx=5, pady=5)
            row_data_second['closing'].grid(row=i, column=4, padx=5, pady=5)
            row_data_second['comments'].grid(row=i, column=5, padx=5, pady=5)
            row_data_second['delete'].grid(row=len(rows), column=7, padx=5, pady=5)

            rows2.append(row_data_second)

        # Add a third section title ***********************
        title_label3 = tk.Label(
            root,
            text="Daily Collection",
            font=("Helvetica", 20, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=10
        )
        title_label3.pack(fill="x")

        # Create a header for the third table

        header_frame3 = tk.Frame(root, bg="#34495e", padx=10, pady=5)
        header_frame3.pack(fill="x", padx=10)
        headers3 = ["Type", "Amount"]
        
        for i, header in enumerate(headers3):
            tk.Label(
                header_frame3,
                text=header,
                font=("Helvetica", 12, "bold"),
                bg="#34495e",
                fg="#ecf0f1",
                width=15,
                anchor="w"
            ).grid(row=0, column=i, padx=5, pady=5)

        # Create rows for the third table
        rows_frame3 = tk.Frame(root)
        rows_frame3.pack(fill=tk.X, padx=10, pady=5)

        static_types = ["Inhand", "Bank"]
        for i, static_type in enumerate(static_types):
            # Static "Type" label
            tk.Label(
                rows_frame3,
                text=static_type,
                width=15,
                anchor="w"
            ).grid(row=i, column=0, padx=5, pady=5)

            tk.Entry(
                rows_frame3,
                font=("Helvetica", 12),
                width=20
            ).grid(row=i, column=1, padx=5, pady=5)

        # Submit Button for the second table
        submit_button2 = tk.Button(root, text="Submit", font=("Arial", 14), bg="#27ae60", fg="white", command=submit_data)
        submit_button2.pack(pady=10)

    except Exception as e:
        import traceback;traceback.print_exc()
        messagebox.showerror("Error", f"Error fetching data: {e}")