from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from information import EMAIL, PASSWORD
import pickle
import random
from random import uniform
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from configuration.agents.user_agents import get_random_agent

def get_base_options(headless=False):
    """Enhanced stealth options for Chrome with performance optimizations"""
    options = Options()
    
    # Performance optimizations
    if headless:
        options.add_argument('--headless=new')  # Only add headless if specified
    
    # GPU-specific fixes
    options.add_argument('--disable-gpu-sandbox')
    options.add_argument('--ignore-gpu-blocklist')
    options.add_argument('--disable-gpu')  # Needed for Windows
    options.add_argument('--disable-software-rasterizer')
    
    # Rest of your existing options
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-logging')
    options.add_argument('--disable-in-process-stack-traces')
    options.add_argument('--disable-crash-reporter')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-dev-tools')
    options.add_argument('--disable-cache')
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-offline-load-stale-cache')
    options.add_argument('--disk-cache-size=0')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-translate')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--mute-audio')
    options.add_argument('--no-first-run')
    options.add_argument('--safebrowsing-disable-auto-update')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--pageLoadStrategy=none')  # Don't wait for full page load
    
    # Core stealth settings
    options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Additional stealth arguments
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    
    # Random timezone
    timezones = ['America/New_York', 'Europe/London', 'Asia/Tokyo']
    options.add_argument(f'--timezone={random.choice(timezones)}')
    
    # Add common plugins to appear more human-like
    options.add_argument('--enable-plugins')
    
    return options

def apply_stealth(browser, mobile=False):
    """Enhanced stealth configuration"""
    vendor = "Apple Inc." if mobile else "Google Inc."
    platform = "iPhone" if mobile else "Win32"
    webgl = "Apple Inc." if mobile else "Intel Inc."
    renderer = "Apple GPU" if mobile else "Intel Iris OpenGL Engine"
    
    stealth(browser,
        languages=["en-US", "en"],
        vendor=vendor,
        platform=platform,
        webgl_vendor=webgl,
        renderer=renderer,
        fix_hairline=True,
        run_on_insecure_origins=True,
        
        # Additional stealth parameters
        enable_canvas_fp=True,           # Enable canvas fingerprint
        enable_webgl_fp=True,           # Enable WebGL fingerprint
        enable_audio_fp=True,           # Enable audio fingerprint
        enable_media_codecs=True,       # Enable media codecs
        enable_plugins_enumeration=True  # Enable plugins enumeration
    )
    
    # Additional JavaScript evasions
    browser.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        window.chrome = { runtime: {} };
    """)

def manual_login(browser, mobile=False):
    """Perform manual login when cookies fail"""
    try:
        url = 'https://m.facebook.com/' if mobile else 'https://www.facebook.com/'
        browser.get(url)
        sleep(5)

        wait = WebDriverWait(browser, 20)
        
        # Check if already logged in first
        if is_logged_in(browser, mobile=mobile):
            print("Already logged in!")
            return True

        # Clear and fill email
        email_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
        )
        email_field.clear()
        email_field.send_keys(Keys.CONTROL + "a")  # Select all
        email_field.send_keys(Keys.DELETE)  # Delete selection
        sleep(1)
        email_field.send_keys(EMAIL)
        sleep(uniform(0.5, 1.5))

        # Clear and fill password
        password_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='pass']"))
        )
        password_field.clear()
        password_field.send_keys(Keys.CONTROL + "a")
        password_field.send_keys(Keys.DELETE)
        sleep(1)
        password_field.send_keys(PASSWORD)
        sleep(uniform(0.5, 1.5))

        # Click login with retry
        for _ in range(3):
            try:
                login_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='login']"))
                )
                login_button.click()
                break
            except:
                sleep(2)
                continue

        # Wait for login to complete with longer timeout
        sleep(uniform(10, 15))

        # Verify login success with multiple checks
        if is_logged_in(browser, mobile=mobile):
            print("Login successful!")
            pickle.dump(browser.get_cookies(), open("my_cookies.pkl", "wb"))
            return True
            
        print("Login verification failed")
        return False
            
    except Exception as e:
        print(f"Manual login failed with error: {str(e)}")
        return False

def is_logged_in(browser, mobile=False):
    """Check if currently logged in using multiple selectors"""
    try:
        wait = WebDriverWait(browser, 10)
        
        if mobile:
            # Mobile-specific selectors
            mobile_selectors = [
                "//div[@data-sigil='MTopBlueBarHeader']",
                "//a[@aria-label='Facebook']",
                "//div[@id='MRoot']",
                "//div[contains(@class, '_7om2')]",  # Mobile header class
                "//div[@role='banner']",
                "//a[@href='/home.php']"
            ]
            for selector in mobile_selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    return True
                except:
                    continue

            # Check mobile-specific URLs
            current_url = browser.current_url
            return any(x in current_url for x in ['m.facebook.com/home.php', 'm.facebook.com/?_rdr'])
        else:
            # Desktop selectors
            desktop_selectors = [
                "//div[@role='banner']",
                "//div[@aria-label='Facebook']",
                "//div[contains(@class, 'x1n2onr6')]//a[@aria-label='Facebook']",
                "//div[contains(@class, 'x1lliihq')]",
                "//input[@name='global_typeahead']"
            ]
            for selector in desktop_selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    return True
                except:
                    continue

            # Check desktop URLs
            current_url = browser.current_url
            return "home.php" in current_url or "/?sk=h_chr" in current_url

    except Exception as e:
        print(f"Login check error: {str(e)}")
        return False

def optimize_wait_times(browser):
    """Optimize page load timeouts"""
    browser.set_page_load_timeout(30)
    browser.implicitly_wait(5)
    return browser

def login(driver_path, cookies_path, headless=False):
    """Logs into Facebook using cookies or manual login"""
    try:
        options = get_base_options(headless=headless)
        # Add desktop-specific options
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Update: Use dynamic user agent
        options.add_argument(f"user-agent={get_random_agent(mobile=False)}")

        # Use the Service object to specify the path to chromedriver
        service = Service(executable_path=driver_path)

        # Pass the Service object to the webdriver
        browser = webdriver.Chrome(service=service, options=options)
        browser = optimize_wait_times(browser)
        apply_stealth(browser, mobile=False)

        if os.path.exists(cookies_path):
            # Try cookie login first
            browser.get('https://www.facebook.com/')
            sleep(uniform(2, 3))

            cookies = pickle.load(open(cookies_path, "rb"))
            for cookie in cookies:
                try:
                    if 'sameSite' not in cookie:
                        cookie['sameSite'] = 'None'
                    if cookie.get('expiry', None) is not None:
                        cookie['expiry'] = int(cookie['expiry'])
                    browser.add_cookie(cookie)
                except Exception as e:
                    continue

            browser.get('https://www.facebook.com/')
            sleep(uniform(2, 3))

            if is_logged_in(browser):
                print("Successfully logged in with cookies!")
                return browser
            else:
                print("Cookie login failed, trying manual login...")
        else:
            print("No cookies found, trying manual login...")

        # If we get here, either no cookies or cookie login failed
        if manual_login(browser):
            return browser

        # If all login attempts fail
        browser.quit()
        return None

    except Exception as e:
        print(f"Login error: {str(e)}")
        if 'browser' in locals():
            browser.quit()
        return None

def login_mobile(driver_path, cookies_path, headless=False):
    """
    Logs into Facebook using saved cookies, emulating a mobile device, 
    with enhanced bot detection avoidance.

    Args:
        driver_path: Path to the chromedriver executable.
        cookies_path: Path to the file containing saved cookies.
        headless: Boolean to control headless mode
    """
    try:
        options = get_base_options(headless=headless)
        options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone X"})
        options.add_argument(f"user-agent={get_random_agent(mobile=True)}")

        service = Service(executable_path=driver_path)
        browser = webdriver.Chrome(service=service, options=options)
        apply_stealth(browser, mobile=True)

        if os.path.exists(cookies_path):
            browser.get('https://m.facebook.com/')
            sleep(uniform(2, 3))

            cookies = pickle.load(open(cookies_path, "rb"))
            for cookie in cookies:
                try:
                    if 'sameSite' not in cookie:
                        cookie['sameSite'] = 'None'
                    if cookie.get('expiry', None) is not None:
                        cookie['expiry'] = int(cookie['expiry'])
                    browser.add_cookie(cookie)
                except Exception as e:
                    continue

            browser.get('https://m.facebook.com/')
            sleep(uniform(2, 3))

            if is_logged_in(browser, mobile=True):  # Pass mobile=True here
                print("Successfully logged in mobile with cookies!")
                return browser
            else:
                print("Mobile cookie login failed, trying manual login...")
        else:
            print("No cookies found, trying manual mobile login...")

        if manual_login(browser, mobile=True):
            return browser

        browser.quit()
        return None

    except Exception as e:
        print(f"Mobile login error: {str(e)}")
        if 'browser' in locals():
            browser.quit()
        return None