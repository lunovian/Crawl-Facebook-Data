import configuration as cf
from time import time, sleep
import os
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from colorama import init, Fore, Style
from datetime import datetime
from pages import PAGES
import subprocess
init()

def log_info(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.BLUE}[{timestamp}] ℹ {message}{Style.RESET_ALL}")

def log_success(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.GREEN}[{timestamp}] ✓ {message}{Style.RESET_ALL}")

def log_error(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.RED}[{timestamp}] ✗ {message}{Style.RESET_ALL}")

def check_cookies(cookies_path):
    """Check if cookies exist and create them if not"""
    if not os.path.exists(cookies_path):
        log_info("Cookies not found. Running save_cookies.py to create them...")
        try:
            subprocess.run(['python', 'save_cookies.py'], check=True)
            if os.path.exists(cookies_path):
                log_success("Cookies created successfully")
            else:
                log_error("Failed to create cookies")
                return False
        except subprocess.CalledProcessError as e:
            log_error(f"Error running save_cookies.py: {str(e)}")
            return False
    return True

def crawl(driver, cookies_path, page_link, page_name):
    log_info(f"Starting crawl for {page_name}")
    
    log_info("Initializing browsers and checking login status...")
    try:
        browser = cf.login(driver, cookies_path)
        browser_mobile = cf.login_mobile(driver, cookies_path)
        log_success("Login successful")
    except Exception as e:
        log_error(f"Login failed: {str(e)}")
        return

    log_info("Getting post URLs...")
    post_urls = cf.get_post_links(browser, page_link)
    log_success(f"Found {len(post_urls)} posts to process")

    if not os.path.exists(f"data/{page_name}"):
        os.makedirs(f"data/{page_name}")

    # Process post URLs with enhanced progress bar
    for url in tqdm(post_urls, 
                   desc="Processing Posts",
                   bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
        id = cf.extract_facebook_post_id(url)
        folder = f"data/{page_name}/{id}"
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        if "posts" in url:
            browser.get(url)

            captions = cf.get_captions_emojis(browser)
            cf.save_text(captions, f"{folder}/caption.txt")

            comments = cf.get_comments(browser)
            cf.save_text(comments, f"{folder}/comments.txt")

            img_urls = cf.get_image_urls(browser)
            cf.download_images(img_urls, folder)

        elif "videos" in url:
            browser.get(url)

            try:
                cf.click_see_more(browser)
            except:
                pass

            captions = cf.get_captions_spe(browser)
            cf.save_text(captions, f"{folder}/caption.txt")

            try:
                cf.click_see_less(browser)
            except:
                pass
            

            try:
                cf.click_see_all(browser)
                sleep(1)
            except Exception:
                pass

            while True:
                try:
                    cf.click_view_more_comments(browser)
                    sleep(0.5)
                except Exception:
                    break

            comments = cf.get_comments(browser)
            cf.save_text(comments, f"{folder}/comments.txt")

            try:
                sleep(5)
                browser_mobile.get(url)
                sleep(5)
                video_urls = cf.get_video_urls(browser_mobile)
                cf.download_videos(video_urls, folder)
            except Exception:
                continue
        
        elif "reel" in url:
            browser.get(url)

            captions = cf.get_captions_reel(browser)

            cf.save_text(captions, f"{folder}/caption.txt")

            try:
                cf.click_see_less(browser)
            except:
                pass


            try:
                cf.click_see_all(browser)
                sleep(1)
            except Exception:
                pass

            cf.click_comment_button(browser)

            while True:
                try:
                    cf.click_view_more_comments(browser)
                    sleep(0.5)
                except Exception:
                    break

            comments = cf.get_comments(browser)
            cf.save_text(comments, f"{folder}/comments.txt")

            try:
                sleep(5)
                browser_mobile.get(url)
                sleep(5)
                video_urls = cf.get_video_urls(browser_mobile)
                cf.download_videos(video_urls, folder)
            except Exception:
                pass

        

if __name__ == "__main__":
    driver = "./chromedriver.exe"
    cookies_path = "my_cookies.pkl"

    # Check cookies before starting
    if not check_cookies(cookies_path):
        log_error("Cannot proceed without valid cookies")
        exit(1)

    total_start_time = time()
    log_info("Starting Facebook crawler")

    for i, page in enumerate(PAGES, 1):
        print(f"\n{Fore.CYAN}{'='*50}")
        log_info(f"Processing page {i}/{len(PAGES)}: {page['name']}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
        start_time = time()
        try:
            crawl(driver, cookies_path, page['link'], page['name'])
            elapsed_time = (time() - start_time)/60
            log_success(f"{page['name']} completed in {elapsed_time:.2f} minutes")
        except Exception as e:
            log_error(f"Failed to process {page['name']}: {str(e)}")

    total_time = (time() - total_start_time)/60
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    log_success(f"All pages processed in {total_time:.2f} minutes")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")