from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
from time import sleep
from configuration.config import get_chrome_options  # Updated import
from information import EMAIL, PASSWORD

# Use the Service object with options
service = Service(executable_path="./chromedriver.exe")
browser = webdriver.Chrome(service=service, options=get_chrome_options())

# Open facebook website
browser.get('https://www.facebook.com/')

# Wait for login elements to be present
wait = WebDriverWait(browser, 10)
email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
password_field = wait.until(EC.presence_of_element_located((By.ID, "pass")))

# Enter login information
email_field.send_keys(EMAIL)
password_field.send_keys(PASSWORD)

# Click login and wait
login_button = browser.find_element(By.NAME, "login")
login_button.click()

# Wait longer for login to complete
sleep(10)

# Save cookies
pickle.dump(browser.get_cookies(), open("my_cookies.pkl", "wb"))
print("Cookies saved successfully!")

browser.close()