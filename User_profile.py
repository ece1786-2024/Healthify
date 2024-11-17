import os
from openai import OpenAI
import json

client = OpenAI(
    api_key = os.getenv('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'),
)

def get_user_profile():
    # initialize the dialoge
    messages = [
        {"role": "system", 
         "content":
            "You are a friendly fitness assistant, responsible for having a natural conversation with the user,"
            "Gradually collect the following information: name, age, gender, weight, fitness goals,"
            "Current physical activity levels, health restrictions, and dietary preferences."
            "Ask one question at a time and respond appropriately based on the user's answers."
        }
    ]

    user_profile = {}

    info_keys = {
        "name": "name",
        "age": "age",
        "gender": "gender",
        "weight": "weight",
        "fitness goal": "fitness goal",
        "current physical activity levels": "current physical activity levels",
        "health restrictions": "health restrictions",
        "dietary preferences": "dietary preferences"  
    }

    collected_keys = set()

    while True:
        # check whether get all the information
        if len(collected_keys) == len(info_keys):
            print("All information collected.")
            break

        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = messages,
            max_tokens = 150,
            temperature = 0.7,
        )

        assistant_message = response.choices[0].message.content.strip()
        print(f"Assistant: {assistant_message}")
        messages.append({"role": "assistant", "content": assistant_message})

        # get user
        user_input = input("User: ")

        messages.append({"role": "user", "content": user_input})

        extraction_prompt = (
            "As an AI assistant, extract any personal information provided from the user's response below. "
            "Include the following keys exactly as specified: "
            "'name', 'age', 'gender', 'weight', 'fitness goal', "
            "'current physical activity levels', 'health restrictions', 'dietary preferences'. "
            "Please output the new information in JSON format(remove Markdown code), without explanation or additional text. "
            "If a piece of information is not provided, do not include it in the JSON."
            "\n\nUser's reply:\n"
            f"\"\"\"\n{user_input}\n\"\"\""
        )

        extraction_response = client.chat.completions.create(
            model = "gpt-4o",
            messages=[
                {"role": "system", "content": extraction_prompt}
            ],
            max_tokens= 150,
            temperature= 0,
        )

        extraction_result = extraction_response.choices[0].message.content.strip()
        
        # Try to parse the JSON and update user_profile
        try:
            new_info = json.loads(extraction_result)
            for key, value in new_info.items():
                key_lower = key.lower()
                if key_lower in info_keys:
                    user_profile[info_keys[key_lower]] = value
                    collected_keys.add(info_keys[key_lower])
        except json.JSONDecodeError as e:
            print("JSON decoding failed:", e)
            print("Extraction Result was:", extraction_result)
            continue  # Proceed to the next iteration

    # Return or print the collected user profile
    print("Collected User Profile:")
    print(json.dumps(user_profile, indent=2))


if __name__ == "__main__":
    get_user_profile()


