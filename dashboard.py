import tkinter as tk
from tkinter import messagebox
import psycopg2
from stock_management import open_new_product_input, open_view_stock
from bank import open_view_bank, open_new_bank_input

# Global reference for the content frame
content_frame = None

# Function to show the dashboard in the same window
def show_dashboard(root):
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
    menu_bar.add_command(label="Home", command=lambda: show_dashboard(root))

    # Stock Management menu
    stock_menu = tk.Menu(menu_bar, tearoff=0)
    stock_menu.add_command(label="Add New Product", command=lambda: open_new_product_input(root))  # Pass 'root' to this function
    stock_menu.add_command(label="View Stock", command=lambda: open_view_stock(root))  # Pass 'root' to this function
    menu_bar.add_cascade(label="Stock Management", menu=stock_menu)

    # Report menu
    report_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Report", menu=report_menu)

    # Bank menu
    bank_menu = tk.Menu(menu_bar, tearoff=0)
    bank_menu.add_command(label="View Bank", command=lambda: open_view_bank(root))  # Pass 'root' to this function
    bank_menu.add_command(label="Add New Bank", command=lambda: open_new_bank_input(root))  # Pass 'root' to this function
    menu_bar.add_cascade(label="Bank Management", menu=bank_menu)


    root.config(menu=menu_bar)

    # Display the dashboard content
    open_dashboard(root)

def open_dashboard(root):
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

        # Create a frame for the cards
        card_frame = tk.Frame(content_frame, bg="#ecf0f1")
        card_frame.pack(pady=20)

        # Fetch stock data
        cursor = conn.cursor()
        cursor.execute("SELECT product_name, product_code, stock FROM product WHERE is_active=TRUE LIMIT 10")
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
