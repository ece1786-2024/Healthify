# User_interface.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from TrainningRec import Training_recommendation
from Dietary_recommendation import Dietary_recommendation
from Recommendation_syn import fetch_user_data, generate_diet_plan, generate_fitness_plan, combine_plan, adjust_daily_progress, to_dataframe
import json
import pandas as pd
from openai import OpenAI
import os
import sqlite3
import threading

# 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
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
    "Monday": {"Calorie intake": 2500, "calories burned (exercise)": 0}, # the day before first day
    "Tuesday": {"Calorie intake": 2200, "calories burned (exercise)": 420},
    "Wednesday": {"Calorie intake": 2300, "calories burned (exercise)": 0}, # lazy, not exercise
    "Thursday": {"Calorie intake": 2300, "calories burned (exercise)": 430},
    "Friday": {"Calorie intake": 2400, "calories burned (exercise)": 0},    # the rest day
    "Saturday": {"Calorie intake": 2600, "calories burned (exercise)": 400},
    "Sunday": {"Calorie intake": 2500, "calories burned (exercise)": 350},  
}

# List of days from today (Tuesday) until next Monday
days = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday"]

messages = [
        {"role": "system", 
         "content":
            "You are a friendly fitness assistant, responsible for having a natural conversation with the user in the soft way,"
            "The tone of asking questions should not be very strong, and make user feel comfortable and friendly. Give respectful to the user."
            "If user feel sad or unhappy, try to make them happy and encourge them."
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
        model = "gpt-4o-mini",
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
        "As an AI assistant, extract personal information provided from the user's response. "
        "The following keys need to collect information: "
        "'name (The user name is a combination of letters)', 'age', 'gender', 'height', 'weight', 'fitness goal', 'dietary preference', "
        "'current physical activity level', 'health restrictions', 'dietary restrictions'."

        "Rules:"
        "1. For 'height':"
        "- The height should be in centimeters, not including the unit."
        "- If the height is in feet and inches, convert it to centimeters."

        "2. For 'weight':"
        "- The weight should be in kilograms, not including the unit."
        "- If the weight is in pounds, convert it to kilograms."

        "3. For 'fitness goal':"
        "- Mark as 'Weight Loss' if the user wants to lose weight."
        "- Mark as 'Muscle Gain' if the user wants to gain muscle."
        "- Mark as 'Improved Endurance' if the user wants to improve endurance."
        "- Mark as 'Relieve Stress' if the user wants to relieve stress."
        "- Mark as 'General' if the user has no specific fitness goal."
        "- If the user has multiple fitness goals, mark the first one."

        "4. For 'dietary preference' (what the user prefers to eat):"
        "-Realted to the fitness goal, if fitness goal is 'Weight Loss', mean he wants low sugar fodd, if fitness goal is 'Muscle Gain', high energy food is prefered."
        "- Mark 'Heart Health' if the user prefers foods that improve heart health."
        "- Mark 'Low Sugar' if the user prefers foods that lower sugar intake."
        "- Mark 'High Energy' if the user prefers foods that provide high energy."
        "- Mark 'Vegan' if the user follows a vegan diet."
        "- Mark 'Keto', 'Paleo', 'Gluten-Free', or other specific preferences based on their dietary approach."
        "- Mark 'General' If the user does not have these specific dietary requirements above."
        "- If the user has multiple dietary preferences, mark the first one."

        "5. For 'current physical activity level':"
        "- Mark 'beginner' if the user is new to exercise."
        "- Mark 'intermediate' if the user engages in light exercise."
        "- Mark 'advanced' if the user exercises regularly."
        "- If the user gives vague information, ask more probing questions until the user gives a clear reply."

        "6. For 'health restrictions':"
        "- health restrictions focus on restrictions on body parts"
        "- If the user says 'no', 'no restrictions', or similar, mark 'No Restrictions'."

        "7. For 'dietary restrictions':"
        "- dietary restrictions focus on restrictions  on certain ingredients and foods."
        "- If the user says 'no', 'no restrictions', or similar, mark 'No Restrictions'."

        "8. If the user's response is irrelevant or nonsensical for the requested information, do not update the profile for that key and indicate that the information is still missing."

        "\nProcess:"
        "- Update the profile based on the information include."
        "- Do not infer or assume any information not provided in the user's latest reply."
        "- For each key, if the user's reply provides valid information, update the profile."
        "- If the user's reply does not include the missing keys, ask follow-up questions to gather specific details for missing keys."

        "\nInput:"
        f"User's reply:\n\"\"\"\n{user_input}\n\"\"\""

        "\nOutput:"
        "- Provide the updated user profile in JSON format."
        "- Only include keys that have been updated based on the user's latest reply."
        "- Do not include keys that have not been updated in this reply."
    )
    try:
        extraction_response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": extraction_prompt}
                ],
                max_tokens= 150,
                temperature= 1.0,
            )
    except Exception as e:
        print("OpenAI API call failed:", e)
        return 
    
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
        print("New info:", new_info)
        for key, value in new_info.items():
            key_lower = key.lower()
            if key_lower in info_keys:
                user_profile[info_keys[key_lower]] = value
                collected_keys.add(info_keys[key_lower])
    except json.JSONDecodeError as e:
        print("JSON decoding failed:", e)
        print("Extraction Result was:", extraction_result)
        pass  # Proceed to the next iteration
    
    missing_info = [key for key, value in user_profile.items() if value is None]
    print("current user profile:", user_profile)    
    print("Missing info:", missing_info)
    
    if missing_info:
        missing_info_text = ", ".join(missing_info)
        system_prompt = (
            f"As a friendly fitness assistant, please continue the conversation with the user. "
            f"Based on the current user profile: {user_profile}, "
            f"please ask the user to provide the following missing information: {missing_info_text}. "
            "Ask in a friendly and conversational manner. "
            "Do not assume any information that the user has not provided. "
            "If the user's previous response was irrelevant or nonsensical for the requested information, "
            "kindly ask again for clarification."
        )
        messages.append({"role": "system", "content": system_prompt})
    else:
        system_prompt = (
        "All user information has been collected. Please inform the user that their personalized plans are being generated. Tell the user it will take a few minutes to generate the plans. Let the user bear with you."
        )
        messages.append({"role": "system", "content": system_prompt})
        
    try:
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            max_tokens = 150,
            temperature = 0.7,
        )
    except Exception as e:
        print("OpenAI API call failed:", e)
        return 
    
    assistant_message = response.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": assistant_message})
    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"Assistant: {assistant_message}\n")
    chat_display.see(tk.END)
    chat_display.config(state="disabled")    
    
    if not missing_info:
        threading.Thread(target=generate_plans).start()
       
    
        
def generate_plans():
    training_rec = Training_recommendation(user_profile)
    dietary_rec = Dietary_recommendation(user_profile)
    previous_day = "Monday"  # Assume the previous day is Monday
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
        profile_window.geometry("500x400")
        profile_window.configure(bg="#e6f7d1")
        profile_window.resizable(True, True)
        
        user_name = user_profile.get("name")
        if user_name is None:
            user_name = "User"
        tk.Label(profile_window, text=f"Hello {user_name}!", font=("Arial", 20, "bold"), bg="#e6f7d1").pack(pady=10)

        details_frame = tk.Frame(profile_window, bg="#e6f7d1")
        details_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        details = [
            ("Age", user_profile.get("age")),
            ("Gender", user_profile.get("gender")),
            ("Height", user_profile.get("height")),
            ("Weight", user_profile.get("weight")),
            ("Fitness Goal", user_profile.get("fitness goal")),
            ("Dietary Preference", user_profile.get("dietary preference")),
            ("Physical Activity Level", user_profile.get("current physical activity levels")),
            ("Health Restrictions", user_profile.get("health restrictions")),
            ("Dietary Restrictions", user_profile.get("dietary restrictions")),
        ]
        
        for i, (label, value) in enumerate(details):
            if value is None:
                value = "You haven't enter this information"
            tk.Label(details_frame, 
                     text=f"{label}:", 
                     font=("Arial", 13), 
                     anchor="w", 
                     bg="#e6f7d1").grid(row=i, column=0, sticky="w", pady=5)
            value_label = tk.Label(details_frame, 
                     text=f"{value}", 
                     font=("Arial", 13),
                     bg="#e6f7d1",
                     wraplength=300,
                     justify="left")
            value_label.grid(row=i, column=1, sticky="w", pady=5)
        
####### End of User Profile ######### 
#####################################                            

def show_plan(table_data, title):
    plan_window = tk.Toplevel(root)
    plan_window.title(title)
    
    plan_window.geometry("1200x800")
    plan_window.configure(bg="#f0f4f7")
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
    
    # Header row: Morning, Noon, Evening
    header_frame = tk.Frame(frame, bg="#6ba96b")
    header_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")
    
    
    empty_label = tk.Label(
    header_frame,
    text="",  # Empty for alignment
    font=("Arial", 18, "bold"),
    bg="#6ba96b",
    fg="white",
    relief="solid",
    borderwidth=1,
    width=10,
    )
    empty_label.grid(row=0, column=0, sticky="nsew")
    
    # Column headers
    frame.grid_columnconfigure(0, weight=0)  # First column has fixed width
    header_frame.grid_columnconfigure(0, weight=0)  # First column of the header has fixed width
    
    
    for i, time_of_day in enumerate(["Morning", "Noon", "Evening"]):
        label = tk.Label(
            header_frame, 
            text=time_of_day, 
            font=("Arial", 18, "bold"), 
            bg="#6ba96b",
            fg="white",
            justify="center",
            wraplength=250,
            relief="solid",
            borderwidth=1
            )
        label.grid(row=0, column=i + 1, sticky="nsew")
        
    colors = ["#d9ead3", "#b6d7a8"]
    for row_i, day in enumerate(table_data.keys()):
        day_label = tk.Label(
            frame,
            text=day, 
            font=("Arial", 18, "bold"), 
            bg="#556b2f", 
            fg="white",
            anchor="center",
            relief="solid",
            borderwidth=1,
            width=10)   
        day_label.grid(row=row_i+1, column=0, sticky="nsew")
        
        for col_i, time_of_day in enumerate(["Morning", "Noon", "Evening"]):
            bg_color = colors[(row_i+col_i) % 2]
            data = table_data[day][time_of_day]
            label = tk.Label(
                frame, 
                text=data, 
                font=("Arial", 12), 
                bg=bg_color, 
                anchor="w", 
                wraplength=250, 
                justify="left",
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=10)
            label.grid(row=row_i+1, column=col_i+1, sticky="nsew")
    
    total_columns = 4
    total_rows = len(table_data) + 1
    for i in range(1,total_columns):
        frame.grid_columnconfigure(i, weight=3, uniform="columns")
        header_frame.grid_columnconfigure(i, weight=3, uniform="columns")
    for i in range(total_rows):
        frame.grid_rowconfigure(i, weight=1)
        
    return plan_window
     

def prepare_table_data(diet_plan=None, fitness_plan=None, combined_timetable=None):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    table = {day: {"Morning": "", "Noon": "", "Evening": ""} for day in days}
        
    for day in days:
        for time_of_day in ["Morning", "Noon", "Evening"]:
            table[day][time_of_day] = ""
            
            # Process diet plan
            if diet_plan and day in diet_plan and time_of_day in diet_plan[day]:
                diet_items = diet_plan[day][time_of_day]
                if diet_items:
                    if isinstance(diet_items, str):
                        # diet_items is a string
                        table[day][time_of_day] += diet_items + "\n"
                    elif isinstance(diet_items, list):
                        # diet_items is a list
                        for item in diet_items:
                            name, *details = item.split(":")
                            details_text = ":".join(details).strip()
                            table[day][time_of_day] += f"**{name.strip()}**\n{details_text}\n\n"
                    else:
                        # diet_items is of an unexpected type
                        pass

            # Process fitness plan
            if fitness_plan and day in fitness_plan and time_of_day in fitness_plan[day]:
                exercise_items = fitness_plan[day][time_of_day]
                if exercise_items:
                    if isinstance(exercise_items, str):
                        # exercise_items is a string (e.g., "Relax day")
                        table[day][time_of_day] += exercise_items + "\n"
                    elif isinstance(exercise_items, list):
                        # exercise_items is a list
                        for item in exercise_items:
                            if isinstance(item, dict):
                                # Extract details from dictionary
                                name = item.get("Exercise", "Unknown")
                                details = [
                                    f"{key}: {value}"
                                    for key, value in item.items()
                                    if key != "Exercise"
                                ]
                                details_text = "\n".join(details)
                                table[day][time_of_day] += f"**{name}**\n{details_text}\n\n"
                            else:
                                # Fallback for string-based exercises
                                name, *details = item.split(", ")
                                details_text = "\n".join(details)
                                table[day][time_of_day] += f"**{name}**\n{details_text}\n\n"
                    else:
                        # exercise_items is of an unexpected type
                        pass

            # Process combined timetable
            if combined_timetable and day in combined_timetable and time_of_day in combined_timetable[day]:
                combined_items = combined_timetable[day][time_of_day]
                if combined_items:
                    # Process diet items
                    diet_items = combined_items.get("Diet", [])
                    if diet_items:
                        if isinstance(diet_items, str):
                            table[day][time_of_day] += diet_items + "\n"
                        elif isinstance(diet_items, list):
                            for item in diet_items:
                                name, *details = item.split(":")
                                details_text = ": ".join(details).strip() if details else ""
                                table[day][time_of_day] += f"**{name.strip()}**\n{details_text}\n\n"
                        else:
                            pass  # Unexpected type

                    # Process fitness items
                    exercise_items = combined_items.get("Fitness", [])
                    if exercise_items:
                        if isinstance(exercise_items, str):
                            table[day][time_of_day] += exercise_items + "\n"
                        elif isinstance(exercise_items, list):
                            for item in exercise_items:
                                if isinstance(item, dict):
                                    name = item.get("Exercise", "Unknown")
                                    details = [
                                        f"{key}: {value}"
                                        for key, value in item.items()
                                        if key != "Exercise"
                                    ]
                                    details_text = "\n".join(details)
                                    table[day][time_of_day] += f"**{name}**\n{details_text}\n\n"
                                else:
                                    name, *details = item.split(", ")
                                    details_text = "\n".join(details)
                                    table[day][time_of_day] += f"**{name}**\n{details_text}\n\n"
                        else:
                            pass  # Unexpected type
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
        menu_button.grid(row=0, column=0, sticky="w", padx=10, pady=10)
    else:
        slide_menu.grid()
        menu_button.grid(row=0, column=1, sticky="w", padx=10, pady=10)

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

menu_button_style = {"font": ("Arial", 12), "bg": "#6b8e23", "fg": "white", "relief": "raised", "bd": 2}
tk.Button(slide_menu, text="My Diet", **menu_button_style, command=show_diet_plan).pack(pady=15, padx=10, fill="x")
tk.Button(slide_menu, text="My Fitness", **menu_button_style, command=show_fitness_plan).pack(pady=15, padx=10, fill="x")
tk.Button(slide_menu, text="My Timetable", **menu_button_style, command=show_timetable).pack(pady=15, padx=10, fill="x")

# Header and toggle button
header = tk.Frame(root, bg="#e6f7d1")
header.grid(row=0, column=1, sticky="ew")

menu_button = tk.Button(root, text="☰", font=("Arial", 15, "bold"), bg="#e6f7d1", relief="flat", command=toggle_menu)
menu_button.grid(row=0, column=0, sticky="w", padx=10, pady=10)

# Main chat frame
chat_frame = tk.Frame(root, bg="#e6f7d1", padx=20, pady=20)
chat_frame.grid(row=1, column=1, sticky="nsew")
chat_frame.grid_rowconfigure(0, weight=0)  
chat_frame.grid_rowconfigure(1, weight=1)
chat_frame.grid_rowconfigure(2, weight=0)
#chat_frame.grid_rowconfigure(3, weight=0)
chat_frame.grid_columnconfigure(0, weight=1)
chat_frame.grid_columnconfigure(1, weight=0)  

# welcome message
welcome_label = tk.Label(chat_frame, text="Welcome to Healthify!", font=("Arial", 20), bg="#e6f7d1", fg="#6ba96b")
welcome_label.grid(row=0, column=0, pady=10, columnspan=2)

# chat display
chat_display = tk.Text(chat_frame, wrap=tk.WORD, height=20, width=70, state="disabled", bg="#f7f7f7", fg="black", font=("Arial", 15), relief="groove", bd=2)
chat_display.grid(row=1, column=0, sticky="nsew", pady=10, columnspan=2)

# Input box for chat
chat_input = tk.Text(chat_frame, height=1, width=70, bg="white", fg="black", font=("Helvetica", 15))
chat_input.grid(row=2, column=0, sticky="ew", pady=10)

def handle_enter(event):
    handle_chat()
    return "break"

chat_input.bind("<Return>", handle_enter)

def process_recommendations(training_rec, dietary_rec, day=None, previous_day=None, calories_week=None):
    global diet_plan, fitness_plan, combined_plan

    # Plan adjustment based on previous day
    user_id = 43
    columns, rows = fetch_user_data(user_id)
    print(rows)
    diet_plan_raw = generate_diet_plan(day, dietary_rec, columns, rows)
    
    # Determine day_index based on the day
    day_indices = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    day_index = day_indices.get(day, 0)  # Default to 0 if day is not found

    fitness_plan_raw = generate_fitness_plan(day, training_rec, day_index, columns, rows, diet_plan_raw)
    
    adjusted_exercise_plan, adjusted_diet_plan = adjust_daily_progress(
        day,
        previous_day,
        calories_week,
        diet_plan_raw,
        fitness_plan_raw,
        columns,
        rows,
        dietary_rec,
        training_rec
    )

    # Update the global plans with adjusted plans for the day
    diet_plan[day] = adjusted_diet_plan
    fitness_plan[day] = adjusted_exercise_plan
    combined_plan[day] = combine_plan(adjusted_diet_plan, adjusted_exercise_plan)

    # Display the adjusted plans
    chat_display.config(state="normal")
    #chat_display.insert(tk.END, f"\nAssistant: Here is your adjusted plan for {day}:\n")    
    chat_display.insert(tk.END, f"Diet Plan for {day} is complete. \n")
    chat_display.insert(tk.END, f"Fitness Plan for {day} is complete. \n")
    chat_display.see(tk.END)
    chat_display.config(state="disabled")


# Send button
send_button = tk.Button(chat_frame, text="Send", font=("Helvetica", 12), bg="#6ba96b", fg="white", command=lambda: process_chat())
send_button.grid(row=2, column=1, pady=5, padx=5, sticky="e")

def process_chat():
    handle_chat()

# Profile button
profile_button = tk.Button(
    root, 
    text="My Profile", 
    font=("Arial", 12), 
    bg="#6b8e23", 
    fg="white", 
    command=show_profile,
    relief="raised",
    bd=2
    
    )
profile_button.grid(row=2, column=0, pady=15, padx=15, sticky="sw")

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


current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "user_profiles.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the user_profiles table if it does not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    height INTEGER,
    weight INTEGER,
    fitness_goal TEXT,
    dietary_preference TEXT,
    physical_activity_level TEXT,
    health_restrictions TEXT,
    dietary_restrictions TEXT
)''')

# Add the user profile to the database
cursor.execute('''
INSERT INTO user_profiles (
    name, age, gender, height, weight, fitness_goal, dietary_preference,
    physical_activity_level, health_restrictions, dietary_restrictions
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    user_profile['name'], user_profile['age'], user_profile['gender'], user_profile['height'], 
    user_profile['weight'], user_profile['fitness goal'], user_profile['dietary preference'],
    user_profile['current physical activity levels'], user_profile['health restrictions'],
    user_profile['dietary restrictions']
))

# Commit and close the connection
conn.commit()
conn.close()