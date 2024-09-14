import os
import re
from openai import OpenAI

api_key_string = os.getenv("API_KEY")
organization_string = os.getenv("ORGANIZATION")
project_string = os.getenv("PROJECT")
assistant_id_string = os.getenv("ASSISTANT_ID")

client = OpenAI(api_key=api_key_string, organization=organization_string, project=project_string)
thread = client.beta.threads.create()
assistantId = assistant_id_string

def call_assistant_api(user_input):
    if "salary requirements" in user_input:
        return os.getenv("SALARY")
    if "referred by" in user_input:
        return "No"
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_input)
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, 
        assistant_id=assistantId,
        instructions="Answer as if you were me using my resume."
    )
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = messages.data[0].content[0].text.value
        number = re.search(r'-?\d+', assistant_response)
        return int(number.group()) if number else assistant_response
    return "Unable to complete"
