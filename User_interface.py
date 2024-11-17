import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import User_profile
from Recommendation_syn import diet_data, fitness_data, generate_diet_plan, generate_fitness_plan, combine_plan, to_dataframe
import json
import pandas as pd
from openai import OpenAI
import os


client = OpenAI(
    api_key = os.getenv('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'),
)

diet_plan = generate_diet_plan(diet_data)
fitness_plan = generate_fitness_plan(fitness_data)
combined_plan = combine_plan(diet_plan, fitness_plan)
df_diet = to_dataframe(diet_plan, plan_type="Diet")
df_fitness = to_dataframe(fitness_plan, plan_type="Fitness")
df_combined = to_dataframe(combined_plan)

print("diet plan")
print(diet_plan)


messages = [
        {"role": "system", 
         "content":
            "You are a friendly fitness assistant, responsible for having a natural conversation with the user,"
            "Gradually collect the following information: name, age, gender, weight, fitness goals,"
            "Current physical activity levels, health restrictions, and dietary preferences."
            "Ask one question at a time and respond appropriately based on the user's answers."
        }
]

user_profile = {}

info_keys = {
        "name": "name",
        "age": "age",
        "gender": "gender",
        "weight": "weight",
        "fitness goal": "fitness goal",
        "current physical activity levels": "current physical activity levels",
        "health restrictions": "health restrictions",
        "dietary preferences": "dietary preferences"  
    }

collected_keys = set()


def start_chat():
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
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

def handle_chat():
    user_input = chat_input.get("1.0", tk.END).strip()
    if not user_input:
        return
    chat_input.delete("1.0", tk.END)
    messages.append({"role": "user", "content": user_input})
    
    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"You: {user_input}\n")
    chat_display.see(tk.END)
    chat_display.config(state="disabled")
    
    extraction_prompt = (
        "As an AI assistant, extract any personal information provided from the user's response below. "
        "Include the following keys exactly as specified: "
        "'name', 'age', 'gender', 'weight', 'fitness goal', "
        "'current physical activity levels', 'health restrictions', 'dietary preferences'. "
        "Please output the new information in JSON format, without explanation or additional text. "
        "If a piece of information is not provided, do not include it in the JSON."
        "\n\nUser's reply:\n"
        f"\"\"\"\n{user_input}\n\"\"\""
    )
    
    extraction_response = client.chat.completions.create(
            model = "gpt-4o",
            messages=[
                {"role": "system", "content": extraction_prompt}
            ],
            max_tokens= 150,
            temperature= 0,
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
    
    if len(collected_keys) == len(info_keys):
        chat_display.config(state="normal")
        chat_display.insert(tk.END, "Assistant: All information collected.\n")
        chat_display.see(tk.END)
        chat_display.config(state="disabled")
        
        #proceed to generate diet and fitness plan
        return
    
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        max_tokens = 150,
        temperature = 0.7,
    )
    
    assitant_message = response.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": assitant_message})
    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"Assistant: {assitant_message}\n")
    chat_display.see(tk.END)
    chat_display.config(state="disabled")

        
def show_profile():
    profile_window = tk.Toplevel(root)
    profile_window.title("Profile")
    profile_window.geometry("400x400")
    tk.Label(profile_window, text="Your Profile", font=("Helvetica", 16)).pack(pady=10)
    profile_display = tk.Text(profile_window, wrap=tk.WORD, height=15, width=50)
    profile_display.insert(tk.END, json.dumps(user_profile, indent=2))
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
        label = tk.Label(frame, text=time_of_day, font=("Helvetica", 12), width=10, anchor="w", bg="#556b2f")
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
        if combined_timetable:
            if "Diet" in combined_timetable[day]:
                morning_diet = combined_timetable[day]["Diet"].get("Morning", [])
                noon_diet = combined_timetable[day]["Diet"].get("Noon", [])
                evening_diet = combined_timetable[day]["Diet"].get("Evening", [])
                table[day]["Morning"] += f"Foods: {','.join(morning_diet)}\n"
                table[day]["Noon"] += f"Foods: {','.join(noon_diet)}\n"
                table[day]["Evening"] += f"Foods: {','.join(evening_diet)}\n"
                
            if "Fitness" in combined_timetable[day]:
                morning_exercises = combined_timetable[day]["Fitness"].get("Morning", "")
                evening_exercises = combined_timetable[day]["Fitness"].get("Evening", "")
                table[day]["Morning"] += f"Exercises: {morning_exercises}\n"
                table[day]["Evening"] += f"Exercises: {evening_exercises}\n"
        
        elif diet_plan or fitness_plan:
            if diet_plan:
                meals = diet_plan.get(day, {})
                morning_diet = meals.get("Morning", [])
                noon_diet = meals.get("Noon", [])
                evening_diet = meals.get("Evening", [])
                table[day]["Morning"] += f"Foods: {','.join(morning_diet)}\n"
                table[day]["Noon"] += f"Foods: {','.join(noon_diet)}\n"
                table[day]["Evening"] += f"Foods: {','.join(evening_diet)}\n"
                
            if fitness_plan:
                exercises = fitness_plan.get(day, {})
                morning_exercises = exercises.get("Morning", "")
                evening_exercises = exercises.get("Evening", "")
                table[day]["Morning"] += f"Exercises: {','.join(morning_exercises)}\n"
                table[day]["Evening"] += f"Exercises: {','.join(evening_exercises)}\n"
                
        
        
        
        
        
        """table[day]["Morning"] = ""
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
            """


                
                        
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
root.configure(bg="#f3f4e9")


root.grid_rowconfigure(1, weight=1) 
root.grid_columnconfigure(1, weight=1)  


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
chat_frame.grid_rowconfigure(0, weight=0)  
chat_frame.grid_rowconfigure(1, weight=1)
chat_frame.grid_rowconfigure(2, weight=0)
chat_frame.grid_rowconfigure(3, weight=0)
chat_frame.grid_columnconfigure(0, weight=1)  

# welcome message
welcome_label = tk.Label(chat_frame, text="Welcome to Healthify!", font=("Helvetica", 20), bg="#f3f4e9", fg="#556b2f")
welcome_label.grid(row=0, column=0, pady=10)

# chat display
chat_display = tk.Text(chat_frame, wrap=tk.WORD, height=20, width=70, state="disabled", bg="#f7f7f7", fg="black", font=("Helvetica", 15))
chat_display.grid(row=1, column=0, sticky="nsew", pady=10)

# Input bot for chat
chat_input = tk.Text(chat_frame, height=3, width=70, bg="white", fg="black", font=("Helvetica", 15))
chat_input.grid(row=2, column=0, sticky="ew", pady=10)

def handle_enter(event):
    handle_chat()
    return "break"
chat_input.bind("<Return>", handle_enter)

# sent button
send_button = tk.Button(chat_frame, text="Send", font=("Helvetica", 12), bg="#556b2f", fg="white", command=handle_chat)
send_button.grid(row=3, column=0, pady=10)

# profile button
profile_button = tk.Button(root, text="My Profile", font=("Helvetica", 12), bg="#556b2f", fg="white", command=show_profile)
profile_button.grid(row=2, column=0, pady=10, sticky="sw")


root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)


# Start the chat
start_chat()

# Run the application
root.mainloop()