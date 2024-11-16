import os
from openai import OpenAI
import json
import pandas as pd


client = OpenAI(
    api_key = os.getenv('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'),
)


def simulate_diet():
    return [
        "Chicken breast", "Salmon", "Quinoa", "Brown rice", "Broccoli",
        "Eggs", "Greek yogurt", "Avocado", "Spinach", "Almonds"
    ]
    
def simulate_fitness():
    return [
        "Push-ups", "Squats", "Deadlifts", "Pull-ups", "Plank",
        "Jogging", "Cycling", "Swimming", "Yoga", "HIIT Workout"
    ]
    

def generate_diet_plan(diet_list):
    prompt = f"""
    You are a diet planner AI. Given the following foods, create a weekly diet plan (Monday to Sunday) for a user who wants to gain muscle or loss weight.

    Foods:
    {', '.join(diet_list)}

    For each day, assign three meals (breakfast, lunch, dinner) using the foods provided. Ensure variety and balance across the week.

    Return the output as a JSON object where each key is a day of the week, and the value is a list of three meals.
    """
    try:
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            max_tokens = 1000,
            temperature = 0.7,
            messages = [
                {"role": "system", "content": "You are an assistant that generates weekly diet plans."},
                {"role": "user", "content": prompt}
            ]
        )
        #print("RAW RESPONSE:", response)
        if not response.choices or not response.choices[0].message.content.strip():
                raise ValueError("Empty or invalid response from API")
            
        response_content = response.choices[0].message.content.strip()
        return parse_json(response_content)

    except Exception as e:
            print(f"An error occurred in diet generation: {e}")
            return {}
        
        
def generate_fitness_plan(fitness_list):
    prompt = f"""
    You are a fitness trainer AI. Given the following exercises, create a weekly fitness plan (Monday to Sunday) for a user who wants to gain muscle or loss weight.

    Exercises:
    {', '.join(fitness_list)}

    For each day, assign one exercise from the list provided. Ensure variety and balance across the week.

    Return the output as a JSON object where each key is a day of the week, and the value is an exercise.
    """
    try:
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            max_tokens = 1000,
            temperature = 0.7,
            messages = [
                {"role": "system", "content": "You are an assistant that generates weekly fitness plans."},
                {"role": "user", "content": prompt}
            ]
        )
        #print("RAW RESPONSE:", response)
        if not response.choices or not response.choices[0].message.content.strip():
                raise ValueError("Empty or invalid response from API")
            
        response_content = response.choices[0].message.content.strip()
        return parse_json(response_content)
    except Exception as e:
            print(f"An error occurred in diet generation: {e}")
            return {}
        
        
def combine_plan(diet_plan, fitness_plan):
    combined_plan = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        combined_plan[day] = {
            "Diet": diet_plan.get(day, []),
            "Fitness": fitness_plan.get(day, []),
        }
    return combined_plan

def to_dataframe(plan, plan_type="Combined"):
    data = []
    for day, activities in plan.items():
        if plan_type == "Diet":
            meals =[]
            for meal in activities:
                if isinstance(meal, dict):
                    meal_name = meal.get("meal", "Meal")
                    food = ", ".join(meal.get("foods", []))
                    meals.append(f"{meal_name}: {food}")
                else:
                    meals.append(meal)
            data.append({"Day": day, "Diet": ";".join(meals)})
        elif plan_type == "Fitness":
            exercises = activities
            if isinstance(activities, list):
                exercises_str = ";".join(activities)
            else:
                exercises_str = exercises
            data.append({"Day": day, "Fitness": exercises_str})
        else:
            meals = []
            for meal in activities["Diet"]:
                if isinstance(meal, dict):
                    meal_name = meal.get("meal", "Meal")
                    food = ", ".join(meal.get("foods", []))
                    meals.append(f"{meal_name}: {food}")
                else:
                    meals.append(meal)
            diet_str = ";".join(meals)
            
            exercises = activities["Fitness"]
            if isinstance(exercises, list):
                exercises_str = ";".join(exercises)
            else:
                exercises_str = exercises
                
            data.append({
                "Day": day, 
                "Diet": diet_str, 
                "Fitness": exercises_str
                })  
    return pd.DataFrame(data)


def parse_json(json_str):
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    return json.loads(json_str.strip())

diet_list = simulate_diet()
fitness_list = simulate_fitness()

try:
    diet_plan = generate_diet_plan(diet_list)
    fitness_plan = generate_fitness_plan(fitness_list)
    combined_plan = combine_plan(diet_plan, fitness_plan)
    df_combined = to_dataframe(combined_plan)
    df_diet = to_dataframe(diet_plan, plan_type="Diet")
    df_fitness = to_dataframe(fitness_plan, plan_type="Fitness")
    print(df_combined)
except Exception as e:
    print(f"An error occurred: {e}")