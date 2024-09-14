from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def press_escape_key(driver):
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.ESCAPE)

def click_button_by_xpath(driver, xpath):
    try:
        button = driver.find_element(By.XPATH, xpath)
        button.click()
        return True
    except NoSuchElementException:
        return False

def click_submit_button(driver):
    return click_button_by_xpath(driver, "//button[@aria-label='Submit application']")

def click_continue_button(driver):
    return click_button_by_xpath(driver, "//button[@aria-label='Continue to next step']")

def click_discard_button(driver):
    return click_button_by_xpath(driver, "//button[.//span[text()='Discard']]")

def click_done_button(driver):
    return click_button_by_xpath(driver, "//button[.//span[text()='Done']]")