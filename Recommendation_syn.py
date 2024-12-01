import os
from openai import OpenAI
import json
import pandas as pd
import sqlite3

# Connect to the SQLite database
def fetch_user_data(user_id, database="user_profiles.db"):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    
    # Fetch the table structure (columns)
    cursor.execute("PRAGMA table_info(user_profiles);")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Fetch the user's data
    cursor.execute("SELECT * FROM user_profiles WHERE id = ?;", (user_id,))
    rows = cursor.fetchall()
    
    # Close the connection
    connection.close()
    
    return columns, rows

client = OpenAI(
    api_key = os.getenv('YOUR_API_KEY'),
)

def generate_diet_plan(day, diet_data, columns, rows):
    prompt = f"""
You are a diet planner AI. Using the following provided daily food choices, create a balanced diet plan for {day}.
Adjust the calorie range and macronutrient distribution according to the user's weight, height, age, and fitness goal (lose weight or gain muscle).

Get the user's weight (kg), height (cm), age (years), gender, diet preference, and health conditions based on {columns} and {rows}.

**Calculate the user's Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation:**
- For men: **BMR = 10 * weight(kg) + 6.25 * height(cm) - 5 * age(years) + 5**
- For women: **BMR = 10 * weight(kg) + 6.25 * height(cm) - 5 * age(years) - 161**

**Then calculate the Total Daily Energy Expenditure (TDEE) by multiplying the BMR with an activity factor of 1.55 (moderate exercise).**

For weight loss:
- **Total daily calories**: TDEE minus 500 calories.
- **Macronutrient distribution**: Total Fat: 20-30% of total calories; Protein: 30-40%; Carbohydrates: 30-50%.

For muscle gain:
- **Total daily calories**: TDEE plus 300-500 calories.
- **Macronutrient distribution**: Total Fat: 20-30%; Protein: 35-45%; Carbohydrates: 40-50%.

**Ensure that the total calories for all meals combined reach the calculated total daily calories. Adjust portion sizes and meal components as needed to meet this goal.**

Each day's diet should be different to provide variety.

Each meal must include:
- A combination of items.
- Each food combination must be provided in the strict format: "Name: Cooking instructions".
- Replace "Name" with the actual food name or combination (e.g., "Salmon Salad").
- "Cooking instructions" should describe the steps to prepare the meal, including the cooking method, key ingredients with their grams, and any important preparation details.
- Calculate the total amount of Calories for that meal in the format "Nutrition: Total Calories: X cal, Total Fat: Xg, Protein: Xg, Carbohydrate: Xg." 

Ensure that:
- The combinations are varied and nutritionally balanced.
- One recipe should only appear once in the plan.
- The recipes must be randomly selected.
- The instructions are simple enough for a home cook.
- The format strictly adheres to JSON, without any code fences, explanations, or additional text.
- The diet restrictions in columns and rows must be obeyed (e.g., if the user is vegetarian, no meat should be included).

**At the end of the plan, provide a summary:**
- "Total Daily Calories: X cal"
- "Macronutrient Breakdown: Fat: X%, Protein: Y%, Carbohydrates: Z%"

Example Output:
{{
  "Morning": [
    "Salmon Scramble: Pan-fry diced salmon with eggs, season with salt and pepper.",
    "Quinoa Porridge: Cook quinoa in water, top with almonds and a drizzle of honey.",
    "Materials: salmon 100g, eggs 2, quinoa 50g, almonds 10g, honey 10g, salt 1g, pepper 1g.",
    "Nutrition: Total Calories: 619 cal, Total Fat: 20g, Protein: 30g, Carbohydrate: 40g."
  ],
  "Noon": [
    "Grilled Chicken Salad: Mix grilled chicken slices with fresh greens, drizzle with olive oil.",
    "Brown Rice with Steamed Vegetables: Steam broccoli and carrots, serve with cooked brown rice.",
    "Materials: chicken 100g, greens 50g, olive oil 10g, rice 50g, broccoli 50g, carrots 50g, salt 1g, pepper 1g.",
    "Nutrition: Total Calories: 357 cal, Total Fat: 15g, Protein: 35g, Carbohydrate: 45g."
  ],
  "Evening": [
    "Baked Salmon: Season salmon with olive oil, bake at 375°F for 15 minutes.",
    "Quinoa-Stuffed Bell Peppers: Fill bell peppers with cooked quinoa and bake.",
    "Materials: salmon 100g, olive oil 10g, quinoa 50g, bell peppers 100g, salt 1g, pepper 1g.",
    "Nutrition: Total Calories: 619 cal, Total Fat: 25g, Protein: 25g, Carbohydrate: 35g."
  ],
  "Summary": [
    "Total Daily Calories: 2595 cal",
    "Macronutrient Breakdown: Fat: 25%, Protein: 35%, Carbohydrates: 40%"
  ]
}}

Using the provided daily food choices below, generate the JSON output for {day}:

{json.dumps(diet_data, indent=2)}
    """
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        max_tokens = 1500,
        temperature = 0.7,
        messages = [
            {"role": "system", "content": "You are an assistant that generates daily diet plans."},
            {"role": "user", "content": prompt}
        ]
    )
                
    response_content = response.choices[0].message.content.strip()
    diet_plan = parse_json(response_content)
    print(diet_plan)
    return diet_plan


def generate_fitness_plan(day, fitness_data, day_index):
    # day_index starts from 1 (Tuesday)
    focus_areas = ["Chest and Arms", "Back and Shoulders", "Legs and Core"]
    if (day_index % 4) == 0:
        focus_area = None  # Rest day
    else:
        focus_area = focus_areas[(day_index - 1) % 3]

    if focus_area is None:
        fitness_plan = {"Evening": None}
    else:
        prompt = f"""
You are a professional fitness trainer AI. Create a detailed and structured fitness plan for {day} based on the requirements and fitness data below. Ensure the plan is comprehensive, meets all criteria, and adheres to the rules provided.

**Requirements and Rules:**

1. **Workout Structure**:
   - Each active day must include **4 to 6 exercises**.
   - Workouts are planned for one session only (either Morning or Evening).
   - Each exercise must specify:
     - "Exercise", "Repetition", "Sets", "Time (minutes)", and "Calorie Consumption (cal)".
     - Calculate Time (minutes) as `sets * time per set` (from {fitness_data}).
     - Calculate calorie consumption as `sets * calorie consumption per set` (from {fitness_data}).
   - Total workout time should be **60 to 90 minutes**.
   - Total calorie consumption for the session should be **300 to 600 calories**, depending on intensity.

2. **Workout Focus**:
   - The workout must target the specific focus area for the day:
     - **{focus_area}**
   - Include a balance of:
     - **Strength training (priority for compound lifts and large muscle groups).**
     - **Cardio (low-to-moderate intensity, time-efficient options).**
     - **Flexibility or core-focused exercises.**

3. **Rest Days**:
   - Rest days must occur after every three active days.
   - Rest days involve no exercises.
   - On rest days, output should be a list with None.

4. **Weekly Plan**:
   - Ensure a balanced rotation of focus areas throughout the week.
   - A week must include exactly **two rest days**.

**Output Format**:
- Provide the output in JSON format only.
- Include a breakdown of exercises and totals for time and calorie consumption.
- Example Output:
{{
    "Evening": [
        {{
            "Exercise": "Barbell Squats",
            "Repetition": 10,
            "Sets": 4,
            "Time (minutes)": 20,
            "Calorie Consumption (cal)": 120
        }},
        {{
            "Exercise": "Pull-Ups",
            "Repetition": 8,
            "Sets": 3,
            "Time (minutes)": 10,
            "Calorie Consumption (cal)": 60
        }}
    ],
    "Total Time": "70 minutes",
    "Total Calorie Consumption": "300 cal"
}}

**Fitness Data Reference**:
{json.dumps(fitness_data, indent=2)}

Generate a fitness plan for {day} strictly in JSON format only.
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are an assistant that generates weekly fitness plans."},
                {"role": "user", "content": prompt}
            ]
        )
          
        response_content = response.choices[0].message.content.strip()
        fitness_plan = parse_json(response_content)
    return fitness_plan

def adjust_daily_progress(day, previous_day, calories_week, diet_plan, fitness_plan, columns, rows):
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

The user's fitness goal, height, weight, age, diet preference, and health conditions can be obtained based on {columns} and {rows}.

The user's weekly routine includes:
    - Rest days must occur after every three active days (e.g., if it starts from Tuesday, then Friday is a rest day).
    - Rest days involve no exercises.
    - Strength training and cardio on active days.

The weekly calorie tracking data for {calories_week} includes:
    - Daily calorie intake and exercise calories burned.

Based on this data:

- If the previous day's calorie consumption exceeds the goal (i.e., consumed more calories than planned), add cardio exercises to today's plan to burn more calories and reduce today's diet calorie intake by up to 200 calories.
- If the previous day's calorie consumption is insufficient (i.e., consumed fewer calories than planned), add strength training exercises to today's plan to increase metabolism and allow for a calorie increase of up to 200 calories in the diet plan.
- If the previous day's calorie consumption aligns with the goal, keep the exercise and diet plans as they are.

Here is today's current exercise plan and diet plan:
Current Exercise Plan for {day}:
{json.dumps(fitness_plan, indent=2)}

Current Diet Plan for {day}:
{json.dumps(diet_plan, indent=2)}

Adjust the plans based on the above rules and format your response strictly as follows:

{{
    "exercise_plan": {{
        "Evening": [/* Adjusted exercises here */],
        "Total Time": "X minutes",
        "Total Calorie Consumption": "Y cal"
    }},
    "diet_plan": {{
      "Morning": [/* Adjusted meals here */],
      "Noon": [/* Adjusted meals here */],
      "Evening": [/* Adjusted meals here */]
    }}
}}

**Do not include any explanations, comments, or additional text. Your entire response should be the JSON object only.**
    """

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        max_tokens = 1000,
        temperature = 0.7,
        messages = [
            {"role": "system", "content": "You are an assistant that adjusts daily exercise and diet plans."},
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
    data = []
    for day, activities in plan.items():
        if plan_type == "Diet":
            if activities is None or not activities:
                data.append({"Day": day, "Diet": None})
            else:
                data.append({
                    "Day": day, 
                    "Morning": activities.get("Morning", ""),
                    "Noon": activities.get("Noon", ""),
                    "Evening": activities.get("Evening", "")
                    })
        elif plan_type == "Fitness":
            if activities is None or not activities:
                data.append({"Day": day, "Fitness": None})
            else:
                data.append({
                    "Day": day,
                    "Evening": activities.get("Evening", "")
                    })
        else:
            meals = activities.get("Diet", {})
            exercises = activities.get("Fitness", {})
            if meals is None or not meals:
                diet_str = None
            else:
                diet_str = f"Morning: {meals.get('Morning', '')}, Noon: {meals.get('Noon', '')}, Evening: {meals.get('Evening', '')}"
            if exercises is None or not exercises:
                exercises_str = None
            else:
                exercises_str = f"Evening: {exercises.get('Evening', '')}"
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
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
        print("Invalid JSON string:", json_str)
        return None


