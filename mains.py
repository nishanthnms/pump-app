import tkinter as tk
from tkinter import messagebox
from dashboard import show_dashboard
from stock_management import open_new_product_input, open_view_stock
import psycopg2

from hupper import start_reloader


if __name__ == "__main__":
    start_reloader('mains.__main__')

# Function to create the PostgreSQL database and tables
def create_db():
    try:
        conn = psycopg2.connect(
            dbname="pump_stock_management",
            user="local_user",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Create users table with unique constraint on username
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE, 
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

        # Create bank table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank (
                id SERIAL PRIMARY KEY,
                bank_name TEXT NOT NULL,
                ifsc_code VARCHAR(250) UNIQUE NOT NULL,
                branch_name VARCHAR(250) NOT NULL,
                account_number VARCHAR(250) NOT NULL,
                account_balance NUMERIC(20,2) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')


        # Create bank_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank_log (
                id SERIAL PRIMARY KEY,
                bank_id INTEGER NOT NULL, 
                log_date DATE NOT NULL,
                opening_balance NUMERIC(20,2) NOT NULL,
                withdraw NUMERIC(20,2) NOT NULL,
                deposit NUMERIC(20,2) NOT NULL,
                closing_balance NUMERIC(20,2) NOT NULL,
                added_by INTEGER NOT NULL,
                comments VARCHAR(250),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_bank FOREIGN KEY (bank_id) REFERENCES bank (id) ON DELETE CASCADE,
                CONSTRAINT fk_added_by FOREIGN KEY (added_by) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')


        # Create stock_update_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_update_log (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL, 
                previous_stock NUMERIC(20,2) NOT NULL,
                updated_stock NUMERIC(20,2) NOT NULL,
                updated_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product (id) ON DELETE CASCADE,
                CONSTRAINT fk_updated_by FOREIGN KEY (updated_by) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # Create sale_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_log (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                opening_stock NUMERIC(20,2) NOT NULL,
                closing_stock NUMERIC(20,2) NOT NULL,
                sale NUMERIC(20,2) NOT NULL,
                unit_profit NUMERIC(20,2) NOT NULL,
                total_profit NUMERIC(20,2) NOT NULL,
                added_by INTEGER NOT NULL, -- Assuming this references a user or employee table
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product (id) ON DELETE CASCADE,
                CONSTRAINT fk_added_by FOREIGN KEY (added_by) REFERENCES users (id) ON DELETE CASCADE
            )
        ''') 

        # Create collection_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_log (
                id SERIAL PRIMARY KEY,
                inhand_amount NUMERIC(20,2) NOT NULL,
                bank_amount NUMERIC(20,2) NOT NULL,
                added_by INTEGER NOT NULL, -- Assuming this references a user or employee table
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_added_by FOREIGN KEY (added_by) REFERENCES users (id) ON DELETE CASCADE

            )
        ''') 

        # Create expense_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_log (
                id SERIAL PRIMARY KEY,
                comment VARCHAR(255) NOT NULL,
                amount NUMERIC(20,2) NOT NULL,
                added_by INTEGER NOT NULL, -- Assuming this references a user or employee table
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_added_by FOREIGN KEY (added_by) REFERENCES users (id) ON DELETE CASCADE
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
        import traceback
        traceback.print_exc()
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
            # Store user ID in the root window for global access
            root.logged_user_id = user[0]
            error_label.config(text="")
            show_dashboard(root)  # Pass the root object to the show_dashboard function
        else:
            error_label.config(text="Invalid username or password", fg="red")

        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")

# Create root window
root = tk.Tk()
root.title("Login")
root.geometry("1280x720")

# Create login form
frame = tk.Frame(root, bg="#ecf0f1", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

title_label = tk.Label(frame, text="Login", font=("Helvetica", 24, "bold"), bg="#ecf0f1", fg="#34495e")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

username_label = tk.Label(frame, text="Username:", font=("Helvetica", 12), bg="#ecf0f1", fg="#34495e")
username_label.grid(row=1, column=0, pady=10, sticky="e")

entry_username = tk.Entry(frame, font=("Helvetica", 12), width=20, bd=2, relief="solid", fg="#34495e")
entry_username.grid(row=1, column=1, pady=10)
entry_username.focus_set()  # Set focus on the username field

password_label = tk.Label(frame, text="Password:", font=("Helvetica", 12), bg="#ecf0f1", fg="#34495e")
password_label.grid(row=2, column=0, pady=10, sticky="e")

entry_password = tk.Entry(frame, font=("Helvetica", 12), width=20, bd=2, relief="solid", fg="#34495e", show="*")
entry_password.grid(row=2, column=1, pady=10)

error_label = tk.Label(frame, text="", font=("Helvetica", 12), fg="red", bg="#ecf0f1")
error_label.grid(row=3, column=0, columnspan=2, pady=5)

# login_button = tk.Button(frame, text="Login", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", width=15, height=2, command=login)
# login_button.grid(row=4, column=0, columnspan=2, pady=20)
login_button = tk.Button(
    frame,
    text="Login",
    font=("Helvetica", 12, "bold"),
    bg="#3498db",
    fg="white",
    width=15,
    height=2,
    command=login
)
login_button.grid(row=4, column=0, columnspan=2, pady=20, sticky="n")


# Bind the Enter key to the login function
root.bind('<Return>', lambda event: login())

# Initialize the database (only needed once)
create_db()

# Start the Tkinter main loop
root.mainloop()
