import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from User_profile import extract_user_profile 
import json


def handle_chat():
    user_input = chat_input.get("1.0", "end-1c")
    if not user_input.strip():
        messagebox.showerror("Error", "Please enter some text!")
        return
    try:
        # Simulate AI response for now
        ai_response = "This is a sample AI response. You can integrate your AI logic here."
        chat_display.config(state="normal")
        chat_display.insert(tk.END, f"You: {user_input}\nAI: {ai_response}\n\n")
        chat_display.config(state="disabled")
        chat_input.delete("1.0", tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process input: {e}")
        
        
def show_profile():
    # Simulate profile generation
    profile = extract_user_profile("Example user input text for AI")  # Replace with user input
    profile_window = tk.Toplevel(root)
    profile_window.title("Profile")
    profile_window.geometry("400x400")
    tk.Label(profile_window, text="Your Profile", font=("Helvetica", 16)).pack(pady=10)
    profile_display = tk.Text(profile_window, wrap=tk.WORD, height=15, width=50)
    profile_display.insert(tk.END, profile)
    profile_display.config(state="disabled")
    profile_display.pack(pady=10)

# Function to show the slide menu
def toggle_menu():
    if slide_menu.winfo_viewable():
        slide_menu.grid_remove()
    else:
        slide_menu.grid()

# Function placeholders for menu buttons
def show_diet_plan():
    messagebox.showinfo("Diet Plan", "Diet Plan will be displayed here!")

def show_fitness_plan():
    messagebox.showinfo("Fitness Plan", "Fitness Plan will be displayed here!")

def show_progress():
    messagebox.showinfo("My Progress", "Your progress will be displayed here!")

# Main window setup
root = tk.Tk()
root.title("Healthify")
root.geometry("800x600")
root.configure(bg="#f3f4e9")

# Slide menu
slide_menu = tk.Frame(root, width=200, bg="#556b2f", height=500)
slide_menu.grid(row=0, column=0, rowspan=3, sticky="ns")
slide_menu.grid_remove()  # Initially hidden

menu_button_style = {"font": ("Helvetica", 12), "bg": "#6b8e23", "fg": "white", "relief": "flat"}
tk.Button(slide_menu, text="Diet Plan", **menu_button_style, command=show_diet_plan).pack(pady=10, padx=10, fill="x")
tk.Button(slide_menu, text="Fitness Plan", **menu_button_style, command=show_fitness_plan).pack(pady=10, padx=10, fill="x")
tk.Button(slide_menu, text="My Progress", **menu_button_style, command=show_progress).pack(pady=10, padx=10, fill="x")

# Header and toggle button
header = tk.Frame(root, bg="#f3f4e9")
header.grid(row=0, column=1, sticky="ew")

menu_button = tk.Button(header, text="☰", font=("Helvetica", 10), bg="#f3f4e9", relief="flat", command=toggle_menu)
menu_button.pack(side="left", padx=10)

# Main chat frame
chat_frame = tk.Frame(root, bg="#f3f4e9", padx=20, pady=20)
chat_frame.grid(row=1, column=1, sticky="nsew")

# welcome message
welcome_label = tk.Label(chat_frame, text="Hello! Welcome to Healthify!\nHow can I help you today?", font=("Helvetica", 16), bg="#f3f4e9", fg="#556b2f")
welcome_label.pack(pady=10)

# chat display
chat_display = tk.Text(chat_frame, wrap=tk.WORD, height=20, width=70, state="disabled", bg="#f7f7f7", fg="black")
chat_display.pack(pady=10)

# Input bot for chat
chat_input = tk.Text(chat_frame, height=3, width=70, bg="white", fg="black")
chat_input.pack(pady=10)

# sent button
send_button = tk.Button(chat_frame, text="Send", font=("Helvetica", 12), bg="#556b2f", fg="white", command=handle_chat)
send_button.pack(pady=10)

# profile button
profile_button = tk.Button(root, text="My Profile", font=("Helvetica", 12), bg="#556b2f", fg="white", command=show_profile)
profile_button.grid(row=2, column=0, pady=10, sticky="sw")


root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Run the application
root.mainloop()