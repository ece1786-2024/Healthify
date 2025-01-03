from openai import OpenAI
import os
import pandas as pd

def Training_recommendation(user_inputs):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "Final_Gym_Dataset.csv")

    try:
        df = pd.read_csv(file_path, encoding='utf-8')  # Default
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')  # Alternate encoding

    criteria = """
    Assume you are a gym expert here to provide expert ideas to people who want to work out. To achieve this, here are some criterias:
    1. Assess the user's fitness goals: Determine whether the user wants to build muscle, lose fat, improve endurance, enhance flexibility, or maintain overall fitness.
    2. Evaluate the user's current fitness level: Identify whether they are a beginner, intermediate, or advanced exerciser.
    3. Account for Health Restrictions: Consider any health restrictions or conditions (e.g., mild asthma, joint issues) provided by the user. Avoid exercises that could aggravate these conditions, and instead suggest safe alternatives that align with their goals.
    4. Establish workout preferences and constraints: Check for preferred workout styles (e.g., gym-based, bodyweight, outdoor), available time per session, and frequency per week.
    5. Design a balanced weekly workout plan: Include exercises for strength, cardio, and flexibility. Ensure variation to prevent monotony and overtraining.
    6. Provide clear instructions: Include reps, sets, rest times, and progression suggestions for each exercise.
    7. Make it adaptable: Offer alternatives for each exercise and tips for progression as the user improves.
    

    Follow these criteria and use the exercises provided to create a training recommendation. Focus solely on training recommendations, not dietary advice.
    """
    user_level = map_experience_level(user_inputs['current physical activity levels'])

    # Filter the dataset for relevant exercises
    relevant_exercises = df[
        (df['Muscle Gain'] == 1) &
        (df['Level'].str.lower() == user_level.lower())
    ]

    # If the dataset is large, limit the number of exercises
    relevant_exercises = relevant_exercises.head(50)

    exercise_list = relevant_exercises[['Title', 'Desc', 'BodyPart', 'Equipment', 'Duration (seconds)', 'Repetitions', 'Calories consumption']].to_dict('records')

    exercise_text = ""
    for exercise in exercise_list:
        title = exercise.get('Title', 'N/A')
        desc = exercise.get('Desc', 'No description available.')
        body_part = exercise.get('BodyPart', 'Various')
        equipment = exercise.get('Equipment', 'None')
        duration = exercise.get('Duration (seconds)', 'Varies')
        repetitions = exercise.get('Repetitions', 'Varies')
        calories = exercise.get('Calories consumption', 'Varies')
    
        exercise_text += f"Title: {title}\n"
        exercise_text += f"Description: {desc}\n"
        exercise_text += f"Body Part: {body_part}\n"
        exercise_text += f"Equipment: {equipment}\n"
        exercise_text += f"Duration: {duration} seconds\n"
        exercise_text += f"Repetitions: {repetitions}\n"
        exercise_text += f"Calories consumption: {calories}\n\n"

    client = OpenAI(
        api_key="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"
    )


    # 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


    prompt = f"""
    {criteria}

    User Information:
    {user_inputs}

    Available Exercises:
    {exercise_text}

    Now, based on the above information, provide 100 personalized training recommendations for the user. The output should be a JSON format sequences with keys: Exercise Choices_1, Exercise Choices_2, Exercise Choices_3, Exercise Choices_4, Exercise Choices_5 and keep until Exercise chocies_100. 
    For each exercise, give a brief description for how to do it. Just json, also with "Reps", "Duration","Rest", "Calories consumption". no others things like tip or else.
    For "Reps", extract the repetitions from the column "Repetitions" from the dataset, and output the number of repetitions by dividing the repetitions by the number of sets. 
    For "Duration", output the duration from the column "Duration (seconds)" from the dataset.
    For example, if the repetitions are 18 and the sets are 2, then the output of "Reps" would be 18 / 2 = 9 repetitions. Only give the final calculated result, not the steps.
    For "Calories consumption", output the calories from the column "Calories consumption" from the dataset, do not make up any information or any calculations.
    """


    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
        ]
    )
    output_text = completion.choices[0].message.content.strip()
    print(output_text)
    return output_text



# Map the user's physical activity level to the dataset's 'Level'
def map_experience_level(physical_activity_level):
    if 'beginner' in physical_activity_level.lower() and not None:
        return 'Beginner'
    elif 'intermediate' in physical_activity_level.lower() and not None:
        return 'Intermediate'
    elif 'advanced' in physical_activity_level.lower() and not None:
        return 'Advanced'
    else:
        return 'Beginner'  # Default to 'Beginner'
    
    