import os
from openai import OpenAI
import json
import pandas as pd

# Load the CSV file into a DataFrame
file_path = "c:/Users/Administrator/Desktop/Enhanced_Nutrition_Dataset.csv"
df = pd.read_csv(file_path)

client = OpenAI(
    api_key = os.getenv('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'),
)

def dietary_recommendation(user_input):
    prompt = f"""
Use the loaded dataset and the input sequence to recommend a dietary food choice for the user based on the extracted information. 
The input sequence includes essential information about the user's profile, such as the user's age, gender, weight, fitness goal, dietary restrictions, eating preference. 
Use user's age, gender, weight information to estimate the user's Body Mass Index (BMI) and Total Daily Energy Expenditure (TDEE).
After calculating the BMI and TDEE, combining the eating preference to calculate the daily calorie and food weight intake, recommend five sets of dietary food choices for the user using the loaded food dataset.
The dietary food choices should include the food name and weight for each kind of food.
The recommendation sets should comply with the user's dietary restrictions. Any food that violates the user's dietary restrictions should be excluded from the recommendation.


User Input:
\"\"\"
{user_input}
\"\"\"

For output sequence, provide a dietary recommendation for the user based on the extracted information. 
The output should be a JSON format sequences with keys: Name, BMI, TDEE, Daily Food Choices_1, Daily Food Choices_2, Daily Food Choices_3, Daily Food Choices_4, Daily Food Choices_5. Only include the number of BMI, TDEE.
The Daily Food Choices keys contains daily food choices and weight for each kind of food. 
The output should remove Markdown code.
"""
    response = client.chat.completions.create(
        model = "gpt-4o",
        max_tokens = 500,
        temperature = 0,
        messages = [
            {"role": "system", "content": prompt}
        ]
    )

    extracted_info = response.choices[0].message.content.strip()

    return extracted_info

# Example user input
user_input = """
{'Name': 'Jack', 'Height': 180, 'Age': 20, 'Weight': '80Kg', 'Gender': 'Male', 'Fitness_goals': 'Muscle gain', 'Heavy_Eater': 'Normal' , 'Physical_activity_level': 'Beginner with no experience, can exercise two days a week', 'Health_constraints': 'None mentioned', 'Dietary_restrictions': 'Prefers meat over vegetables, dislikes intense exercise'}
"""

# Extract user profile
recommendation = dietary_recommendation(user_input)

#data_dict = json.loads(recommendation)
#print(data_dict)
print(recommendation)
