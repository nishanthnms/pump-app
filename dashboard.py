import tkinter as tk
from tkinter import messagebox
import psycopg2
from stock_management import open_new_product_input, open_view_stock
from bank import open_view_bank, open_new_bank_input
from daily_sales import open_daily_sales

# Global reference for the content frame
content_frame = None

def show_dashboard(root):
    global content_frame
    root.title("Pump Management - Dashboard")

    # Clear the current content (login form or previous frame)
    for widget in root.winfo_children():
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
        card_frame.pack(pady=20, padx=20)

        # Fetch stock data
        cursor = conn.cursor()
        cursor.execute("SELECT product_name, product_code, stock FROM product WHERE is_active=TRUE LIMIT 10")
        products = cursor.fetchall()

        # Define the card width and height
        card_width = 300
        card_height = 100

        # Loop through products and create cards
        for i, product in enumerate(products):
            product_name, product_code, stock = product

            # Convert product name to uppercase
            product_name = product_name.upper()

            # Determine stock text and color based on the value
            if product_name.lower() in ["petrol", "diesel"] or product_code.startswith(("PTRL", "DESL")):
                stock_text = f"{stock} Liters"
            else:
                stock_text = f"{stock} Units"

            # Choose a color for the stock value based on quantity (example: green for high, red for low)
            stock_color = "#27ae60" if stock > 50 else "#e74c3c"  # Green for stock > 50, red for stock <= 50

            # Create a frame for each product card with a shaded border
            card = tk.Frame(card_frame, width=card_width, height=card_height, bd=2, relief="solid", bg="#ffffff", 
                            highlightbackground="#7f8c8d", highlightcolor="#7f8c8d", highlightthickness=2)
            card.grid(row=i // 3, column=i % 3, padx=20, pady=20, sticky="nsew")
            card.pack_propagate(False)  # Prevent auto-resizing

            # Add product name as card title (uppercase text)
            title_label = tk.Label(card, text=product_name, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#34495e")
            title_label.pack(pady=10)

            # Display stock value with an attractive color
            stock_label = tk.Label(card, text=stock_text, font=("Helvetica", 12), bg="#ffffff", fg=stock_color)
            stock_label.pack()


        # Close database connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Unable to fetch dashboard data: {e}")

# Main application window
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    root.state("zoomed")
    show_dashboard(root)
    root.mainloop()
