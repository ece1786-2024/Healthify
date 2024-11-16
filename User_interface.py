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
root.title("AI Chat Interface")
root.geometry("600x500")

# Slide menu
slide_menu = tk.Frame(root, width=200, bg="lightgray", height=500)
slide_menu.grid(row=0, column=0, sticky="ns")
slide_menu.grid_remove()  # Initially hidden

tk.Button(slide_menu, text="Diet Plan", command=show_diet_plan).pack(pady=10)
tk.Button(slide_menu, text="Fitness Plan", command=show_fitness_plan).pack(pady=10)
tk.Button(slide_menu, text="My Progress", command=show_progress).pack(pady=10)

# Header and toggle button
header = tk.Frame(root, bg="white", height=50)
header.grid(row=0, column=1, sticky="ew")

menu_button = tk.Button(header, text="☰", command=toggle_menu, bg="white", borderwidth=0)
menu_button.pack(side="left", padx=10)

profile_button = tk.Button(root, text="Profile", command=show_profile)
profile_button.grid(row=2, column=0, pady=20, sticky="sw")

# Chat area
chat_frame = tk.Frame(root, bg="white", height=450)
chat_frame.grid(row=1, column=1, sticky="nsew")

tk.Label(chat_frame, text="Hello! How can I help today?", font=("Helvetica", 14), bg="white").pack(pady=10)

chat_display = tk.Text(chat_frame, wrap=tk.WORD, height=20, width=50, state="disabled", bg="lightgray")
chat_display.pack(pady=10)

# Input box
chat_input = tk.Text(chat_frame, height=3, width=50, bg="white")
chat_input.pack(pady=10)

# Send button
send_button = tk.Button(chat_frame, text="Send", command=handle_chat)
send_button.pack()

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Run the application
root.mainloop()