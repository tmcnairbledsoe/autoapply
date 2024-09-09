from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select 
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
import time
from openai import OpenAI
from bs4 import BeautifulSoup

import requests
import zipfile
import os
import sys
import re

# Get sensitive information from environment variables
api_key_string = os.getenv("API_KEY")
organization_string = os.getenv("ORGANIZATION")
project_string = os.getenv("PROJECT")
assistant_id_string = os.getenv("ASSISTANT_ID")
email_string = os.getenv("EMAIL")
password_string = os.getenv("PASSWORD")
chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
salary_string = os.getenv("SALARY")

client = OpenAI(api_key=api_key_string,organization=organization_string,project=project_string,)


thread = client.beta.threads.create()
assistantId = assistant_id_string

def call_assistant_api(user_input):
    if "salary requirements" in user_input:
        return salary_string
    if "referred by" in user_input:
        return "No"
    message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_input
    )
    run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistantId,
    instructions="You are an assistant who will use my resume to answer questions as if you were me into a text box. Answer in either a single word, yes or no, or with only an integer if possible."
    )
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        assistant_response = messages.data[0].content[0].text.value
        try:
            number = re.search(r'-?\d+', assistant_response)  # This will also match negative numbers
            if number:
                return int(number.group())
            else:
                return assistant_response
        except:
            return assistant_response
    else:
        print(run.status)

def get_latest_chrome_driver_version():
    # Fetch the latest ChromeDriver version from the official API
    response = requests.get('https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE')
    
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception('Failed to fetch the latest ChromeDriver version.')

def download_chrome_driver(version, download_path):
    # Build the download URL for Windows
    
    url = f'https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip'
    
    # Download the file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(download_path, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception('Failed to download ChromeDriver.')

def extract_zip(file_path, extract_to):
    # Extract the ZIP file
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def setup_chrome_driver():
    try:
        # Get the latest ChromeDriver version
        version = get_latest_chrome_driver_version()
        print(f"Latest ChromeDriver version: {version}")

        # Paths
        download_path = os.path.join(os.getcwd(), 'chromedriver.zip')
        extract_to = os.getcwd()

        # Download ChromeDriver
        print("Downloading ChromeDriver...")
        download_chrome_driver(version, download_path)
        
        # Extract ChromeDriver
        print("Extracting ChromeDriver...")
        extract_zip(download_path, extract_to)

        # Clean up the ZIP file
        os.remove(download_path)
        print("ChromeDriver setup complete.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Call the function to setup ChromeDriver
setup_chrome_driver()

# Set up WebDriver service
webdriver_path = os.path.join(os.getcwd(), 'chromedriver-win64\\chromedriver.exe')

service = Service(webdriver_path)

chrome_profile_path = chrome_profile_path
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument(f"--user-data-dir={chrome_profile_path}")
chrome_options.add_argument("--profile-directory=Default") 

# Now you can continue with your Selenium code
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get('https://www.linkedin.com/login')

# Wait for the page to load
wait = WebDriverWait(driver, 10)


def press_escape_key():
    # You can send ESC to any element or active element
    body = driver.find_element(By.TAG_NAME, 'body')  # Sending Escape to the body
    body.send_keys(Keys.ESCAPE)
    print("Escape key pressed.")


def click_discard_button():
    try:
        # Find the button that contains the text 'Discard'
        discard_button = driver.find_element(By.XPATH, "//button[.//span[text()='Discard']]")
        discard_button.click()
        print("Discard button clicked!")
    except NoSuchElementException:
        print("No 'Discard' button found.")
        raise NoSuchElementException()

def click_continue_button():
    try:
        # Find the button with aria-label "continue to next step"
        button = driver.find_element(By.XPATH, "//button[@aria-label='Continue to next step' or @aria-label='Review your application']")
        button.click()
        print("Button clicked!")
    except NoSuchElementException:
        print("No 'continue to next step' button found.")
        raise NoSuchElementException()
        
def click_submit_button():
    try:
        # Find the button with aria-label "continue to next step"
        button = driver.find_element(By.XPATH, "//button[@aria-label='Submit application']")
        button.click()
        print("Button clicked!")
    except NoSuchElementException:
        print("No 'submit' button found.")
        raise NoSuchElementException()
        
def click_done_button():
    try:
        # Find the button with aria-label "continue to next step"
        button = driver.find_element(By.XPATH, "//button[.//span[text()='Done']]")
        button.click()
        print("Button clicked!")
    except NoSuchElementException:
        print("No 'done' button found.")
        raise NoSuchElementException()
try:

    try:
    
        # Wait for the email input field to be clickable and enter your email
        email = wait.until(EC.element_to_be_clickable((By.ID, 'username')))
        email.send_keys(email_string)

        # Wait for the password input field to be clickable and enter your password
        password = wait.until(EC.element_to_be_clickable((By.ID, 'password')))
        password.send_keys(password_string)

        # Submit the form
        password.send_keys(Keys.RETURN)

        # Wait for the login process to complete
        driver.implicitly_wait(10)  

    except Exception as e:
        print("skipping signin")
        
    # Wait for the "Jobs" link to be clickable based on its href attribute
    jobs_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']"))
    )

    # Click the link
    jobs_link.click()
    print("Clicked the 'Jobs' link.")

    # Wait for the Jobs page to load (optional)
    driver.implicitly_wait(10)  

    # Wait for the "Show all" button/link based on its class name
    show_all_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "discovery-templates-jobs-home-vertical-list__footer"))
    )
    
    # Click the link
    show_all_button.click()
    print("Clicked the 'Show all' link.")

    # Wait for the next page to load (optional)
    driver.implicitly_wait(10)  

    # Find all job card elements within the list
    page_num = 2

    while True:
        try:

            # Wait for the jobs search result list to appear
            job_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
            # Set to keep track of unique job card elements
            job_urls = set()
            all_job_cards = []

            while True:
                # Find all job cards on the current page
                job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container--clickable")
                
                # Add unique job cards to the list
                for job_card in job_cards:
                    job_url = job_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                    if job_url not in job_urls:
                        job_urls.add(job_url)
                        all_job_cards.append(job_card)
                
                # Scroll to the last job card
                if job_cards:
                    driver.execute_script("arguments[0].scrollIntoView();", job_cards[-1])
                
                # Wait for new job cards to load (adjust sleep time if necessary)
                time.sleep(2)
                
                # Find new job cards after scrolling
                new_job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container--clickable")
                
                # Break if no new job cards are loaded
                if len(new_job_cards) == len(job_cards):
                    break  # No new job cards were loaded

            # Now all unique job cards are stored in all_job_cards

            for job_card in all_job_cards:
                try:
                    # Scroll to the job card to ensure visibility
                    driver.execute_script("arguments[0].scrollIntoView();", job_card)
                    
                    # Click the job card to open the job details on the right
                    job_card.click()

                    # Wait for the job details container to appear on the right
                    job_details = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__job-details--wrapper"))
                    )

                    # Check for the "Easy Apply" button inside the job details container
                    try:
                        easy_apply_button = job_details.find_element(By.CLASS_NAME, "jobs-apply-button")
                        if "Easy Apply" in easy_apply_button.text:
                            time.sleep(2)
                            # If the button contains "Easy Apply", click it using JavaScript
                            driver.execute_script("arguments[0].click();", easy_apply_button)
                            print("Clicked Easy Apply for job.")
                            time.sleep(2)
                        else:
                            raise Exception()

                    except Exception as e:
                        print("No Easy Apply button found for this job.")
                        continue

                    # Check if the "Continue Applying" button appears in a popup
                    try:
                        continue_apply_button = job_details.find_element(By.CLASS_NAME, "jobs-apply-button")
                        if "Continue Applying" in continue_apply_button.text:
                            time.sleep(2)
                            # If the button contains "Easy Apply", click it using JavaScript
                            driver.execute_script("arguments[0].click();", continue_apply_button)
                            print("Clicked continue_apply_button for job.")
                            time.sleep(2)
                            easy_apply_button = job_details.find_element(By.CLASS_NAME, "jobs-apply-button")
                            if "Easy Apply" in easy_apply_button.text:
                                # If the button contains "Easy Apply", click it using JavaScript
                                driver.execute_script("arguments[0].click();", easy_apply_button)
                                print("Clicked Easy Apply for job.")

                    except Exception as e:
                        # If no "Continue Applying" button is found, continue to the next step
                        print("No 'Continue Applying' button found for this job.")
                    countattempts = 0
                    while True:
                        if countattempts > 10:
                            press_escape_key()
                            driver.implicitly_wait(2)
                            click_discard_button()
                            driver.implicitly_wait(2)
                            break
                        countattempts += 1
                        parent_div = driver.find_element(By.CLASS_NAME, "jobs-easy-apply-content")
                        try:
                            textboxes = parent_div.find_elements(By.XPATH, ".//input[@type='text']")
                    
                            for textbox in textboxes:
                                # Check if the textbox is empty
                                if textbox.get_attribute('value') == "":
                                    # Get the ID of the textbox
                                    textbox_id = textbox.get_attribute('id')
                                    
                                    # Find the associated label using the 'for' attribute
                                    label = driver.find_element(By.XPATH, f"//label[@for='{textbox_id}']")

                                    textbox.send_keys(call_assistant_api(label.text))

                            dropdowns = parent_div.find_elements(By.TAG_NAME, "select")
                            
                            for dropdown in dropdowns:
                                # Check if any option is selected
                                selected_option = dropdown.get_attribute("value")
                                
                                if selected_option == "" or selected_option == "Select an option":  # If no option is selected (assuming empty value is "")
                                    # Get the ID of the dropdown
                                    dropdown_id = dropdown.get_attribute('id')
                                    
                                    # Find the associated label using the 'for' attribute
                                    label = driver.find_element(By.XPATH, f"//label[@for='{dropdown_id}']")
                                    returnText = call_assistant_api(label.text)
                                    if "yes" in returnText.lower():
                                        dropdown.send_keys("yes")
                                    elif "no" in returnText.lower():
                                        dropdown.send_keys("no")
                                    else:
                                        dropdown.send_keys(returnText)
                                    
                                    

                            radio_groups = {}
                    
                            # Get all radio button inputs
                            radio_buttons = parent_div.find_elements(By.XPATH, ".//input[@type='radio']")
                            
                            # Group radio buttons by their 'name' attribute
                            for radio in radio_buttons:
                                name = radio.get_attribute("name")
                                if name not in radio_groups:
                                    radio_groups[name] = []
                                radio_groups[name].append(radio)
                            
                            # Check each group to see if any radio button is selected
                            for group_name, radios in radio_groups.items():
                                selected = any(radio.is_selected() for radio in radios)
                                
                                if not selected:
                                    # If no radio button is selected in the group, find the associated label
                                    # Assuming the label is associated with the first radio button in the group
                                    radio_id = radios[0].get_attribute('id')
                                    label = driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                                    
                                    answer = call_assistant_api(label.text)
                                    if "yes" in answer.lower():
                                        radio_button = driver.find_element(By.XPATH, f"//input[@type='radio' and @name='{group_name}']//following::label[text()='Yes']")
                                    elif "no" in answer.lower():
                                        radio_button = driver.find_element(By.XPATH, f"//input[@type='radio' and @name='{group_name}']//following::label[text()='No']")
                                    else:
                                        radio_button = driver.find_element(By.XPATH, f"//input[@type='radio' and @name='{group_name}']//following::label[text()='"+answer+"']")
                                    
                                    radio_button.click()

                        except Exception as e:
                            print(f"An error occurred: {e}")
                        
                        try:
                            # Try to find and click the button
                            click_continue_button()
                            
                            # Add a small delay to avoid rapid re-clicking if needed
                            driver.implicitly_wait(2)
                        except NoSuchElementException:
                            # Break the loop if the button is not found
                            print("Button no longer exists or process complete.")
                            break

                        
                    try:
                        # Try to find and click the button
                        click_submit_button()
                        driver.implicitly_wait(2)

                        click_done_button()
                        
                        # Add a small delay to avoid rapid re-clicking if needed
                        driver.implicitly_wait(2)
                    except NoSuchElementException:
                        # Break the loop if the button is not found
                        print("Button no longer exists or process complete.")
                    
                    time.sleep(2)

                except:
                    # Break the loop if the button is not found
                    print("Failed to submit application")

             # Dynamically construct the aria-label value for the current page
            aria_label_value = f"Page {page_num}"

            # Find the button with the aria-label for the current page
            button = driver.find_element(By.XPATH, f"//button[@aria-label='{aria_label_value}']")
            
            # Click the button for the current page
            button.click()
            print(f"Clicked button for {aria_label_value}")

            # Optionally add a small wait for the page to load after clicking
            driver.implicitly_wait(10)

            # Increment the page number for the next iteration
            page_num += 1

        except NoSuchElementException:
            # Break the loop when no more pages (buttons) are found
            print(f"No button found for 'Page {page_num}'. Stopping.")
            break
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser session
    print("done")
    time.sleep(100)

