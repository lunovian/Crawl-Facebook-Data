from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pickle
from time import sleep

# Use the Service object to specify the path to chromedriver
service = Service(executable_path="./chromedriver.exe")
# or, for automatic finding of the driver :
# service = Service()

# Pass the Service object to the webdriver
browser = webdriver.Chrome(service=service)

### Log in to Facebook
# Open facebook website
browser.get('https://www.facebook.com/')

# Stop the program in 5 seconds
sleep(5)

# Enter the login information
user = browser.find_element(By.ID, "email")
user.send_keys("") # enter your email

password = browser.find_element(By.ID, "pass")
password.send_keys("") # enter your password

# Login
login_button = browser.find_element(By.NAME, "login")
login_button.click()

sleep(25)

pickle.dump(browser.get_cookies(), open("my_cookies.pkl", "wb"))

browser.close()