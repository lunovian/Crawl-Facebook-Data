from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pickle
from time import sleep
from selenium.webdriver.chrome.options import Options

def login(driver, cookies_path):
    # mobile_emulation = {
    #     "deviceName": "iPhone X"  # Or any other device you want to emulate
    # }
    # options = Options()
    # options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Use the Service object to specify the path to chromedriver
    service = Service(executable_path=driver)

    # Pass the Service object to the webdriver
    browser = webdriver.Chrome(service=service)

    ### Log in to Facebook
    # Open facebook website
    browser.get('https://www.facebook.com/')

    # Stop the program in 5 seconds
    sleep(5)

    # Load cookie from file
    cookies = pickle.load(open(cookies_path, "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)

    # Refresh the browser
    browser.get('https://www.facebook.com/')

    return browser

def login_mobile(driver, cookies_path):

    mobile_emulation = {
        "deviceName": "iPhone X"  # Or any other device you want to emulate
    }
    options = Options()
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Use the Service object to specify the path to chromedriver
    service = Service(executable_path=driver)

    # Pass the Service object to the webdriver
    browser = webdriver.Chrome(service=service, options=options)

    ### Log in to Facebook
    # Open facebook website
    browser.get('https://www.facebook.com/')

    # Stop the program in 5 seconds
    sleep(5)

    # Load cookie from file
    cookies = pickle.load(open(cookies_path, "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)

    # Refresh the browser
    browser.get('https://www.facebook.com/')

    return browser