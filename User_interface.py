# User_interface.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from TrainningRec import Training_recommendation
from Dietary_recommendation import Dietary_recommendation
from Recommendation_syn import generate_diet_plan, generate_fitness_plan, combine_plan, adjust_daily_progress, to_dataframe
import json
import pandas as pd
from openai import OpenAI
import os

client = OpenAI(
      api_key="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"
)

######################################
############ User Profile ############

profile_window = None
diet_plan_window = None
fitness_plan_window = None
timetable_window = None

diet_plan = {}
fitness_plan = {}
combined_plan = {}

# Define the calories_week data
calories_week = {
    "Monday": {"Calorie intake": 2500, "calories burned (exercise)": 0},
    "Tuesday": {"Calorie intake": 1800, "calories burned (exercise)": 1200},
    "Wednesday": {"Calorie intake": 2300, "calories burned (exercise)": 1300},
    "Thursday": {"Calorie intake": 2100, "calories burned (exercise)": 0},
    "Friday": {"Calorie intake": 1700, "calories burned (exercise)": 1100},
    "Saturday": {"Calorie intake": 1800, "calories burned (exercise)": 1200},
    "Sunday": {"Calorie intake": 2700, "calories burned (exercise)": 0},
}

# List of days from today (Tuesday) until next Monday
days = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday"]

messages = [
        {"role": "system", 
         "content":
            "You are a friendly fitness assistant, responsible for having a natural conversation with the user,"
            "Gradually collect the following information: name, age, gender, height, weight, fitness goals,"
            "Dietary preference(Heart Health, Low Sugar, High Energy, General), Current physical activity level (beginner, intermediate, advanced), health restrictions, dietary restrictions."
            "If null is present, ask the question and respond appropriately based on the user's answer."
        }
]

user_profile = {
    "name": None,
    "age": None,
    "gender": None,
    "height": None,
    "weight": None,
    "fitness goal": None,
    "dietary preference": None,
    "current physical activity levels": None,
    "health restrictions": None,
    "dietary restrictions": None
}

info_keys = {
        "name": "name",
        "age": "age",
        "gender": "gender",
        "height": "height",
        "weight": "weight",
        "fitness goal": "fitness goal",
        "dietary preference": "dietary preference",
        "current physical activity level": "current physical activity levels",
        "health restrictions": "health restrictions",
        "dietary restrictions": "dietary restrictions"  
    }

collected_keys = set()

def start_chat():
    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = messages,
        max_tokens = 150,
        temperature = 1.0,
    )

    assistant_message = response.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": assistant_message})
    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"Assistant: {assistant_message}\n")
    chat_display.see(tk.END)
    chat_display.config(state="disabled")

def handle_chat():
    user_input = chat_input.get("1.0", tk.END).strip()
    if not user_input:
        return None, None
    
    chat_input.delete("1.0", tk.END)
    messages.append({"role": "user", "content": user_input})
    
    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"You: {user_input}\n")
    chat_display.see(tk.END)
    chat_display.config(state="disabled")
    
    extraction_prompt = (
        " As an AI assistant, extract personal information provided from the user's response. "
        " The following keys need to collect information:"  
        " 'name(The user name is a combination of letters)', 'age', 'gender', 'height', 'weight', 'fitness goal', 'dietary preference', " 
        " 'current physical activity level', 'health restrictions', 'dietary restrictions'."  

        " Rules:" 
        " 1. For 'fitness goal':" 
        " - Mark as 'Weight Loss' if the user wants to lose weight." 
        " - Mark as 'Muscle Gain' if the user wants to gain muscle." 
        " - Mark as 'Improved Endurance' if the user wants to improve endurance." 
        " - Mark as 'Relieve Stress' if the user wants to relieve stress." 
        " - Mark as 'General' if the user has no specific fitness goal."

        " 2. For 'dietary preference' (what the user prefers to eat):" 
        " - Mark 'Heart Health' if the user prefers foods that improve heart health." 
        " - Mark 'Low Sugar' if the user prefers foods that lower sugar intake." 
        " - Mark 'High Energy' if the user prefers foods that provide high energy." 
        " - Mark 'General' if the user has no specific dietary requirements." 
      

        " 3. For 'current physical activity level':" 
        " - Mark 'beginner' if the user is new to exercise." 
        " - Mark 'intermediate' if the user engages in light exercise." 
        " - Mark 'advanced' if the user exercises regularly." 

        " Input: "
        "\n\nUser's reply:\n"
        f"\"\"\"\n{user_input}\n\"\"\""

        "\n\nUser's profile:\n"
        f"\"\"\"\n{user_profile}\n\"\"\""

        " Output:" 
        " - Provide the updated user profile in JSON format." 
        " - If a piece of information is not provided, do not include it in the JSON." 

        " Process:" 
        " - check the user's profile before ask the user questions if any missing or null values in the user's profile, ask until get information or mark 'unkown'." 
    )
    
    extraction_response = client.chat.completions.create(
            model = "gpt-4o",
            messages=[
                {"role": "system", "content": extraction_prompt}
            ],
            max_tokens= 150,
            temperature= 1.0,
        )
    
    extraction_result = extraction_response.choices[0].message.content.strip()
    
    extraction_result_cleaned = extraction_result
    if extraction_result.startswith("```") and extraction_result.endswith("```"):
        extraction_result_cleaned = extraction_result.strip("`")
        # Remove the language specifier if present
        extraction_result_cleaned = extraction_result_cleaned.replace("json\n", "").replace("json\n", "")
        extraction_result_cleaned = extraction_result_cleaned.strip()
        
    
    # Try to parse the JSON and update user_profile
    try:
        new_info = json.loads(extraction_result_cleaned)
        for key, value in new_info.items():
            key_lower = key.lower()
            if key_lower in info_keys:
                user_profile[info_keys[key_lower]] = value
                collected_keys.add(info_keys[key_lower])
    except json.JSONDecodeError as e:
        print("JSON decoding failed:", e)
        print("Extraction Result was:", extraction_result)
        pass  # Proceed to the next iteration
    
    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = messages,
        max_tokens = 150,
        temperature = 0.7,
    )
    
    assistant_message = response.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": assistant_message})
    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"Assistant: {assistant_message}\n")
    chat_display.see(tk.END)
    chat_display.config(state="disabled")

    if len(collected_keys) == len(info_keys):
        chat_display.config(state="normal")
        chat_display.insert(tk.END, "Assistant: All information collected.\n")
        chat_display.see(tk.END)
        chat_display.config(state="disabled")
        
        # Proceed to generate diet and fitness plan
        training_rec = Training_recommendation(user_profile)
        dietary_rec = Dietary_recommendation(user_profile)
        # Now proceed to simulate the days
        previous_day = "Monday"  # Assuming previous day is Monday
        for day in days:
            # Adjust the plans based on previous day's data
            process_recommendations(
                training_rec,
                dietary_rec,
                day=day,
                previous_day=previous_day,
                calories_week=calories_week
            )
            # Update the previous day
            previous_day = day
            # Update the GUI
            root.update()
        # After simulating the days, inform the user
        chat_display.config(state="normal")
        chat_display.insert(tk.END, "Assistant: Your plans have been generated.\n")
        chat_display.see(tk.END)
        chat_display.config(state="disabled")        

def show_profile():
    global profile_window  # Refer to the global variable

    if profile_window and profile_window.winfo_exists():
        # If the profile window exists and is open, destroy it
        profile_window.destroy()
        profile_window = None
    else:
        # If the profile window is not open, create and show it
        profile_window = tk.Toplevel(root)
        profile_window.title("Profile")
        profile_window.geometry("400x400")
        tk.Label(profile_window, text="Your Profile", font=("Helvetica", 16)).pack(pady=10)

        profile_display = tk.Text(profile_window, wrap=tk.WORD, height=15, width=50)
        profile_display.insert(tk.END, json.dumps(user_profile, indent=2))
        profile_display.config(state="disabled")
        profile_display.pack(pady=10)
        
####### End of User Profile ######### 
#####################################                            

def show_plan(table_data, title):
    plan_window = tk.Toplevel(root)
    plan_window.title(title)
    
    plan_window.geometry("1200x800")
    plan_window.resizable(True, True)
    
    canvas = tk.Canvas(plan_window, bg="#e6f7d1")
    scrollbar = ttk.Scrollbar(plan_window, orient="vertical", command=canvas.yview) 
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    frame = tk.Frame(canvas, bg="#e6f7d1")
    canvas_frame = canvas.create_window((0, 0), window=frame, anchor="nw")
        
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", on_frame_configure)
    
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_frame, width=event.width)
    canvas.bind("<Configure>", on_canvas_configure)
    
    header_frame = tk.Frame(frame, bg="#6ba96b")
    header_frame.grid(row=0, column=1, columnspan=len(table_data)+1, sticky="nsew")
    
    empty_label = tk.Label(header_frame, text="", bg="#6ba96b")
    empty_label.grid(row=0, column=0, sticky="nsew")
    
    for i, day in enumerate(table_data.keys()):
        label = tk.Label(
            header_frame, 
            text=day, 
            font=("Helvetica", 15), 
            width=25, 
            bg="#6ba96b",
            fg="white",
            justify="center",
            wraplength=150
            )
        label.grid(row=0, column=i, sticky="nsew")
    
    for row_i, time_of_day in enumerate(["Morning", "Noon", "Evening"]):
        label = tk.Label(
            frame,
            text=time_of_day, 
            font=("Helvetica", 18, "bold"), 
            width=15,
            bg="#556b2f", 
            fg="white",
            anchor="center")   
        label.grid(row=row_i+1, column=0, sticky="nsew")
        
        for col_i, day in enumerate(table_data.keys()):
            data = table_data[day][time_of_day]
            label = tk.Label(
                frame, 
                text=data, 
                font=("Helvetica", 12), 
                bg="#e6f7d1", 
                anchor="w", 
                wraplength=150, 
                justify="left")
            label.grid(row=row_i+1, column=col_i+1, sticky="nsew")
    
    total_columns = len(table_data) + 1
    total_rows = len(["Morning", "Noon", "Evening"]) + 1
    for i in range(total_columns):
        frame.grid_columnconfigure(i, weight=3)
        header_frame.grid_columnconfigure(i, weight=3)
    for i in range(total_rows):
        frame.grid_rowconfigure(i, weight=1)
        
    return plan_window
     

def prepare_table_data(diet_plan=None, fitness_plan=None, combined_timetable=None):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    table = {day: {"Morning": "", "Noon": "", "Evening": ""} for day in days}
        
    for day in days:
        table[day]["Morning"] = ""
        table[day]["Noon"] = ""
        table[day]["Evening"] = ""
        
        if diet_plan is not None and combined_timetable is None:
            morning_diet = diet_plan.get(day, {}).get("Morning", [])
            if morning_diet:
                formatted_morning = "\n".join(morning_diet)
                table[day]["Morning"] += f"Foods:\n{formatted_morning}\n"
            
            noon_diet = diet_plan.get(day, {}).get("Noon", [])
            if noon_diet:
                formatted_noon = "\n".join(noon_diet)
                table[day]["Noon"] += f"Foods:\n{formatted_noon}\n"
                
            evening_diet = diet_plan.get(day, {}).get("Evening", [])
            if evening_diet:
                formatted_evening = "\n".join(evening_diet)
                table[day]["Evening"] += f"Foods:\n{formatted_evening}\n"
                        
        if fitness_plan is not None and combined_timetable is None:
            exercises = fitness_plan.get(day, {})
            morning_exercises = exercises.get("Morning", [])
            evening_exercises = exercises.get("Evening", [])
            morning_exercises_text = ", ".join(morning_exercises)
            evening_exercises_text = ", ".join(evening_exercises)
            table[day]["Morning"] += f"Exercises:\n{morning_exercises_text}\n"
            table[day]["Evening"] += f"Exercises:\n{evening_exercises_text}\n"
                
                
        if combined_timetable is not None:
            morning_diet = diet_plan.get(day, {}).get("Morning", [])
            if morning_diet:
                formatted_morning = "\n".join(morning_diet)
                table[day]["Morning"] += f"Foods:\n{formatted_morning}\n"
            
            noon_diet = diet_plan.get(day, {}).get("Noon", [])
            if noon_diet:
                formatted_noon = "\n".join(noon_diet)
                table[day]["Noon"] += f"Foods:\n{formatted_noon}\n"
                
            evening_diet = diet_plan.get(day, {}).get("Evening", [])
            if evening_diet:
                formatted_evening = "\n".join(evening_diet)
                table[day]["Evening"] += f"Foods:\n{formatted_evening}\n"
            
            morning_exercises = combined_timetable.get(day, {}).get("Fitness", {}).get("Morning", [])
            morning_exercise_text = ", ".join(morning_exercises)
            table[day]["Morning"] += f"Exercises: {morning_exercise_text}\n"
            evening_exercises = combined_timetable.get(day, {}).get("Fitness", {}).get("Evening", [])
            evening_exercise_text = ", ".join(evening_exercises)
            table[day]["Evening"] += f"Exercises: {evening_exercise_text}\n"
                    
    return table
           

def show_diet_plan():
    table_data = prepare_table_data(diet_plan=diet_plan)
    show_plan(table_data, "Diet Plan")
    
def show_fitness_plan():
    table_data = prepare_table_data(fitness_plan=fitness_plan)
    show_plan(table_data, "Fitness Plan")
    
def show_timetable():
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
root.configure(bg="#e6f7d1")

root.grid_rowconfigure(1, weight=1) 
root.grid_columnconfigure(1, weight=1)  

# Slide menu
slide_menu = tk.Frame(root, width=200, bg="#6ba96b", height=500)
slide_menu.grid(row=0, column=0, rowspan=3, sticky="ns")
slide_menu.grid_remove()  # Initially hidden

menu_button_style = {"font": ("Helvetica", 12), "bg": "#6b8e23", "fg": "white", "relief": "flat"}
tk.Button(slide_menu, text="My Diet Plan", **menu_button_style, command=show_diet_plan).pack(pady=15, padx=10, fill="x")
tk.Button(slide_menu, text="My Fitness Plan", **menu_button_style, command=show_fitness_plan).pack(pady=15, padx=10, fill="x")
tk.Button(slide_menu, text="My Timetable", **menu_button_style, command=show_timetable).pack(pady=15, padx=10, fill="x")

# Header and toggle button
header = tk.Frame(root, bg="#e6f7d1")
header.grid(row=0, column=1, sticky="ew")

menu_button = tk.Button(header, text="☰", font=("Helvetica", 15), bg="#e6f7d1", relief="flat", command=toggle_menu)
menu_button.pack(side="left", padx=10)

# Main chat frame
chat_frame = tk.Frame(root, bg="#e6f7d1", padx=20, pady=20)
chat_frame.grid(row=1, column=1, sticky="nsew")
chat_frame.grid_rowconfigure(0, weight=0)  
chat_frame.grid_rowconfigure(1, weight=1)
chat_frame.grid_rowconfigure(2, weight=0)
chat_frame.grid_rowconfigure(3, weight=0)
chat_frame.grid_columnconfigure(0, weight=1)  

# welcome message
welcome_label = tk.Label(chat_frame, text="Welcome to Healthify!", font=("Helvetica", 20), bg="#e6f7d1", fg="#6ba96b")
welcome_label.grid(row=0, column=0, pady=10)

# chat display
chat_display = tk.Text(chat_frame, wrap=tk.WORD, height=20, width=70, state="disabled", bg="#f7f7f7", fg="black", font=("Helvetica", 15))
chat_display.grid(row=1, column=0, sticky="nsew", pady=10)

# Input box for chat
chat_input = tk.Text(chat_frame, height=3, width=70, bg="white", fg="black", font=("Helvetica", 15))
chat_input.grid(row=2, column=0, sticky="ew", pady=10)

def handle_enter(event):
    handle_chat()
    return "break"

chat_input.bind("<Return>", handle_enter)

def process_recommendations(training_rec, dietary_rec, day=None, previous_day=None, calories_week=None):
    global diet_plan, fitness_plan, combined_plan

    # Plan adjustment based on previous day
    diet_plan_raw = generate_diet_plan(day, dietary_rec)
    fitness_plan_raw = generate_fitness_plan(day, training_rec)
    adjusted_exercise_plan, adjusted_diet_plan = adjust_daily_progress(
        day,
        previous_day,
        calories_week,
        diet_plan_raw,
        fitness_plan_raw,
    )

    # Update the global plans with adjusted plans for the day
    diet_plan[day] = adjusted_diet_plan
    fitness_plan[day] = adjusted_exercise_plan
    combined_plan[day] = combine_plan(adjusted_diet_plan, adjusted_exercise_plan)

    # Display the adjusted plans
    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"\nAssistant: Here is your adjusted plan for {day}:\n")    
    chat_display.insert(tk.END, f"Diet Plan for {day} is complete. \n")
    chat_display.insert(tk.END, f"Fitness Plan for {day} is complete. \n")
    chat_display.see(tk.END)
    chat_display.config(state="disabled")

# Send button
send_button = tk.Button(chat_frame, text="Send", font=("Helvetica", 12), bg="#6ba96b", fg="white", command=lambda: process_chat())
send_button.grid(row=3, column=0, pady=10)

def process_chat():
    handle_chat()

# Profile button
profile_button = tk.Button(
    root, 
    text="My Profile", 
    font=("Helvetica", 12), 
    bg="#6b8e23", 
    fg="white", 
    command=show_profile,
    relief="flat",
    anchor="center"
    )
profile_button.grid(row=2, column=0, pady=10, sticky="sw")

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Start the chat
start_chat()

# Run the application
root.mainloop()

__all__ = [
    "root",
    "start_chat",
    "process_recommendations",
    "Training_recommendation",
    "Dietary_recommendation",
    "user_profile",
    "collected_keys",
    "info_keys",
    "chat_display",
    "diet_plan",
    "fitness_plan",
    "combined_plan"
]
