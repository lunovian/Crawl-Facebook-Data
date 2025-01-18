from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pickle
import random
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

def login(driver_path, cookies_path):
    """
    Logs into Facebook using saved cookies, with enhanced bot detection avoidance.

    Args:
        driver_path: Path to the chromedriver executable.
        cookies_path: Path to the file containing saved cookies.

    Returns:
        A Selenium WebDriver instance logged into Facebook.
    """

    options = Options()
    
    # Headless mode (comment out to run with visible browser)
    # options.add_argument("--headless")

    # Stealth options
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Disable certain features that can be used for detection
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Random User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        # ... add more real user agents ...
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Use the Service object to specify the path to chromedriver
    service = Service(executable_path=driver_path)

    # Pass the Service object to the webdriver
    browser = webdriver.Chrome(service=service, options=options)

    # Apply selenium-stealth
    stealth(browser,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    # Open Facebook with initial sleep
    browser.get('https://www.facebook.com/')
    sleep(random.uniform(3, 5))  # Initial longer sleep

    # Load cookies
    try:
        cookies = pickle.load(open(cookies_path, "rb"))
        for cookie in cookies:
            # Ensure the 'sameSite' attribute is set, or it will be ignored by Chrome
            if 'sameSite' not in cookie:
                cookie['sameSite'] = 'None' # You might need 'Strict' or 'Lax' depending on the website and cookie
            if cookie.get('expiry', None) is not None:
                cookie['expiry'] = int(cookie['expiry'])
            browser.add_cookie(cookie)
    except FileNotFoundError:
        print(f"Error: Cookies file not found at {cookies_path}")
        browser.quit()
        return None
    except Exception as e:
        print(f"Error loading cookies: {e}")
        browser.quit()
        return None

    # Refresh with human-like delay
    browser.get('https://www.facebook.com/')
    sleep(random.uniform(2, 4))  # Shorter sleep after refresh

    return browser


def login_mobile(driver_path, cookies_path):
    """
    Logs into Facebook using saved cookies, emulating a mobile device, 
    with enhanced bot detection avoidance.

    Args:
        driver_path: Path to the chromedriver executable.
        cookies_path: Path to the file containing saved cookies.

    Returns:
        A Selenium WebDriver instance logged into Facebook, emulating a mobile device.
    """

    mobile_emulation = {
        "deviceName": "iPhone X"  # Or any other supported device
    }

    options = Options()
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Headless mode (comment out to run with visible browser)
    # options.add_argument("--headless")

    # Stealth options - Important even when emulating a mobile device
    options.add_argument("start-maximized") # Even in mobile emulation, maximizing can be helpful
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Disable certain features that can be used for detection
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Random User-Agent (matching the emulated device)
    user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1", # iPhone
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1", # iPhone
        # Add more user agents for iPhone X or other mobile devices you want to emulate
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Use the Service object to specify the path to chromedriver
    service = Service(executable_path=driver_path)

    # Pass the Service object to the webdriver
    browser = webdriver.Chrome(service=service, options=options)

    # Apply selenium-stealth
    stealth(browser,
            languages=["en-US", "en"],
            vendor="Apple Inc.", # Match vendor to the emulated device
            platform="iPhone",   # Match platform to the emulated device
            webgl_vendor="Apple Inc.", # Or "Google Inc." if you emulate an Android
            renderer="Apple GPU",       # Be sure to use appropriate WebGL renderer for your device
            fix_hairline=True,
            )

    # Open Facebook with initial sleep
    browser.get('https://m.facebook.com/') # Use the mobile version of Facebook
    sleep(random.uniform(3, 5))  # Initial longer sleep

    # Load cookies
    try:
        cookies = pickle.load(open(cookies_path, "rb"))
        for cookie in cookies:
            # Ensure the 'sameSite' attribute is set correctly
            if 'sameSite' not in cookie:
                cookie['sameSite'] = 'None' # Or 'Strict', 'Lax'
            if cookie.get('expiry', None) is not None:
                cookie['expiry'] = int(cookie['expiry'])
            browser.add_cookie(cookie)
    except FileNotFoundError:
        print(f"Error: Cookies file not found at {cookies_path}")
        browser.quit()
        return None
    except Exception as e:
        print(f"Error loading cookies: {e}")
        browser.quit()
        return None

    # Refresh with human-like delay
    browser.get('https://m.facebook.com/') # Use the mobile version of Facebook
    sleep(random.uniform(2, 4))  # Shorter sleep after refresh

    return browser