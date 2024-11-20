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
print(df_diet)



######################################
############ User Profile ############
# From here to the end of handle_chat function



messages = [
        {"role": "system", 
         "content":
            "You are a friendly fitness assistant, responsible for having a natural conversation with the user,"
            "Gradually collect the following information: name, age, gender, height, weight, fitness goals,"
            "Dietary preference(Heart Health, Low Sugar, High Energy, General), Current physical activity level (low, normal, high), health restrictions, dietary restrictions."
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
        "'name', 'age', 'gender','height', 'weight', 'fitness goal', "
        "'dietary preferences', 'current physical activity level, 'health restrictions', 'dietary restrictions'. "
        "for fitness goal, mark as 'Weight Loss' if user wants to lose weight, 'Muscle Gain' if user wants to gain muscle, 'Improved Endurance' if user wants to imrpove endurance, 'Stress Relief' if user wants to relieve stress, 'Heart Health' if user wants to improve heart health, 'null' if user does not provide any information."
        "for dietary preference, mark as 'Heart Health' if user wants to improve heart health, 'Low Sugar' if user wants lower sugar intake, 'High Energy' if user wants to have high energy food, 'General', 'null' if user does not provide any information."
        #"Map dietary preferences to one of the following: 'Heart Health', 'Low Sugar', 'High Energy', or 'General'. "
        #"If the user's input is unclear, try to infer it or set it to 'unknown'. "
        #"for dietary preference,  mark as 'Heart Health' if user input is heart health, 'Low Sugar' if user input is low sugar, 'High Energy' if user input is high energy, 'General' if user doesn't have any preference."
        #"for dietary preference, mark as 'Heart Health', 'Low Sugar', 'High Energy', 'General', 'null' if user does not provide any information."
        "mark current physical activity level as low if user is newbie, normal if User has light exercise, high if user ususally do exercise."
        "for dietary restrictions, mark as 'Vegetarian', 'Vegan', 'Pescatarian', 'Gluten Free', 'Lactose Free', 'Nut Allergy', 'Shellfish Allergy', 'null' if user does not provide any information."
        "If the user indicates that he does not know or is unwilling to provide any of this information for exactly key, set the corresponding value to 'unknown'."
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
        model = "gpt-4o",
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

        
        
####### End of User Profile ######### 
#####################################
        
        
        
        
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
   
     
    

def prepare_table_data(diet_plan=None, fitness_plan=None, combined_timetable=None):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    table = {day: {"Morning": "", "Noon": "", "Evening": ""} for day in days}
        
        
    for day in days:
        table[day]["Morning"] = ""
        table[day]["Noon"] = ""
        table[day]["Evening"] = ""
        
        if diet_plan and not combined_timetable:
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
                        
        if fitness_plan and not combined_timetable:
            exercises = fitness_plan.get(day, {})
            morning_exercises = exercises.get("Morning", [])
            evening_exercises = exercises.get("Evening", [])
            morning_exercises_text = ",".join(morning_exercises)
            evening_exercises_text = ",".join(evening_exercises)
            table[day]["Morning"] += f"Exercises:\n{morning_exercises_text}\n"
            table[day]["Evening"] += f"Exercises:\n{evening_exercises_text}\n"
                
                
        if combined_timetable:
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

# Input bot for chat
chat_input = tk.Text(chat_frame, height=3, width=70, bg="white", fg="black", font=("Helvetica", 15))
chat_input.grid(row=2, column=0, sticky="ew", pady=10)

def handle_enter(event):
    handle_chat()
    return "break"
chat_input.bind("<Return>", handle_enter)

# sent button
send_button = tk.Button(chat_frame, text="Send", font=("Helvetica", 12), bg="#6ba96b", fg="white", command=handle_chat)
send_button.grid(row=3, column=0, pady=10)

# profile button
profile_button = tk.Button(
    root, 
    text="My Profile", 
    font=("Helvetica", 12), 
    bg="#6ba96b", 
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

