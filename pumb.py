import tkinter as tk

# Function to clear the current content and replace it with new input fields
def open_new_user_input():
    # Clear the current content
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # Add new user input fields
    tk.Label(content_frame, text="Enter Your Name:").pack(pady=5)
    name_entry = tk.Entry(content_frame)
    name_entry.pack(pady=5)

    tk.Label(content_frame, text="Enter Your Email:").pack(pady=5)
    email_entry = tk.Entry(content_frame)
    email_entry.pack(pady=5)

    tk.Button(content_frame, text="Submit", command=lambda: print(f"Name: {name_entry.get()}, Email: {email_entry.get()}")).pack(pady=10)

# Function to display "Hi, how are you" text
def display_greeting():
    # Clear the current content
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # Display greeting text
    tk.Label(content_frame, text="Hi, how are you?").pack(pady=20)

# Create the main window
root = tk.Tk()
root.title("Tkinter Dynamic Content Example")
root.geometry("400x300")

# Create a menu bar
menu_bar = tk.Menu(root)

# Create a File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=open_new_user_input)
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Create an Edit menu
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Show Greeting", command=display_greeting)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

# Add the menu bar to the root window
root.config(menu=menu_bar)

# Create a frame for dynamic content
content_frame = tk.Frame(root)
content_frame.pack(fill="both", expand=True)

# Initial content
tk.Label(content_frame, text="Welcome to the application!").pack(pady=20)

# Run the application
root.mainloop()
