import os
from dotenv import load_dotenv

def load_environment():
    load_dotenv()
    return {
        "api_key": os.getenv("API_KEY"),
        "organization": os.getenv("ORGANIZATION"),
        "project": os.getenv("PROJECT"),
        "assistant_id": os.getenv("ASSISTANT_ID"),
        "email": os.getenv("EMAIL"),
        "password": os.getenv("PASSWORD"),
        "chrome_profile_path": os.getenv("CHROME_PROFILE_PATH"),
        "salary": os.getenv("SALARY")
    }
