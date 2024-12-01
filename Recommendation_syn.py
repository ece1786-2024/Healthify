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
- **Total daily calories**: TDEE plus 500 calories.
- **Macronutrient distribution**: Total Fat: 20-30%; Protein: 35-45%; Carbohydrates: 40-50%.

**Ensure that the total calories for all meals combined reach the calculated total daily calories (e.g., if the calculated total daily calories are 3500 cal, the sum of the calories from all meals should be close to 3500 cal). Adjust portion sizes and meal components as needed to meet this goal.**

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
- **Use only the foods provided in the diet_data below (excluding salt, sugar, oil, etc.) to create the meals.**
- **Adjust portion sizes and include additional meals or snacks if necessary to meet the total daily calorie requirement.**

**At the end of the plan, provide a summary:**
- "Total Daily Calories: X cal"
- "Macronutrient Breakdown: Fat: X%, Protein: Y%, Carbohydrates: Z%"

Example Output:
{{
  "Morning": [
    "Salmon Scramble: Pan-fry diced salmon (200g) with eggs (3), season with salt and pepper.",
    "Quinoa Porridge: Cook quinoa (100g) in water, top with almonds (20g) and a drizzle of honey.",
    "Materials: salmon 200g, eggs 3, quinoa 100g, almonds 20g, honey 10g, salt 1g, pepper 1g.",
    "Nutrition: Total Calories: 1238 cal, Total Fat: 40g, Protein: 60g, Carbohydrate: 80g."
  ],
  "Noon": [
    "Grilled Chicken Salad: Mix grilled chicken slices (200g) with fresh greens (100g), drizzle with olive oil.",
    "Brown Rice with Steamed Vegetables: Steam broccoli (100g) and carrots (100g), serve with cooked brown rice (100g).",
    "Materials: chicken 200g, greens 100g, olive oil 10g, rice 100g, broccoli 100g, carrots 100g, salt 1g, pepper 1g.",
    "Nutrition: Total Calories: 714 cal, Total Fat: 30g, Protein: 70g, Carbohydrate: 90g."
  ],
  "Evening": [
    "Baked Salmon: Season salmon (200g) with olive oil, bake at 375°F for 15 minutes.",
    "Quinoa-Stuffed Bell Peppers: Fill bell peppers (200g) with cooked quinoa (100g) and bake.",
    "Materials: salmon 200g, olive oil 10g, quinoa 100g, bell peppers 200g, salt 1g, pepper 1g.",
    "Nutrition: Total Calories: 1238 cal, Total Fat: 50g, Protein: 50g, Carbohydrate: 70g."
  ],
  "Summary": [
    "Total Daily Calories: 3190 cal",
    "Macronutrient Breakdown: Fat: 29%, Protein: 35%, Carbohydrates: 36%"
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
    return diet_plan


def generate_fitness_plan(day, fitness_data, day_index, columns, rows, diet_plan):
    focus_areas = ["Chest and Arms", "Back and Shoulders", "Legs and Core"]
    if (day_index % 4) == 0:
        focus_area = None  # Rest day
    else:
        focus_area = focus_areas[(day_index - 1) % 3]
    
    if focus_area is None:
        fitness_plan = {"Evening": "Relax day"}
    else:
        # Extract user data
        gender = rows[0][columns.index('gender')]
        age = int(rows[0][columns.index('age')])
        weight = float(rows[0][columns.index('weight')])  # in kg
        height = float(rows[0][columns.index('height')])  # in cm
        fitness_goal = rows[0][columns.index('fitness_goal')]
        health_conditions = rows[0][columns.index('health_restrictions')]
        fitness_level = rows[0][columns.index('physical_activity_level')]
        
        # Calculate BMR
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Assume a moderate activity level
        activity_factor = 1.55
        tdee = bmr * activity_factor
        total_daily_calories = tdee
        
        # Extract total daily calories from diet_plan
        total_diet_calories = 0
        if 'Summary' in diet_plan:
            for item in diet_plan['Summary']:
                if "Total Daily Calories" in item:
                    total_diet_calories = float(item.split(':')[1].strip().split()[0])
                    break
        
        prompt = f"""
You are a professional fitness trainer AI. Create a detailed and structured fitness plan for {day} based on the requirements and fitness data below. Ensure the plan is comprehensive, meets all criteria, and adheres to the rules provided.

**User Information:**
- Gender: {gender}
- Age: {age} years
- Weight: {weight} kg
- Height: {height} cm
- Fitness Level: {fitness_level}
- Fitness Goal: {fitness_goal}
- Health Conditions: {health_conditions}
- Total Daily Calorie Intake from Diet Plan: {total_diet_calories:.0f} cal
- Total Daily Energy Expenditure (TDEE): {tdee:.0f} cal

**Requirements and Rules:**

1. **Workout Structure**:
   - the number of workout from 4 to 6. No less or more
   - the number of sets at least 6, no more than 12.
   - Workouts are planned for one session only (either Morning or Evening).
   - Each exercise must specify:
     - "Exercise", "Repetition", "Sets", "Time (minutes)", and "Calorie Consumption (cal)".
     - Calculate Time (minutes) as **sets * duration per set (from {fitness_data} and transfer into minutes from second)**.
     - Calculate Calorie Consumption as **sets * calorie consumption per set (from {fitness_data})**.
   - the sum of all exericses' Time (minutes) should be **60 to 120 minutes**.
   - the sum of all exericses' calorie consumption for the session should be **400 to 600 calories**.

2. **Workout Focus**:
   - The workout must target the specific focus area for the day:
     - **{focus_area}**
   - Include a balance of:
     - **Strength training (priority for compound lifts and large muscle groups).**
     - **Cardio (adjust duration and intensity to help meet caloric expenditure goals), it cannot exceed 60 minutes.**
     - **Flexibility or core-focused exercises.**

3. **Rest Days**:
   - Rest days must occur after every three active days.
   - Rest days involve no exercises and contain Relax Day instead the exercises.

4. **Weekly Plan**:
   - Ensure a balanced rotation of focus areas throughout the week.

**Use only the exercises provided in the fitness_data below to create the plan.**

**Output Format**:
- if the list of exercises is empty, provide the output as "Evening": "Relax day".
- Provide the output in JSON format only.
- Include a breakdown of exercises and totals for time and calorie consumption.
- Example Output:
{{
    "Evening": [

    "Exercise 1": "Barbell Squats",
    "Repetition": 10,
    "Ses": 4,
        "Time (minutes)": 20,
    "Calorie Consumption (cal)": 120
    ,
    
    "Exercise 2": "Pull-Ups",
    "Repetition": 8,
    "Sets": 3,
    "Time (minutes)": 10,
    "Calorie Consumption (cal)": 60

    ]
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
    print(fitness_plan)
    return fitness_plan


def adjust_daily_progress(day, previous_day, calories_week, diet_plan, fitness_plan, columns, rows, diet_data, fitness_data):
    """
    Analyzes whether the daily exercise is sufficient based on consumption and intake.
    Adjusts the exercise plan.
    """
    if not calories_week or not previous_day:
        return fitness_plan, diet_plan

    # Extract user data
    gender = rows[0][columns.index('gender')]
    age = int(rows[0][columns.index('age')])
    weight = float(rows[0][columns.index('weight')])  # in kg
    height = float(rows[0][columns.index('height')])  # in cm
    fitness_goal = rows[0][columns.index('fitness_goal')]
    health_conditions = rows[0][columns.index('health_restrictions')]

    # Calculate BMR
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161


    ingest_calories = calories_week[previous_day]["Calorie intake"]
    burned_calories = calories_week[previous_day]["calories burned (exercise)"]
    calorie_difference = ingest_calories - bmr - burned_calories
    print(calorie_difference)
    prompt = f"""

You are a fitness and nutrition expert AI.

The user consumed **{ingest_calories} calories** on {previous_day} and burned **{burned_calories} calories** through exercise.

The user's fitness goal is **{fitness_goal}**. Their age is **{age}**, height is **{height} cm**, weight is **{weight} kg**, and they have the following health conditions: **{health_conditions}**.

The user's weekly routine includes:
- Rest days must occur after every three active days (e.g., if it starts from Tuesday, then Friday is a rest day).
- Rest days involve no exercises.
- Strength training and cardio on active days.

The weekly calorie tracking data is:
{json.dumps(calories_week, indent=2)}

**Issue to Address:**

- The daily calorie intake and calorie consumption are **below the limits specified in the workout structure**.
- The calorie difference between actual and planned intake is **{calorie_difference:.0f} calories**.

**Requirements:**

1. **Adjust the Fitness Plan**:

   - **Increase the total exercise time and calorie consumption** to meet the minimum required:
     - **Total Time (minutes)**: the sum of Total Time for each exercise at least **60 minutes** and no more than **120** minutes.
     - **Total Calorie Consumption (cal)**: At least **400 calories**.
   - **Select additional exercises** that are suitable for the user's fitness level and health conditions.
   - The sum of bmi and Total Calorie Consumption (cal) in fitness plan should larger than the total daily calories in diet plan.
   - Ensure that the **number of workouts is between 4 and 6**, and the **number of sets is at least 6 less than 12 (based on the total time not excced two hours)**.

2. **Adjust the Diet Plan**:

   - **Increase the total daily calorie intake** to meet the minimum required.
   - Adjust meals by adding nutrient-dense foods from the provided diet data.
   - Ensure that the **macronutrient distribution** remains balanced.

3. **Rest Days**:
- Rest days must occur after every three active days.
- Rest days involve no exercises and contain Relax Day instead the exercises.

**Constraints:**

- **Use only the foods provided in `diet_data`** (excluding salt, sugar, oil, etc.) and the **exercises provided in `fitness_data`**.
- **All adjustments must strictly adhere to the user's dietary restrictions and health conditions**.
- **Do not exceed the maximum limits specified in the workout structure**.

**Output Format:**
- ** if the list of exercises is empty or "Relax day", provide the output as "Evening": "Relax day". **
- **Provide the adjusted plans in valid JSON format like Current Exercise Plan and Current Diet Plan**.
- **Include all required fields** for each exercise and meal.
- **Do not include any explanations or additional text**.

**Adjusted Exercise Plan for {day}:**

(Current Exercise Plan)
{json.dumps(fitness_plan, indent=2)}

**Adjusted Diet Plan for {day}:**

(Current Diet Plan)
{json.dumps(diet_plan, indent=2)}

**Diet Data Reference:**
{json.dumps(diet_data, indent=2)}

**Fitness Data Reference:**
{json.dumps(fitness_data, indent=2)}
"""


    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1000,
        temperature=0.7,
        messages=[
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
    try:
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        return json.loads(json_str.strip())
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {}




