import psycopg2
import tkinter as tk
from tkinter import messagebox

def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")
        return None

def open_bank_management():
    def fetch_bank_details():
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bank ORDER BY id")
            bank_details = cursor.fetchall()
            conn.close()
            return bank_details
        else:
            return []

    def create_bank_form(edit_mode=False, existing_data=None):
        def submit():
            bank_name = bank_name_var.get().strip()
            ifsc_code = ifsc_code_var.get().strip()
            branch_name = branch_name_var.get().strip()
            account_number = account_number_var.get().strip()
            account_balance = account_balance_var.get().strip()

            # Validation
            if not all([bank_name, ifsc_code, branch_name, account_number, account_balance]):
                messagebox.showerror("Input Error", "All fields are required!")
                return

            try:
                account_balance = float(account_balance)
            except ValueError:
                messagebox.showerror("Input Error", "Account Balance must be a number!")
                return

            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                try:
                    if edit_mode and existing_data:
                        # Update existing record
                        cursor.execute(''' 
                            UPDATE bank 
                            SET bank_name = %s, 
                                ifsc_code = %s, 
                                branch_name = %s, 
                                account_number = %s, 
                                account_balance = %s
                            WHERE id = %s
                        ''', (bank_name, ifsc_code, branch_name, account_number, account_balance, existing_data[0]))
                        success_message = "Bank details updated successfully!"
                    else:
                        # Insert new record
                        cursor.execute(''' 
                            INSERT INTO bank (bank_name, ifsc_code, branch_name, account_number, account_balance)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (bank_name, ifsc_code, branch_name, account_number, account_balance))
                        success_message = "Bank details added successfully!"

                    conn.commit()
                    messagebox.showinfo("Success", success_message)
                    refresh_table()
                    form_window.destroy()
                except psycopg2.Error as e:
                    messagebox.showerror("Database Error", str(e))
                finally:
                    conn.close()

        # Ensure the form window is only created once
        if hasattr(create_bank_form, "form_window") and create_bank_form.form_window.winfo_exists():
            create_bank_form.form_window.lift()  # Focus the existing form if it's already open
            return

        form_window = tk.Toplevel(bank_window)
        form_window.title("Add/Edit Bank Details")
        form_window.geometry("400x350")
        form_window.configure(bg="#f4f4f4")

        # Declare StringVar variables
        bank_name_var = tk.StringVar(value=existing_data[1] if edit_mode else '')
        ifsc_code_var = tk.StringVar(value=existing_data[2] if edit_mode else '')
        branch_name_var = tk.StringVar(value=existing_data[3] if edit_mode else '')
        account_number_var = tk.StringVar(value=existing_data[4] if edit_mode else '')
        account_balance_var = tk.StringVar(value=str(existing_data[5]) if edit_mode else '')

        # Form labels and entries with styling
        labels = ["Bank Name", "IFSC Code", "Branch Name", "Account Number", "Account Balance"]
        vars = [bank_name_var, ifsc_code_var, branch_name_var, account_number_var, account_balance_var]

        for i, (label, var) in enumerate(zip(labels, vars)):
            tk.Label(form_window, text=label, bg="#f4f4f4", font=('Arial', 10), anchor='w').grid(row=i, column=0, padx=20, pady=10, sticky='e')
            tk.Entry(form_window, textvariable=var, font=('Arial', 10)).grid(row=i, column=1, padx=20, pady=10)

        # Submit button
        submit_text = "Update" if edit_mode else "Add"
        tk.Button(form_window, text=f"{submit_text} Bank", command=submit, bg="#4CAF50", fg="white", font=('Arial', 12)).grid(row=len(labels), column=0, columnspan=2, pady=20)

        # Store form window reference
        create_bank_form.form_window = form_window

    def edit_bank(bank_id):
        # Fetch the full record for the selected bank
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bank WHERE id = %s", (bank_id,))
            existing_data = cursor.fetchone()
            conn.close()

            if existing_data:
                create_bank_form(edit_mode=True, existing_data=existing_data)

    def delete_bank(bank_id):
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this bank record?"):
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM bank WHERE id = %s", (bank_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Bank details deleted successfully!")
                    refresh_table()
                except psycopg2.Error as e:
                    messagebox.showerror("Database Error", str(e))
                finally:
                    conn.close()

    def refresh_table():
        # Clear existing rows in the table
        for row in table_frame.winfo_children():
            row.destroy()

        # Fetch bank details
        bank_details = fetch_bank_details()

        # Populate table with header row
        headers = ["Bank Name", "IFSC Code", "Branch Name", "Account Number", "Account Balance", "Actions"]
        for col, header in enumerate(headers):
            tk.Label(table_frame, text=header, width=20, anchor='w', font=('Arial', 12, 'bold'), bg="#007BFF", fg="white", padx=10).grid(row=0, column=col, padx=5, pady=5)

        # Populate bank details in table rows
        for index, detail in enumerate(bank_details):
            # Create a row of bank data
            tk.Label(table_frame, text=detail[1], width=20, anchor='w').grid(row=index+1, column=0, padx=10, pady=5)
            tk.Label(table_frame, text=detail[2], width=20, anchor='w').grid(row=index+1, column=1, padx=10, pady=5)
            tk.Label(table_frame, text=detail[3], width=20, anchor='w').grid(row=index+1, column=2, padx=10, pady=5)
            tk.Label(table_frame, text=detail[4], width=20, anchor='w').grid(row=index+1, column=3, padx=10, pady=5)
            tk.Label(table_frame, text=detail[5], width=20, anchor='w').grid(row=index+1, column=4, padx=10, pady=5)

            # Edit Button
            tk.Button(table_frame, text="Edit", command=lambda bank_id=detail[0]: edit_bank(bank_id), bg="#FFC107", fg="black").grid(row=index+1, column=5, padx=10, pady=5)
            
            # Delete Button
            tk.Button(table_frame, text="Delete", command=lambda bank_id=detail[0]: delete_bank(bank_id), bg="#DC3545", fg="white").grid(row=index+1, column=6, padx=10, pady=5)

    # Create Bank Management Window
    bank_window = tk.Toplevel()
    bank_window.title("Bank Management")
    bank_window.geometry("900x500")
    bank_window.configure(bg="#f4f4f4")

    # Create the table frame
    table_frame = tk.Frame(bank_window, bg="#f4f4f4")
    table_frame.pack(pady=20)

    # Add a button to open the form for creating a new bank record
    tk.Button(bank_window, text="Add Bank", command=create_bank_form, bg="#28A745", fg="white", font=('Arial', 12)).pack(pady=20)

    # Refresh the table with bank details
    refresh_table()