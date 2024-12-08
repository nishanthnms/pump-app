import tkinter as tk
from tkinter import messagebox
from dashboard import show_dashboard
from stock_management import open_new_product_input, open_view_stock
import psycopg2

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
                comments VARCHAR(250),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_bank FOREIGN KEY (bank_id) REFERENCES bank (id) ON DELETE CASCADE
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
            show_dashboard(root)  # Pass the root object to the show_dashboard function
        else:
            error_label.config(text="Invalid username or password", fg="red")

        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")

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

# Initialize the database (only needed once)
create_db()

# Start the Tkinter main loop
root.mainloop()
