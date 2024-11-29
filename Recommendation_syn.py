import os
from openai import OpenAI
import json
import pandas as pd


client = OpenAI(
    api_key = os.getenv('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'),
)

def generate_diet_plan(day, diet_data):
    prompt = f"""
        You are a diet planner AI. Using the following provided daily food choices, create a balanced diet plan for {day}.
        Each meal must include:
        - A combination of items (at least 2 for Morning, and at least 3 for Noon and Evening).
        - Each food combination must be provided in the strict format: "Name: Cooking instructions".
        - Replace "Name" with the actual food name or combination (e.g., "Salmon Salad").
        - Total amount of Calories should not exceed 2500 for the day.
        - "Cooking instructions" should describe the steps to prepare the meal, including the cooking method, key ingredients, and any important preparation details.
        - Total amount of Calories for that meal in the format "Calories: X". 

        Ensure that:
        - The combinations are varied and nutritionally balanced.
        - One recipe should only appear once in the plan.
        - The recipe must be distinct from the previous day's plan.
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
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        max_tokens = 1000,
        temperature = 0.7,
        messages = [
            {"role": "system", "content": "You are an assistant that generates daily diet plans."},
            {"role": "user", "content": prompt}
        ]
    )
                
    response_content = response.choices[0].message.content.strip()
    diet_plan = parse_json(response_content)

    return diet_plan
        
        
def generate_fitness_plan(day, fitness_data):
    prompt = f"""
    You are a fitness trainer AI. Create a fitness plan for {day} with the following requirements:

    1. Each day has:
    - Morning: 2 exercises.
    - Evening: 2 exercises.

    2. One weak has two rest days with no exercises (Thursday and Sunday).

    3. The Duration should add second after the number (e.g., "Duration: 10 seconds").

    4. Example Output:
    {{
        
        "Morning": ["Dumbbell Spell Caster: Repetition: X, Duration: Y", "Cable Russian: Repetition: X, Duration: Y"],
        "Evening": ["Cable Reverse: Repetition: X, Duration: Y", "30-Minute Run: Repetition: X, Duration: Y"]

    }}

    Example Data:
    {json.dumps(fitness_data, indent=2)}

    Rules:
    - Use the example above, and follow the same format.
    - No explanations, extra text, or code fences.
    - Ensure variety, balance, and intensity.

    Output only as a JSON object.
    """
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        max_tokens = 1000,
        temperature = 0.7,
        messages = [
            {"role": "system", "content": "You are an assistant that generates weekly fitness plans."},
            {"role": "user", "content": prompt}
        ]
    )
    #print("RAW RESPONSE:", response)
      
    response_content = response.choices[0].message.content.strip()
    exercise_plan = parse_json(response_content)

    return exercise_plan
        
        
def adjust_daily_progress(day, previous_day, calories_week, diet_plan, fitness_plan):
    """
    Analyzes whether the daily exercise is sufficient based on consumption and intake.
    Adjusts the exercise plan.
    """
    if not calories_week or not previous_day:
        return fitness_plan, diet_plan
    
    consumption_calories = calories_week[previous_day]["Calorie intake"]
    burned_calories = calories_week[previous_day]["calories burned (exercise)"]

    prompt = f"""
    You are a fitness and nutrition expert AI.

    The user has consumed {consumption_calories} calories on {previous_day} and has burned {burned_calories} calories through exercise.

    Based on the user's goal to maintain a healthy lifestyle, adjust the curent exercise plan and diet plan.

    One weak has two rest days with no exercises (Thursday and Sunday). 

    If you decide that the previous day's Calorie consumption is not up to standard, you can add additional cardio (such as run, swim and soon) to the today's exercise plan to burn more calories, and reduce the intake of up to 200 calories in the diet plan.

    If you decide that the previous day's Calorie consumption is too high, you can add more strength training exercises to the today's exercise plan to build muscle and increase metabolism, and increase the intake of up to 200 calories in the diet plan.

    If you decide that the previous day's Calorie consumption is just right, adjusted exercise plan and diet plan can keep the exercise and diet plan as current exercise plan and diet plan.


    Current Exercise Plan for {day}:
    {json.dumps(fitness_plan, indent=2)}

    Current Diet Plan for {day}:
    {json.dumps(diet_plan, indent=2)}

    Output the adjusted exercise plan and diet plan in JSON format, following the same structure as the current plans, in the following format:
    
    The output should be in the following format:
    {{
        "exercise_plan":{{
        "Morning": ["Exercise Name: Repetition: X, Duration: Y seconds", "Exercise Name: Repetition: X, Duration: Y seconds"],
        "Evening": ["Exercise Name: Repetition: X, Duration: Y seconds", "Exercise Name: Repetition: X, Duration: Y seconds"]
        }},
        "diet_plan":{{
          "Morning": [
            "Salmon Scramble: Pan-fry diced salmon with eggs, season with salt and pepper. Calories: X.",
            "Quinoa Porridge: Cook quinoa in water, top with almonds and a drizzle of honey. Calories: Y."
          ],
          "Noon": [
            "Grilled Chicken Salad: Mix grilled chicken slices with fresh greens, drizzle with olive oil. Calories: X.",
            "Brown Rice with Steamed Vegetables: Steam broccoli and carrots, serve with cooked brown rice. Calories: Y."
          ],
          "Evening": [
            "Baked Salmon: Season salmon with olive oil, bake at 375°F for 15 minutes. Calories: X.",
            "Quinoa-Stuffed Bell Peppers: Fill bell peppers with cooked quinoa and bake. Calories: Y."
          ]
        }}
    }}

    **Do not include any explanations, comments, or additional text. Your entire response should be the JSON object only.**

    """

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        max_tokens = 1000,
         temperature = 0.7,
        messages = [
            {"role": "system", "content": "You are an assistant that adjusts daily exercise plans."},
            {"role": "user", "content": prompt}
        ]
    )

    response_content = response.choices[0].message.content.strip()
    adjusted_plans = parse_json(response_content)
    adjusted_exercise_plan = adjusted_plans.get('exercise_plan', fitness_plan)
    adjusted_diet_plan = adjusted_plans.get('diet_plan', diet_plan)
    return adjusted_exercise_plan, adjusted_diet_plan

def combine_plan(diet_plan, fitness_plan):
    combined_plan = {}
    days = set(diet_plan.keys()).union(set(fitness_plan.keys()))
    for day in days:
        combined_plan[day] = {
            "Diet": diet_plan.get(day, {}),
            "Fitness": fitness_plan.get(day, {}),
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
    json_str = json_str.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    return json.loads(json_str.strip())
