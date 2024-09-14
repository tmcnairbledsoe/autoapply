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
from helpers.environment import load_environment
from helpers.selenium_actions import (
    press_escape_key,
    click_discard_button,
    click_continue_button,
    click_submit_button,
    click_done_button,
    click_button_by_xpath,
)

from chrome_driver.driver_setup import setup_chrome_driver
from api.assistant_api import call_assistant_api

import requests
import zipfile
import os
import sys
import re

# Get sensitive information from environment variables
env = load_environment()

def main():
    # Setup ChromeDriver
    setup_chrome_driver()

    webdriver_path = os.path.join(os.getcwd(), 'chromedriver-win64\\chromedriver.exe')

    service = Service(webdriver_path)

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={env['chrome_profile_path']}")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open LinkedIn login page
        driver.get('https://www.linkedin.com/login')
        wait = WebDriverWait(driver, 10)

        # Login to LinkedIn
        login(driver, wait, env['email'], env['password'])

        # Navigate to the Jobs page
        navigate_to_jobs_page(driver, wait)

        # Apply to jobs listed on the page
        apply_to_jobs(driver, wait)

    finally:
        # Close the browser session
        driver.quit()
        print("Job application process completed.")
        

def login(driver, wait, email_string, password_string):
    """Handles logging into LinkedIn."""
    try:
        email_input = wait.until(EC.element_to_be_clickable((By.ID, 'username')))
        email_input.send_keys(email_string)

        password_input = wait.until(EC.element_to_be_clickable((By.ID, 'password')))
        password_input.send_keys(password_string)
        password_input.send_keys(Keys.RETURN)

        print("Logged into LinkedIn.")
        driver.implicitly_wait(10)  
    except Exception as e:
        print(f"Failed to login: {e}")

def navigate_to_jobs_page(driver, wait):
    """Navigates to the LinkedIn Jobs page."""
    try:
        jobs_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']"))
        )
        jobs_link.click()

        driver.implicitly_wait(10)  
        # Wait for the "Show all" button/link based on its class name
        show_all_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "discovery-templates-jobs-home-vertical-list__footer"))
        )
        
        # Click the link
        show_all_button.click()
        print("Navigated to the Jobs page.")

        # Wait for the next page to load (optional)
        driver.implicitly_wait(10)  
    except Exception as e:
        print(f"Failed to navigate to Jobs page: {e}")

def apply_to_jobs(driver, wait):
    """Automates applying to jobs on LinkedIn."""
    page_num = 2
    while True:
        try:
            # Wait for the jobs search result list to appear
            all_job_cards = get_all_job_cards(driver, wait)

            for job_card in all_job_cards:
                try:
                    # Scroll to the job card to ensure visibility
                    driver.execute_script("arguments[0].scrollIntoView();", job_card)
                    
                    # Click the job card to open the job details on the right
                    job_card.click()

                    # Wait for the job details container to appear on the right
                    job_details = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__job-details--wrapper"))
                    )

                    apply_to_job(driver)

                except Exception as e:
                    print(f"Error while processing job card: {e}")
                    continue

            # Move to the next page of jobs
            if not click_button_by_xpath(driver, f"//button[@aria-label='Page {page_num}']"):
                print(f"No more job pages found after Page {page_num}.")
                break

            print(f"Navigating to page {page_num} of job listings.")
            page_num += 1
            time.sleep(2)

        except Exception as e:
            print(f"Error while applying to jobs: {e}")
            break

def get_all_job_cards(driver, wait):
    wait.until(
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
    return all_job_cards

def apply_to_job(driver):
    """Handles the process of applying to a job using 'Easy Apply'."""
    try:
        easy_apply_button = driver.find_element(By.CLASS_NAME, "jobs-apply-button")
        if "Easy Apply" in easy_apply_button.text:
            driver.execute_script("arguments[0].click();", easy_apply_button)
            print("Clicked 'Easy Apply'.")
            time.sleep(2)
            check_continue(driver)

            # Fill out the application form
            fill_application_form(driver)

            # Submit the application
            click_submit_button(driver)
            driver.implicitly_wait(2)
            click_done_button()
            driver.implicitly_wait(2)
            
            # Add a small delay to avoid rapid re-clicking if needed
            print("Job application submitted.")
        else:
            print("No 'Easy Apply' option for this job.")
    except Exception as e:
        print(f"Error in Easy Apply process: {e}")

def check_continue(driver):
    # Check if the "Continue Applying" button appears in a popup
    try:
        continue_apply_button = driver.find_element(By.CLASS_NAME, "jobs-apply-button")
        if "Continue Applying" in continue_apply_button.text:
            time.sleep(2)
            # If the button contains "Easy Apply", click it using JavaScript
            driver.execute_script("arguments[0].click();", continue_apply_button)
            print("Clicked continue_apply_button for job.")
            time.sleep(2)
            easy_apply_button = driver.find_element(By.CLASS_NAME, "jobs-apply-button")
            if "Easy Apply" in easy_apply_button.text:
                # If the button contains "Easy Apply", click it using JavaScript
                driver.execute_script("arguments[0].click();", easy_apply_button)
                print("Clicked Easy Apply for job.")

    except Exception as e:
        # If no "Continue Applying" button is found, continue to the next step
        print("No 'Continue Applying' button found for this job.")

def fill_application_form(driver):
    """Fills out the job application form using the assistant API."""
    countattempts = 0
    while True:
        if countattempts > 10:
            press_escape_key()
            driver.implicitly_wait(2)
            click_discard_button()
            driver.implicitly_wait(2)
            break
        countattempts += 1
        try:
            parent_div = driver.find_element(By.CLASS_NAME, "jobs-easy-apply-content")

            # Handle text inputs
            textboxes = parent_div.find_elements(By.XPATH, ".//input[@type='text']")
            for textbox in textboxes:
                if textbox.get_attribute('value') == "":
                    textbox_id = textbox.get_attribute('id')
                    label = driver.find_element(By.XPATH, f"//label[@for='{textbox_id}']")
                    textbox.send_keys(call_assistant_api(label.text))
                    print(f"Filled text input for {label.text}")

            # Handle dropdowns
            dropdowns = parent_div.find_elements(By.TAG_NAME, "select")
            for dropdown in dropdowns:
                selected_option = dropdown.get_attribute("value")
                if selected_option == "" or selected_option == "Select an option":
                    dropdown_id = dropdown.get_attribute('id')
                    label = driver.find_element(By.XPATH, f"//label[@for='{dropdown_id}']")
                    returnText = call_assistant_api(label.text)
                    if "yes" in returnText.lower():
                        dropdown.send_keys("yes")
                    elif "no" in returnText.lower():
                        dropdown.send_keys("no")
                    else:
                        dropdown.send_keys(returnText)
                    print(f"Filled dropdown for {label.text}")

            # Handle radio buttons
            radio_groups = {}
            radio_buttons = parent_div.find_elements(By.XPATH, ".//input[@type='radio']")
            for radio in radio_buttons:
                name = radio.get_attribute("name")
                if name not in radio_groups:
                    radio_groups[name] = []
                radio_groups[name].append(radio)

            for group_name, radios in radio_groups.items():
                selected = any(radio.is_selected() for radio in radios)
                if not selected:
                    radio_id = radios[0].get_attribute('id')
                    label = driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                    answer = call_assistant_api(label.text)
                    for radio in radios:
                        if "yes" in answer.lower() and "yes" == radio.get_attribute("value").lower():
                            radio.click()
                            print(f"Selected Yes for {label.text}")
                            break
                        elif "no" in answer.lower() and "no" == radio.get_attribute("value").lower():
                            radio.click()
                            print(f"Selected No for {label.text}")
                            break
                        else:
                            if radio.get_attribute("value").lower() == answer.lower():
                                radio.click()
                                print(f"Selected {answer} for {label.text}")
                                break
                        

            print("Application form filled.")
        except Exception as e:
            print(f"Error while filling application form: {e}")

        try:
            # Try to find and click the button
            click_continue_button()
            
            # Add a small delay to avoid rapid re-clicking if needed
            driver.implicitly_wait(2)
        except NoSuchElementException:
            # Break the loop if the button is not found
            print("Click Continue Button Failed")

                        
if __name__ == "__main__":
    main()