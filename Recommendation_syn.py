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
        You are a diet planner AI. Using the following provided daily food choices, create a balanced diet plan for {day}.
        Each meal must include:
        - A combination of items (at least 2 for Morning, and at least 3 for Noon and Evening).
        - Each food combination must be provided in the strict format: "Name: Cooking instructions".
        - Replace "Name" with the actual food name or combination (e.g., "Salmon Salad").
        - "Cooking instructions" should describe the steps to prepare the meal, including the cooking method, key ingredients, and any important preparation details.

        Ensure that:
        - The combinations are varied and nutritionally balanced.
        - The instructions are simple enough for a home cook.
        - The format strictly adheres to JSON, without any code fences, explanations, or additional text.

        Example Output:
        {{
          "Morning": [
            "Salmon Scramble: Pan-fry diced salmon with eggs, season with salt and pepper.",
            "Quinoa Porridge: Cook quinoa in water, top with almonds and a drizzle of honey."
          ],
          "Noon": [
            "Grilled Chicken Salad: Mix grilled chicken slices with fresh greens, drizzle with olive oil.",
            "Brown Rice with Steamed Vegetables: Steam broccoli and carrots, serve with cooked brown rice."
          ],
          "Evening": [
            "Baked Salmon: Season salmon with olive oil, bake at 375°F for 15 minutes.",
            "Quinoa-Stuffed Bell Peppers: Fill bell peppers with cooked quinoa and bake."
          ]
        }}

        Using the provided daily food choices below, generate the JSON output for {day}:

        {json.dumps(diet_data, indent=2)}
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
    You are a fitness trainer AI. Create a weekly fitness plan with the following requirements:

    1. Each day has:
    - Morning: At least 2 exercises.
    - Evening: At least 2 exercises.

    2. Format the output strictly as:
    {{
        "Monday": {{
            "Morning": ["Exercise Name: Repetition: X, Duration: Y", "Exercise Name: Repetition: X, Duration: Y"],
            "Evening": ["Exercise Name: Repetition: X, Duration: Y", "Exercise Name: Repetition: X, Duration: Y"]
        }},
        ...
        "Sunday": {{
            "Morning": ["Exercise Name: Repetition: X, Duration: Y", "Exercise Name: Repetition: X, Duration: Y"],
            "Evening": ["Exercise Name: Repetition: X, Duration: Y", "Exercise Name: Repetition: X, Duration: Y"]
        }}
    }}

    Example Data:
    {json.dumps(fitness_data, indent=2)}

    Rules:
    - Use the format above exactly.
    - No explanations, extra text, or code fences.
    - Ensure variety, balance, and intensity.

    Output only as a JSON object.
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