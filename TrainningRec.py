from openai import OpenAI
import os

client = OpenAI(
    api_key = os.getenv('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'),
)


#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


inputs = {'Name': 'Jack', 'Age': 20, 'Weight': 'overweight', 'Gender': 'male', 'Fitness_goals': 'muscle gain', 'Physical_activity_level': 'beginner with no experience, can exercise two days a week', 'Health_constraints': 'none', 'Dietary_restrictions': 'does not like vegetables, prefers meat'}

criteria1 = """
Assume you are a gym expert here to provide expert ideas to people who want to work out. To achieve this, follow these steps:
1. Assess the user's fitness goals: Determine whether the user wants to build muscle, lose fat, improve endurance, enhance flexibility, or maintain overall fitness.
2. Evaluate the user's current fitness level: Identify whether they are a beginner, intermediate, or advanced exerciser.
3. Establish workout preferences and constraints: Check for preferred workout styles (e.g., gym-based, bodyweight, outdoor), available time per session, and frequency per week.
4. Design a balanced weekly workout plan: Include exercises for strength, cardio, and flexibility. Ensure variation to prevent monotony and overtraining.
5. Provide clear instructions: Include reps, sets, rest times, and progression suggestions for each exercise.
6. Make it adaptable: Offer alternatives for each exercise and tips for progression as the user improves.
"""

client = OpenAI()
prompt1 = f"{criteria1}\n\nNow, give the expert idea to the person with information list below:\"{inputs}\""

completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": prompt1},
    ]
)
output_text = completion.choices[0].message.content.strip()
print(output_text)