import tkinter as tk
from tkinter import messagebox,ttk
import psycopg2
import functools


content_frame = None

def open_daily_sales(root):
    global grand_total_row
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
        headers2 = ["Bank Name", "Opening", "Closing", "Balance", "Action"]
        
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
                "closing": tk.Entry(rows_frame2, width=25),
                "balance": tk.Entry(rows_frame2, width=25),
            }

            row_data_second['delete'] = tk.Button(
                rows_frame2, 
                text="❌ Delete", 
                fg="red",
                command=lambda r=row_data_second: delete_row(r, rows2)  # Use lambda with default argument
            )

            row_data_second['bank_name'].grid(row=i, column=0, padx=5, pady=5)
            row_data_second['opening'].grid(row=i, column=1, padx=5, pady=5)
            row_data_second['closing'].grid(row=i, column=2, padx=5, pady=5)
            row_data_second['balance'].grid(row=i, column=3, padx=5, pady=5)
            row_data_second['delete'].grid(row=len(rows), column=4, padx=5, pady=5)

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

        rows2 = []

        # for bank_data in bank:
        #     bank_name = bank_data[0]  # Extract product name from tuple
        #     row_data_second = {
        #         "bank_name": tk.Label(rows_frame2, text=bank_name, width=20, anchor="w"),
        #         "opening": tk.Entry(rows_frame2, width=25),
        #         "closing": tk.Entry(rows_frame2, width=25),
        #         "balance": tk.Entry(rows_frame2, width=25),
        #     }

        #     row_data_second['delete'] = tk.Button(
        #         rows_frame2, 
        #         text="❌ Delete", 
        #         fg="red",
        #         command=lambda r=row_data_second: delete_row(r, rows2)  # Use lambda with default argument
        #     )

            # row_data_second['bank_name'].grid(row=i, column=0, padx=5, pady=5)
            # row_data_second['opening'].grid(row=i, column=1, padx=5, pady=5)
            # row_data_second['closing'].grid(row=i, column=2, padx=5, pady=5)
            # row_data_second['balance'].grid(row=i, column=3, padx=5, pady=5)
            # row_data_second['delete'].grid(row=len(rows), column=4, padx=5, pady=5)

            # rows2.append(row_data_second)

        # Submit Button for the second table
        submit_button2 = tk.Button(root, text="Submit", command=lambda: print("Second table submitted"))
        submit_button2.pack(pady=10)

    except Exception as e:
        import traceback;traceback.print_exc()
        messagebox.showerror("Error", f"Error fetching data: {e}")