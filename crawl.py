import configuration as cf
from time import time, sleep
import os
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def crawl(driver, cookies_path, page_link, page_name):
    browser = cf.login(driver, cookies_path)
    browser_mobile = cf.login_mobile(driver, cookies_path)

    post_urls, video_urls = cf.get_post_links(browser, page_link)

    if not os.path.exists(f"data/{page_name}"):
        os.makedirs(f"data/{page_name}")

    # Process post URLs
    for url in tqdm(post_urls, desc="Processing Posts"):
        id = cf.extract_facebook_post_id(url)
        folder = f"data/{page_name}/{id}"
        if not os.path.exists(folder):
            os.makedirs(folder)

        browser.get(url)

        captions = cf.get_captions_emojis(browser)
        cf.save_text(captions, f"{folder}/caption.txt")

        comments = cf.get_comments(browser)
        cf.save_text(comments, f"{folder}/comments.txt")

        img_urls = cf.get_image_urls(browser)
        cf.download_images(img_urls, folder)

    # Process video URLs
    for url in tqdm(video_urls, desc="Processing Videos Posts"):
        id = cf.extract_facebook_post_id(url)
        folder = f"data/{page_name}/{id}"
        if not os.path.exists(folder):
            os.makedirs(folder)

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
        

if __name__ == "__main__":
    driver = "./chromedriver.exe"
    cookies_path = "my_cookies.pkl"

    page_link = ""
    page_name = ""

    # End timing the process
    start_time = time()

    crawl(driver, cookies_path, page_link, page_name)
    # End timing the process
    end_time = time()
    elapsed_time = (end_time - start_time)/60

    print(f"Processing completed in {elapsed_time:.2f} minutes.")