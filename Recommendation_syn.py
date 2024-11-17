import os
from openai import OpenAI
import json
import pandas as pd


client = OpenAI(
    api_key = os.getenv('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'),
)

diet_data = {
    "Name": "Jack",
    "BMI": 24.69,
    "TDEE": 2500,
    "Daily Food Choices_1": [
        {"name": "Fish, raw, chinook, salmon", "weight": "200g"},
        {"name": "Nuts, almonds", "weight": "50g"},
        {"name": "Quinoa, uncooked", "weight": "100g"},
        {"name": "Edamame, prepared, frozen", "weight": "150g"},
        {"name": "Yogurt, nonfat, plain, Greek", "weight": "200g"}
    ],
    "Daily Food Choices_2": [
        {"name": "Game meat, raw, wild, boar", "weight": "200g"},
        {"name": "Nuts, raw, pistachio nuts", "weight": "50g"},
        {"name": "Buckwheat", "weight": "100g"},
        {"name": "Tempeh", "weight": "150g"},
        {"name": "Soybeans, raw, mature seeds", "weight": "100g"}
    ],
    "Daily Food Choices_3": [
        {"name": "Fish, raw, wild, coho, salmon", "weight": "200g"},
        {"name": "Nuts, dried, black, walnuts", "weight": "50g"},
        {"name": "Lentils, raw", "weight": "100g"},
        {"name": "Tofu, fried", "weight": "150g"},
        {"name": "Oats", "weight": "100g"}
    ],
    "Daily Food Choices_4": [
        {"name": "Pheasant, meat and skin, raw", "weight": "200g"},
        {"name": "Nuts, hazelnuts or filberts", "weight": "50g"},
        {"name": "Millet, raw", "weight": "100g"},
        {"name": "Tempeh, cooked", "weight": "150g"},
        {"name": "Soy flour, roasted, full-fat", "weight": "100g"}
    ],
    "Daily Food Choices_5": [
        {"name": "Fish, raw, carp", "weight": "200g"},
        {"name": "Seeds, paste, sesame butter", "weight": "50g"},
        {"name": "Barley, hulled", "weight": "100g"},
        {"name": "Natto", "weight": "150g"},
        {"name": "Wheat germ, crude", "weight": "100g"}
    ]
}

fitness_data = {
    "Name": "Jack",
    "Exercise Choices_1": {
        "Title": "Barbell Side Bend",
        "Description": "This exercise targets the abdominals, specifically the obliques, using a barbell.",
        "Repetitions": 8,
        "Sets": 2,
        "Rest_time": "60 seconds between sets"
    },
    "Exercise Choices_2": {
        "Title": "Kettlebell Pass Between The Legs",
        "Description": "This exercise gives an all-around abdominal workout and enhances coordination.",
        "Repetitions": 17,
        "Sets": 2,
        "Rest_time": "60 seconds between sets"
    },
    "Exercise Choices_3": {
        "Title": "Cable reverse crunch",
        "Description": "Targets the lower abdominals specifically using a cable machine.",
        "Repetitions": 14,
        "Sets": 2,
        "Rest_time": "60 seconds between sets"
    },
    "Exercise Choices_4": {
        "Title": "Dumbbell spell caster",
        "Description": "A comprehensive exercise working abs, shoulders, back, hips, and legs in a coordinated motion.",
        "Repetitions": 12,
        "Sets": 2,
        "Rest_time": "60 seconds between sets"
    },
    "Exercise Choices_5": {
        "Title": "Plate Twist",
        "Description": "This exercise enhances core strength and targets the obliques.",
        "Repetitions": 16,
        "Sets": 2,
        "Rest_time": "60 seconds between sets"
    }
}

    

def generate_diet_plan(diet_data):
    diet_plan = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        prompt = f"""
        You are a diet planner AI. Using the following provided daily food choices, create a balanced diet plan for {day}. Each meal must include detailed cooking instructions for the user.
        The plan must have:
        - Morning: A combination of items (at least 2). Format: "Name: cooking instructions".
        - Noon: A combination of items (at least 3). Format: "Name: cooking instructions".
        - Evening: A combination of items (at least 3). Format: "Name: cooking instructions".

        Example Data:
        {json.dumps(diet_data, indent=2)}

        Ensure that the combinations are varied, nutritionally balanced, and simple enough for a home cook. The instructions should include the cooking method, key ingredients, and steps to prepare the meal. Return the output as a JSON object only, without any code fences, explanations, or additional text. The JSON object should have "Morning", "Noon", and "Evening" as keys with their respective food combinations and cooking instructions for {day}.
        """
        try:
            response = client.chat.completions.create(
                model = "gpt-3.5-turbo",
                max_tokens = 1000,
                temperature = 0.7,
                messages = [
                    {"role": "system", "content": "You are an assistant that generates daily diet plans."},
                    {"role": "user", "content": prompt}
                ]
            )
                
            response_content = response.choices[0].message.content.strip()
            day_plan = parse_json(response_content)
            diet_plan[day] = day_plan

        except Exception as e:
                print(f"An error occurred in diet generation: {e}")
                diet_plan[day] = {}
    return diet_plan
        
        
def generate_fitness_plan(fitness_data):
    prompt = f"""
    You are a fitness trainer AI. Using the following provided exercise choices, create a weekly fitness plan. And rememeber to give the user instructions on how to perform the exercises (repetition and duration).
    Each day must have:
    - Morning: A combination of exercises (at least two).
    - Evening: A combination of exercises (at least two).

    Example Data:
    {json.dumps(fitness_data, indent=2)}

    Ensure that each day's combinations are varied and balanced and must be sufficiently intense. Return the output as a JSON object where each key is a day of the week, and the value contains "Morning" and "Evening" with their respective exercise combinations.
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
    """data = []
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
                })  """
                
                
    data = []
    for day, activities in plan.items():
        if plan_type == "Diet":
            if isinstance(activities, list):
                meals = ";".join(activities)
                data.append({"Day": day, "Diet": meals})
            else:
                data.append({
                    "Day": day, 
                    "Morning": activities.get("Morning", ""),
                    "Noon": activities.get("Noon", ""),
                    "Evening": activities.get("Evening", "")
                    })
        elif plan_type == "Fitness":
            if isinstance(activities, list):
                exercises = ";".join(activities)
                data.append({"Day": day, "Fitness": exercises})
            else:
                data.append({
                    "Day": day,
                    "Morning": activities.get("Morning", ""),
                    "Evening": activities.get("Evening", "")
                    })
        else:
            meals = activities.get("Diet", {})
            exercises = activities.get("Fitness", {})
            if isinstance(meals, list):
                diet_str = ";".join(meals)
            else:
                diet_str = f"Morning: {meals.get('Morning', '')}, Noon: {meals.get('Noon', '')}, Evening: {meals.get('Evening', '')}"
            if isinstance(exercises, list):
                exercises_str = ";".join(exercises)
            else:
                exercises_str = f"Morning: {exercises.get('Morning', '')}, Evening: {exercises.get('Evening', '')}"
            data.append({
                "Day": day,
                "Diet": diet_str,
                "Fitness": exercises_str
                })
    return pd.DataFrame(data)


def parse_json(json_str):
    try:
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        return json.loads(json_str.strip())
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {}

diet_plan = generate_diet_plan(diet_data)
fitness_plan = generate_fitness_plan(fitness_data)
combined_plan = combine_plan(diet_plan, fitness_plan)

df_combined = to_dataframe(combined_plan)
df_diet = to_dataframe(diet_plan, "Diet")
df_fitness = to_dataframe(fitness_plan, "Fitness")

print(df_diet)