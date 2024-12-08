import tkinter as tk
from tkinter import messagebox
import psycopg2

content_frame = None


def open_view_bank(root):  
    """
    Display bank inventory listing with Edit and Update options.
    """
    # Clear the existing widgets except the menu
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
            widget.destroy()

    try:
        # Connect to the database and fetch bank details
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, bank_name, ifsc_code, branch_name, account_number, account_balance FROM bank WHERE is_active=TRUE")
        banks = cursor.fetchall()

        # Add a title label
        title_label = tk.Label(
            root,
            text="Bank Inventory",
            font=("Helvetica", 20, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=10
        )
        title_label.pack(fill="x")

        # Create a header for the bank list
        header_frame = tk.Frame(root, bg="#34495e", padx=10, pady=5)
        header_frame.pack(fill="x", padx=10)

        headers = ["Bank Name", "IFSC Code", "Branch Name", "Account Number", "Account Balance", "Edit", "Update"]
        column_widths = [20, 20, 15, 20, 20, 10, 10]

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

        # Create rows for each bank
        for index, bank in enumerate(banks):
            print(index,'-------index')
            bank_id, bank_name, ifsc_code, branch_name, account_number, account_balance = bank

            # Alternate row colors
            bg_color = "#ecf0f1" if index % 2 == 0 else "#bdc3c7"

            row_frame = tk.Frame(root, bg=bg_color, padx=10, pady=5)
            row_frame.pack(fill="x", padx=10)

            # Add bank details
            tk.Label(row_frame, text=bank_name, font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=20, anchor="w").grid(row=0, column=0, padx=5)
            tk.Label(row_frame, text=ifsc_code, font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=20, anchor="w").grid(row=0, column=1, padx=5)
            tk.Label(row_frame, text=branch_name, font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=20, anchor="w").grid(row=0, column=2, padx=5)
            tk.Label(row_frame, text=account_number, font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=20, anchor="w").grid(row=0, column=3, padx=5)
            tk.Label(row_frame, text=account_balance, font=("Helvetica", 12), bg=bg_color, fg="#34495e", width=10, anchor="w").grid(row=0, column=4, padx=5)

            # Add Edit button
            edit_button = tk.Button(row_frame, text="Edit", command=lambda p_id=bank_id: open_edit_bank_form(root, p_id), bg="#f39c12")
            edit_button.grid(row=0, column=5, padx=5)

            # Add Delete button
            update_button = tk.Button(row_frame, text="Delete", command=lambda p_id=bank_id: delete_bank(root, p_id), bg="#27ae60")
            update_button.grid(row=0, column=6, padx=5)

        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching stock data: {e}")


def open_new_bank_input(root):
    from dashboard import show_dashboard

    global content_frame

    # Clear existing content (including the stock listing)
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
            widget.destroy()

    content_frame = tk.Frame(root, bg="#f4f6f7")
    content_frame.pack(fill="both", expand=True)

    title_label = tk.Label(content_frame, text="Enter New Bank Details", font=("Helvetica", 18, "bold"), bg="#f4f6f7", fg="#2c3e50")
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Create labeled entries for bank details
    name_entry = create_labeled_entry("Bank Name:", 1)
    code_entry = create_labeled_entry("IFSC Code:", 2)
    branch_entry = create_labeled_entry("Branch Name:", 3)
    acc_no_entry = create_labeled_entry("Account Number:", 4)
    acc_blnc_entry = create_labeled_entry("Account Balance:", 5)

    # Submit Button to save new bank details
    submit_button = tk.Button(content_frame, text="Submit", command=lambda: save_bank(name_entry, code_entry, branch_entry, acc_no_entry, acc_blnc_entry, root), bg="#27ae60", fg="#ffffff", font=("Helvetica", 12, "bold"))
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

def save_bank(name_entry, code_entry, branch_entry, acc_no_entry, acc_blnc_entry, root):
    from dashboard import show_dashboard

    bank_name = name_entry.get()
    ifsc_code = code_entry.get()
    branch_name = branch_entry.get()
    account_number = acc_no_entry.get()
    account_balance = acc_blnc_entry.get()

    # Validate inputs
    if not bank_name or not ifsc_code or not branch_name or not account_number or not account_balance:
        messagebox.showerror("Input Error", "Please fill all fields")
        return

    try:
        # Connect to the database and insert bank
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO bank (bank_name, ifsc_code, branch_name, account_number, account_balance)
                            VALUES (%s, %s, %s, %s, %s)''',
                        (bank_name, ifsc_code, branch_name, account_number, account_balance))
        
        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        # Show success message
        messagebox.showinfo("Success", "Bank added successfully!")

        # Redirect to the dashboard
        show_dashboard(root)

    except Exception as e:
        messagebox.showerror("Database Error", f"Error saving bank: {e}")


def open_edit_bank_form(root, bank_id):
    global content_frame

    # Clear existing content (including the stock listing)
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
            widget.destroy()

    content_frame = tk.Frame(root, bg="#f4f6f7")  # Set background color
    content_frame.pack(fill="both", expand=True)

    # Fetch bank details
    conn = psycopg2.connect(
        dbname="pump_stock_management",
        user="local_user",
        password="123",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT bank_name, ifsc_code, branch_name, account_number, account_balance FROM bank WHERE is_active=TRUE")
    bank = cursor.fetchone()
    conn.close()

    if not bank:
        messagebox.showerror("Error", "Bank not found!")
        return

    bank_name, ifsc_code, branch_name, account_number, account_balance = bank

    # Add a title label for Edit bank
    title_label = tk.Label(content_frame, text="Edit Bank Details", font=("Helvetica", 18, "bold"), bg="#f4f6f7", fg="#2c3e50")
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

    name_entry = create_labeled_entry("Bank Name:", bank_name, 1)
    code_entry = create_labeled_entry("IFSC Code:", ifsc_code, 2)
    branch_entry = create_labeled_entry("Branch Name:", branch_name, 3)
    acc_no_entry = create_labeled_entry("Accoount Number:", account_number, 4)
    acc_blnc_entry = create_labeled_entry("Account Balance:", account_balance, 5)

    # Save changes to the database
    def save_edited_bank():
        updated_name = name_entry.get()
        updated_code = code_entry.get()
        updated_branch = branch_entry.get()
        updated_acc_no = acc_no_entry.get()
        updated_acc_blnc = acc_blnc_entry.get()

        if not updated_name or not updated_code or not updated_branch or not updated_acc_no or not updated_acc_blnc:
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

            # Update bank details in the database
            cursor.execute('''UPDATE bank
                              SET bank_name = %s, ifsc_code = %s, branch_name = %s, account_number = %s, account_balance = %s
                              WHERE id = %s''',
                           (updated_name, updated_code, updated_branch, updated_acc_no, updated_acc_blnc, bank_id))
            
            conn.commit()
            cursor.close()
            conn.close()

            # Success message and redirect to stock view
            messagebox.showinfo("Success", "Bank details updated successfully!")
            open_view_bank(root)

        except Exception as e:
            messagebox.showerror("Error", f"Error updating bank: {e}")
    # Back button
    back_button = tk.Button(content_frame, text="Back", command=lambda: open_view_bank(root), bg="#e74c3c")
    back_button.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

    # Save button
    save_button = tk.Button(content_frame, text="Save Changes", command=save_edited_bank, bg="#3498db")
    save_button.grid(row=6, column=2, padx=10, pady=20, sticky="ew")

def delete_bank(root, bank_id):
    global content_frame

    # Clear existing content (including the stock listing)
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):  # Skip menu widgets
            widget.destroy()

    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True)

    # Database connection with error handling
    try:
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete the bank?"
        )

        if confirm:
            # Check for existing stocks or dependencies
            cursor.execute("DELETE FROM bank WHERE id = %s", (bank_id,))
            conn.commit()

            # Success message
            messagebox.showinfo(
                "Bank Deleted", 
                f"Bank 'Bank removed successfully."
            )
            
            # Optionally refresh the bank list or return to bank list view
            open_view_bank(root)  # Assuming you have a view_banks function

        else:
            open_view_bank(root)  # Assuming you have a view_banks function


    except psycopg2.Error as e:
        # Detailed error handling
        messagebox.showerror(
            "Database Error", 
            f"An error occurred: {str(e)}"
        )
        conn.rollback()

    finally:
        # Always close database connections
        if conn:
            cursor.close()
            conn.close()