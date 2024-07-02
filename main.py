import json
import ollama
from actions import get_response_time
from prompts import system_prompt

def generate_text_with_conversation(messages):
    response = ollama.chat(model='llama3', messages=messages)
    return response['message']['content']

available_actions = {
    "get_response_time": get_response_time
}

user_prompt = "what is the response time of google.com"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
]

turn_count = 1
max_turns = 5

def extract_json(text):
    try:
        return json.loads(text)
    except:
        pass

while turn_count < max_turns:
    
    turn_count += 1

    response = generate_text_with_conversation(messages)

    answer_index = response.find("ANSWER: ")
    if answer_index != -1:
        print(response[answer_index + 8:])
        break

    json_function = extract_json(response)

    if json_function:
        function_name = json_function[0]['function_name']
        function_params = json_function[0]['function_params']
        if function_name not in available_actions:
            raise Exception('Tried to run an unrecognized action')
        action_function = available_actions[function_name]
        result = action_function(**function_params)
        function_result_message = f"ACTION_RESPONSE: {result}"
        messages.append({"role": "user", "content": function_result_message})
        with open("logs/history.txt", "w") as log_file:
            log_file.write(function_result_message)
    
    with open("logs/history.txt", "w") as log_file:
        log_file.write("loop " + str(turn_count))
        log_file.write("---")
        log_file.write(response)
