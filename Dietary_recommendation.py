import os
from openai import OpenAI
import json
import pandas as pd

# Load the CSV file into a DataFrame
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "Enhanced_Nutrition_Dataset.csv")
df = pd.read_csv(file_path)

# Example user input
user_input = {'Name': 'Terry', 'Height': 181, 'Age': 23, 'Weight': '81Kg', 'Gender': 'Male', 'Fitness_goals': 'Weight Loss', 'Dietary_preference': 'High Energy' , 'Physical_activity_level': 'Beginner with no experience, can exercise two days a week', 'Health_constraints': 'None mentioned', 'Dietary_restrictions': 'allergy to peanuts'}

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
    
# Set those parameters based on the user input
user_purpose = dietary_purpose(user_input['Fitness_goals'])
user_preference = dietary_preference(user_input['Dietary_preference'])


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


if user_preference == 'Heart Health':
    candidate_foods = candidate_foods[candidate_foods['category'] == 'Heart Health']
elif user_preference == 'Low Sugar':
    candidate_foods = candidate_foods[candidate_foods['category'] == 'Low Sugar']
elif user_preference == 'High Energy':
    candidate_foods = candidate_foods[candidate_foods['category'] == 'High Energy']

food_list = candidate_foods[['name', 'calories', 'total_fat', 'protein', 'carbohydrate']].to_dict('records')
# Limit the number of foods to 200
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
    food_text += f"calories: {calories}\n"
    food_text += f"total_fat: {total_fat}\n"
    food_text += f"protein: {protein}\n"
    food_text += f"carbohydrate: {carbohydrate}\n"


client = OpenAI(
    api_key = os.getenv('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'),
)

def dietary_recommendation(user_input):
    prompt = f"""

User Input:{user_input}
Loaded Dataset:{food_text}    

Use the loaded dataset and the User Input to recommend a dietary food choice for the user based on the extracted information. 
The input sequence includes essential information about the user's profile, such as the user's age, gender, weight, fitness goal, dietary restrictions, eating preference. 
The loaded dataset contains a list of food items with their nutritional information, such as calories, total fat, protein, and carbohydrate.
Use user's age, gender, weight information to estimate the user's Body Mass Index (BMI) and Total Daily Energy Expenditure (TDEE).
After calculating the BMI and TDEE, combining the eating preference to calculate the daily calorie and food weight intake, recommend five sets of dietary food choices for the user using the loaded food dataset.
The dietary food choices should include the food name and weight for each kind of food.
The recommendation sets should comply with the user's dietary restrictions. Any food that violates the user's dietary restrictions should be excluded from the recommendation.



For output sequence, provide a dietary recommendation for the user based on the extracted information. 
The output should be a JSON format sequences with keys: Name, BMI, TDEE, Daily Food Choices_1, Daily Food Choices_2, Daily Food Choices_3, Daily Food Choices_4, Daily Food Choices_5. Only include BMI & TDEE number, not calculation.
The Daily Food Choices keys contains daily food choices and weight for each kind of food. 
The output should remove Markdown code.
"""
    response = client.chat.completions.create(
        model = "gpt-4o",
        max_tokens = 700,
        temperature = 0,
        messages = [
            {"role": "system", "content": prompt}
        ]
    )

    extracted_info = response.choices[0].message.content.strip()

    return extracted_info

# Extract user profile
recommendation = dietary_recommendation(user_input)

print(recommendation)
