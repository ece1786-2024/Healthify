import os
import json
import pandas as pd
from openai import OpenAI

# Load the CSV file into a DataFrame
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "Enhanced_Nutrition_Dataset.csv")
try:
    df = pd.read_csv(file_path, encoding='utf-8')  # Default
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding='ISO-8859-1')  # Alternate encoding

# Detect the dietary purpose based on the fitness goals (Default: Weight Loss)
def dietary_purpose(Fitness_goals):
    if Fitness_goals == 'Muscle Gain':
        return 'Muscle Gain'
    elif Fitness_goals == 'Weight Loss':
        return 'Weight Loss'
    elif Fitness_goals == 'Improved Endurance':
        return 'Improved Endurance'
    elif Fitness_goals == 'Stress Relief':
        return 'Stress Relief'
    elif Fitness_goals == 'Heart Health':
        return 'Heart Health'
    else:
        return 'Weight Loss'

# Detect the dietary preference based on the dietary preference (Default: General)
def dietary_preference(Dietary_preference):
    if Dietary_preference == 'Heart Health':
        return 'Heart Health'
    elif Dietary_preference == 'Low Sugar':
        return 'Low Sugar'
    elif Dietary_preference == 'High Energy':
        return 'High Energy'
    else:
        return 'General'

def Dietary_recommendation(user_input): 
    # Set parameters based on the user input
    user_purpose = dietary_purpose(user_input['fitness goal'])
    user_preference = dietary_preference(user_input['dietary preference'])

    # Filter the candidate foods based on the user's dietary preference and fitness goals
    if user_purpose == 'Muscle Gain':
        candidate_foods = df[df['muscle_gain'] == 1]
    elif user_purpose == 'Weight Loss':
        candidate_foods = df[df['weight_loss'] == 1]
    elif user_purpose == 'Improved Endurance':
        candidate_foods = df[df['improved_endurance'] == 1]
    elif user_purpose == 'Stress Relief':
        candidate_foods = df[df['stress_relief'] == 1]
    elif user_purpose == 'Heart Health':
        candidate_foods = df[df['heart_health'] == 1]
    else:
        candidate_foods = df  # Default to all foods if no specific purpose

    if user_preference == 'Heart Health':
        candidate_foods = candidate_foods[candidate_foods['category'] == 'Heart Health']
    elif user_preference == 'Low Sugar':
        candidate_foods = candidate_foods[candidate_foods['category'] == 'Low Sugar']
    elif user_preference == 'High Energy':
        candidate_foods = candidate_foods[candidate_foods['category'] == 'High Energy']
    else:
        candidate_foods = candidate_foods  # No additional filtering for 'General'

    # Limit the number of foods to 200
    food_list = candidate_foods[['name', 'calories', 'total_fat', 'protein', 'carbohydrate']].to_dict('records')
    food_list = food_list[:200]

    # Convert the food list to a text format
    food_text = ""
    for food in food_list:
        name = food.get('name')
        calories = food.get('calories')
        total_fat = food.get('total_fat')
        protein = food.get('protein')
        carbohydrate = food.get('carbohydrate')
        
        food_text += f"name: {name}\n"
        food_text += f"calories per gram: {calories} cal/g\n"
        food_text += f"total_fat per gram: {total_fat} g/g\n"
        food_text += f"protein per gram: {protein} g/g\n"
        food_text += f"carbohydrate per gram: {carbohydrate} g/g\n"

    client = OpenAI(
        api_key = os.getenv('YOUR_API_KEY'),
    )

    def dietary_recommendation(user_input):
        prompt = f"""
User Input: {user_input}
Loaded Dataset:
{food_text}

Using the loaded dataset and the user input, recommend a diverse and balanced set of food items for the user.  For each food item, provide the calories and nutritional values per gram.  Do not limit or specify the weight of each food item.

The user's profile includes age, gender, weight, fitness goal, dietary restrictions, and eating preferences. Use the user's age, gender, fitness goal, dietary preferences, and weight to provide the recommendations of food. Ensure the recommendations comply with the user's dietary restrictions and preferences. Exclude any foods that violate these restrictions. 

Recommend exactly 100 food items suitable for the user using the loaded food dataset. For each food item, provide the following details:
- Food Name
- Calories per gram
- Total Fat per gram
- Protein per gram
- Carbohydrate per gram

Ensure that the recommendations comply with the user's dietary restrictions.  Exclude any foods that violate these restrictions.  The recommended foods should be common and accessible.

Structure the output in JSON format with the following structure:
{{
  "Name": "User's Name",
  "Recommended Foods": [
    {{
      "Food Choices_1": {{
        "Food Name": "Food Name",
        "Calories per gram": X,
        "Total Fat per gram": X,
        "Protein per gram": X,
        "Carbohydrate per gram": X
      }},
      ...
      "Food Choices_100": {{
        "Food Name": "Food Name",
        "Calories per gram": X,
        "Total Fat per gram": X,
        "Protein per gram": X,
        "Carbohydrate per gram": X
      }}
    }}
  ]
}}

The output must include exactly 100 recommendations. Do not include any explanations or calculations in the response. Only provide the JSON output as described.
    """
        response = client.chat.completions.create(
            model = "gpt-4o",
            max_tokens = 1500,
            temperature = 0.7,
            messages = [
                {"role": "user", "content": prompt}
            ]
        )

        extracted_info = response.choices[0].message.content.strip()

        return extracted_info

    # Generate the recommendations
    recommendation = dietary_recommendation(user_input)
    print(recommendation)
    return recommendation


