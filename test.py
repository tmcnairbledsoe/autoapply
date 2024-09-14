import os
import sys
import time
import re
import requests
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class AssistantAPI:
    """Class for interacting with OpenAI Assistant API."""
    
    def __init__(self, api_key, organization, project, assistant_id):
        self.client = OpenAI(api_key=api_key, organization=organization, project=project)
        self.thread = self.client.beta.threads.create()
        self.assistant_id = assistant_id

    def call_assistant(self, user_input):
        """Handles interaction with the assistant based on user input."""
        if "salary requirements" in user_input:
            return os.getenv("SALARY")
        if "referred by" in user_input:
            return "No"
        
        try:
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=user_input
            )
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id,
                instructions=(
                    "You are an assistant who will use my resume to answer questions "
                    "as if you were me into a text box. Answer in either a single word, "
                    "yes or no, or with only an integer if possible."
                )
            )
            
            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
                assistant_response = messages.data[0].content[0].text.value
                return self._extract_response(assistant_response)
            else:
                return run.status
        except Exception as e:
            print(f"Error calling assistant API: {e}")
            return None

    @staticmethod
    def _extract_response(assistant_response):
        """Extract numeric or textual response from assistant's message."""
        try:
            number = re.search(r'-?\d+', assistant_response)
            if number:
                return int(number.group())
            return assistant_response
        except:
            return assistant_response

class ChromeDriverManager:
    """Class to manage the setup and operation of ChromeDriver."""
    
    def __init__(self, chrome_profile_path):
        self.chrome_profile_path = chrome_profile_path
    
    def get_latest_version(self):
        """Fetches the latest ChromeDriver version from the official API."""
        try:
            response = requests.get('https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE')
            if response.status_code == 200:
                return response.text.strip()
            else:
                raise Exception('Failed to fetch the latest ChromeDriver version.')
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def download_driver(self, version):
        """Downloads and extracts ChromeDriver."""
        try:
            download_path = os.path.join(os.getcwd(), 'chromedriver.zip')
            extract_to = os.getcwd()
            url = f'https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip'
            
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(download_path, 'wb') as f:
                    f.write(response.content)
                self._extract_zip(download_path, extract_to)
                os.remove(download_path)
                print("ChromeDriver setup complete.")
            else:
                raise Exception('Failed to download ChromeDriver.')
        except Exception as e:
            print(f"Error downloading ChromeDriver: {e}")
            sys.exit(1)
    
    @staticmethod
    def _extract_zip(file_path, extract_to):
        """Extracts ZIP file to a specified directory."""
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    
    def setup_webdriver(self):
        """Sets up the Chrome WebDriver with the user's Chrome profile."""
        version = self.get_latest_version()
        self.download_driver(version)
        
        webdriver_path = os.path.join(os.getcwd(), 'chromedriver-win64', 'chromedriver.exe')
        service = Service(webdriver_path)
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument(f"--user-data-dir={self.chrome_profile_path}")
        chrome_options.add_argument("--profile-directory=Default")
        
        return webdriver.Chrome(service=service, options=chrome_options)

class JobApplicationBot:
    """Bot for automating job applications on LinkedIn."""

    def __init__(self, driver, assistant):
        self.driver = driver
        self.assistant = assistant
        self.wait = WebDriverWait(driver, 10)

    def login(self, email, password):
        """Logs into LinkedIn."""
        try:
            self.driver.get('https://www.linkedin.com/login')
            email_field = self.wait.until(EC.element_to_be_clickable((By.ID, 'username')))
            email_field.send_keys(email)
            
            password_field = self.wait.until(EC.element_to_be_clickable((By.ID, 'password')))
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
        except Exception as e:
            print(f"Error logging in: {e}")
    
    def apply_to_jobs(self):
        """Main function to automate job applications."""
        try:
            # Implement job application logic here
            pass  # Replace with job automation logic
        except Exception as e:
            print(f"Error applying to jobs: {e}")

    def _fill_form_fields(self):
        """Helper function to fill form fields based on assistant's responses."""
        pass  # Implementation to interact with form fields

def autoapply():
    # Load environment variables
    load_dotenv()

    # Initialize Assistant API
    assistant_api = AssistantAPI(
        api_key=os.getenv("API_KEY"),
        organization=os.getenv("ORGANIZATION"),
        project=os.getenv("PROJECT"),
        assistant_id=os.getenv("ASSISTANT_ID")
    )

    # Setup ChromeDriver
    chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
    chrome_manager = ChromeDriverManager(chrome_profile_path)
    driver = chrome_manager.setup_webdriver()

    # Initialize and run the job application bot
    bot = JobApplicationBot(driver, assistant_api)
    bot.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
    bot.apply_to_jobs()

if __name__ == "__autoapply__":
    autoapply()
