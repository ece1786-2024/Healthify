from openai import OpenAI
import os
import pandas as pd

file_path = r"C:\Users\ZZY\Desktop\1786project\Healthify\Final_Gym_Dataset.csv"

df = pd.read_csv(file_path)



user_inputs = {'Name': 'Jack', 'Age': 20, 'Weight': 'overweight', 'Gender': 'male', 'Fitness_goals': 'muscle gain', 'Physical_activity_level': 'beginner with no experience, can exercise two days a week', 'Health_constraints': 'none', 'Dietary_restrictions': 'does not like vegetables, prefers meat'}

criteria = """
Assume you are a gym expert here to provide expert ideas to people who want to work out. To achieve this, here are some criterias:
1. Assess the user's fitness goals: Determine whether the user wants to build muscle, lose fat, improve endurance, enhance flexibility, or maintain overall fitness.
2. Evaluate the user's current fitness level: Identify whether they are a beginner, intermediate, or advanced exerciser.
3. Establish workout preferences and constraints: Check for preferred workout styles (e.g., gym-based, bodyweight, outdoor), available time per session, and frequency per week.
4. Design a balanced weekly workout plan: Include exercises for strength, cardio, and flexibility. Ensure variation to prevent monotony and overtraining.
5. Provide clear instructions: Include reps, sets, rest times, and progression suggestions for each exercise.
6. Make it adaptable: Offer alternatives for each exercise and tips for progression as the user improves.

Follow these criteria and use the exercises provided to create a training recommendation. Focus solely on training recommendations, not dietary advice.
"""

# Map the user's physical activity level to the dataset's 'Level'
def map_experience_level(physical_activity_level):
    if 'beginner' in physical_activity_level.lower():
        return 'Beginner'
    elif 'intermediate' in physical_activity_level.lower():
        return 'Intermediate'
    elif 'advanced' in physical_activity_level.lower():
        return 'Advanced'
    else:
        return 'Beginner'  # Default to 'Beginner'
    
user_level = map_experience_level(user_inputs['Physical_activity_level'])

# Filter the dataset for relevant exercises
relevant_exercises = df[
    (df['Muscle Gain'] == 1) &
    (df['Level'].str.lower() == user_level.lower())
]

# If the dataset is large, limit the number of exercises
relevant_exercises = relevant_exercises.head(10)

exercise_list = relevant_exercises[['Title', 'Desc', 'BodyPart', 'Equipment', 'Duration (seconds)', 'Repetitions']].to_dict('records')

exercise_text = ""
for exercise in exercise_list:
    title = exercise.get('Title', 'N/A')
    desc = exercise.get('Desc', 'No description available.')
    body_part = exercise.get('BodyPart', 'Various')
    equipment = exercise.get('Equipment', 'None')
    duration = exercise.get('Duration (seconds)', 'Varies')
    repetitions = exercise.get('Repetitions', 'Varies')
    
    exercise_text += f"Title: {title}\n"
    exercise_text += f"Description: {desc}\n"
    exercise_text += f"Body Part: {body_part}\n"
    exercise_text += f"Equipment: {equipment}\n"
    exercise_text += f"Duration: {duration} seconds\n"
    exercise_text += f"Repetitions: {repetitions}\n\n"

client = OpenAI(
    api_key = os.getenv('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'),
)

# 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


prompt = f"""
{criteria}

User Information:
{user_inputs}

Available Exercises:
{exercise_text}

Now, based on the above information, provide a personalized training recommendation for the user.
"""


completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": prompt},
    ]
)
output_text = completion.choices[0].message.content.strip()
print(output_text)