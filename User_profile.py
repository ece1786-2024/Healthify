import os
from openai import OpenAI
import json

client = OpenAI(
    api_key = os.getenv('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'),
)

def extract_user_profile(user_input):
    prompt = f"""
Translate the user input into English and Extract the following information from the user's input:
- Name
- Age
- Gender
- Weight
- Fitness Goals
- Current Physical Activity Level
- Health Constraints
- Dietary Restrictions

User Input:
\"\"\"
{user_input}
\"\"\"

Only Provide the extracted information in JSON format with keys: Name, age, weight, gender, fitness_goals, physical_activity_level, Health_constraints, Dietary_restrictions. The output should remove Markdown code
"""
    response = client.chat.completions.create(
        model = "gpt-4o",
        max_tokens = 300,
        temperature = 0,
        messages = [
            {"role": "system", "content": prompt}
        ]
    )

    extracted_info = response.choices[0].message.content.strip()

    return extracted_info

# Example user input
user_input = """
我的名字叫Jack,我是一名20岁没有任何健身经验的男性初学者, 我长得很胖但我想要增肌,我每周时间只有两天可以锻炼,我不喜欢吃蔬菜更喜欢吃肉,不想做太激烈的运动。
"""

# Extract user profile
user_profile = extract_user_profile(user_input)

data_dict = json.loads(user_profile)

print(data_dict)

