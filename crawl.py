import configuration as cf
from time import time, sleep
import os
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from colorama import init, Fore, Style
from art import text2art
init()

def print_header(page_name):
    header = text2art("FB Crawler", font='block')
    print(Fore.CYAN + header + Style.RESET_ALL)
    print(Fore.GREEN + f"Target Page: {page_name}" + Style.RESET_ALL)
    print("=" * 50 + "\n")

def crawl(driver, cookies_path, page_link, page_name):
    print_header(page_name)
    
    print(Fore.YELLOW + "Initializing browsers..." + Style.RESET_ALL)
    browser = cf.login(driver, cookies_path)
    browser_mobile = cf.login_mobile(driver, cookies_path)

    print(Fore.YELLOW + "Getting post URLs..." + Style.RESET_ALL)
    post_urls = cf.get_post_links(browser, page_link)
    print(Fore.GREEN + f"Found {len(post_urls)} posts to process" + Style.RESET_ALL)

    if not os.path.exists(f"data/{page_name}"):
        os.makedirs(f"data/{page_name}")

    # Process post URLs with enhanced progress bar
    for url in tqdm(post_urls, 
                   desc=Fore.CYAN + "Processing Posts" + Style.RESET_ALL,
                   bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Style.RESET_ALL)):
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
    page_link = "https://www.facebook.com/vinamilkofficial"
    page_name = "vinamilk"

    start_time = time()
    crawl(driver, cookies_path, page_link, page_name)
    end_time = time()
    elapsed_time = (end_time - start_time)/60

    print(Fore.GREEN + "\n" + "=" * 50)
    print(f"✨ Processing completed in {elapsed_time:.2f} minutes! ✨")
    print("=" * 50 + Style.RESET_ALL)