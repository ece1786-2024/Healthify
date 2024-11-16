import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from User_profile import extract_user_profile 
from Recommendation_syn import simulate_diet, simulate_fitness, generate_diet_plan, generate_fitness_plan, combine_plan, to_dataframe
import json
import pandas as pd



diet_list = simulate_diet()
fitness_list = simulate_fitness()
diet_plan = generate_diet_plan(diet_list)
fitness_plan = generate_fitness_plan(fitness_list)
combined_plan = combine_plan(diet_plan, fitness_plan)

# Convert plans to DataFrames
df_diet = to_dataframe(diet_plan, plan_type="Diet")
df_fitness = to_dataframe(fitness_plan, plan_type="Fitness")
df_combined = to_dataframe(combined_plan)


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
    
def show_plan(table_data, title):
    plan_window = tk.Toplevel(root)
    plan_window.title(title)
    plan_window.geometry("900x600")
    
    canvas = tk.Canvas(plan_window, bg="#f3f4e9")
    frame = tk.Frame(canvas, bg="#f3f4e9")
    scrollbar = ttk.Scrollbar(plan_window, orient="vertical", command=canvas.yview) 
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0,0), window=frame, anchor="nw") 
    
    header_frame = tk.Frame(frame, bg="#f3f4e9")
    header_frame.grid(row=0, column=1, columnspan=7)
    for i, day in enumerate(table_data.keys()):
        label = tk.Label(header_frame, text=day, font=("Helvetica", 12), width=10, bg="#556b2f")
        label.grid(row=0, column=i, sticky="nsew")
    
    for row_i, time_of_day in enumerate(["Morning", "Noon", "Evening"]):
        label = tk.Label(frame, text=time_of_day, font=("Helvetica", 12), width=10, anchor="w")
        label.grid(row=row_i+1, column=0, sticky="w")
        
        for col_i, day in enumerate(table_data.keys()):
            data = table_data[day][time_of_day]
            label = tk.Label(frame, text=data, font=("Helvetica", 10), bg="#f3f4e9", anchor="w", wraplength=120, justify="left")
            label.grid(row=row_i+1, column=col_i+1, sticky="w")
    
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
        
    
    
def prepare_table_data(diet_plan=None, fitness_plan=None, combined_timetable=None):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    table = {day: {"Morning": "", "Noon": "", "Evening": ""} for day in days}
    
    for day in days:
        
        table[day]["Morning"] = ""
        table[day]["Noon"] = ""
        table[day]["Evening"] = ""
        
        if diet_plan and not combined_timetable:
            for meal_str in diet_plan.get(day, []):
                if ': ' in meal_str:
                    meal_type, foods = meal_str.split(': ', 1)
                    if meal_type == "Breakfast":
                        table[day]["Morning"] += f"Foods:\n{foods}\n"
                    elif meal_type == "Lunch":
                        table[day]["Noon"] += f"Foods:\n{foods}\n"
                    elif meal_type == "Dinner":
                        table[day]["Evening"] += f"Foods:\n{foods}\n"
                        
        if fitness_plan and not combined_timetable:
            exercises = fitness_plan.get(day, "No exercises")
            table[day]["Morning"] += f"Exercises:\n{exercises}\n"
            table[day]["Evening"] += f"Exercises:\n{exercises}\n"
                
                
        if combined_timetable:
            for meal_str in diet_plan.get(day, []):
                if ': ' in meal_str:
                    meal_type, foods = meal_str.split(': ', 1)
                    if meal_type == "Breakfast":
                        table[day]["Morning"] += f"Foods:\n{foods}\n"
                    elif meal_type == "Lunch":
                        table[day]["Noon"] += f"Foods:\n{foods}\n"
                    elif meal_type == "Dinner":
                        table[day]["Evening"] += f"Foods:\n{foods}\n"
            exercises = fitness_plan.get(day, "No exercises")
            table[day]["Morning"] += f"Exercises:\n{exercises}\n"
            table[day]["Evening"] += f"Exercises:\n{exercises}\n"


                
                        
    return table
    
    
    
     
      
def show_diet_plan():
    print(diet_plan)
    table_data = prepare_table_data(diet_plan=diet_plan)
    show_plan(table_data, "Diet Plan")
    
def show_fitness_plan():
    print(fitness_plan)
    table_data = prepare_table_data(fitness_plan=fitness_plan)
    show_plan(table_data, "Fitness Plan")
    
def show_timetable():
    print(combined_plan)
    table_data = prepare_table_data(diet_plan=diet_plan, fitness_plan=fitness_plan, combined_timetable=combined_plan)
    show_plan(table_data, "Combined Timetable")
    
    

# Function to show the slide menu
def toggle_menu():
    if slide_menu.winfo_viewable():
        slide_menu.grid_remove()
    else:
        slide_menu.grid()


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
tk.Button(slide_menu, text="My Diet Plan", **menu_button_style, command=show_diet_plan).pack(pady=15, padx=10, fill="x")
tk.Button(slide_menu, text="My Fitness Plan", **menu_button_style, command=show_fitness_plan).pack(pady=15, padx=10, fill="x")
tk.Button(slide_menu, text="My Timetable", **menu_button_style, command=show_timetable).pack(pady=15, padx=10, fill="x")

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