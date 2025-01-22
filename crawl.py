from configuration import (
    login, login_mobile, get_post_links, get_captions_emojis,
    get_comments, get_image_urls, download_images, click_see_more,
    get_captions_spe, click_see_less, click_see_all, click_view_more_comments,
    get_video_urls, download_videos, get_captions_reel, click_comment_button,
    extract_facebook_post_id, save_text
)
from time import time, sleep
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from pages import PAGES
import subprocess
from configuration.logger import Logger
from configuration.report_generator import ReportGenerator
from concurrent.futures import ProcessPoolExecutor, as_completed
import signal
from collections import defaultdict

def crawl(driver, cookies_path, page_link, page_name, logger, headless=False):
    logger.info(f"Starting crawl for {page_name}")
    
    logger.info("Initializing browsers and checking login status...")
    try:
        browser = login(driver, cookies_path, headless=headless)
        browser_mobile = login_mobile(driver, cookies_path, headless=headless)
        logger.success("Login successful")
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return

    logger.info("Getting post URLs...")
    post_urls = get_post_links(browser, page_link)
    if not post_urls:
        logger.error("No posts found or error collecting posts")
        return False
    
    logger.success(f"Found {len(post_urls)} posts to process")

    if not os.path.exists(f"data/{page_name}"):
        os.makedirs(f"data/{page_name}")

    # Statistics tracking
    stats = defaultdict(int)
    stats.update({
        'posts': 0,
        'videos': 0,
        'reels': 0,
        'images': 0,
        'comments': 0,
        'failed': 0
    })

    # Create main progress bar
    main_progress = logger.create_progress_bar(
        f"{page_name}_main",
        len(post_urls),
        f"🔍 Processing {page_name}"
    )

    for url in post_urls:
        try:
            id = extract_facebook_post_id(url)
            folder = f"data/{page_name}/{id}"
            if not os.path.exists(folder):
                os.makedirs(folder)
                
            # Process different types of posts
            if "posts" in url:
                stats['posts'] += 1
                logger.info(f"Processing post {stats['posts']}/{len(post_urls)}")
                browser.get(url)

                captions = get_captions_emojis(browser)
                save_text(captions, f"{folder}/caption.txt")

                comments = get_comments(browser)
                save_text(comments, f"{folder}/comments.txt")

                img_urls = get_image_urls(browser)
                download_images(img_urls, folder)
                stats['images'] += len(img_urls)
                stats['comments'] += len(comments)

            elif "videos" in url:
                stats['videos'] += 1
                logger.info(f"Processing video {stats['videos']}/{len(post_urls)}")
                browser.get(url)

                try:
                    click_see_more(browser)
                except:
                    pass

                captions = get_captions_spe(browser)
                save_text(captions, f"{folder}/caption.txt")

                try:
                    click_see_less(browser)
                except:
                    pass
                

                try:
                    click_see_all(browser)
                    sleep(1)
                except Exception:
                    pass

                while True:
                    try:
                        click_view_more_comments(browser)
                        sleep(0.5)
                    except Exception:
                        break

                comments = get_comments(browser)
                save_text(comments, f"{folder}/comments.txt")
                stats['comments'] += len(comments)

                try:
                    sleep(5)
                    browser_mobile.get(url)
                    sleep(5)
                    video_urls = get_video_urls(browser_mobile)
                    download_videos(video_urls, folder)
                except Exception:
                    continue
            
            elif "reel" in url:
                stats['reels'] += 1
                logger.info(f"Processing reel {stats['reels']}/{len(post_urls)}")
                browser.get(url)

                captions = get_captions_reel(browser)

                save_text(captions, f"{folder}/caption.txt")

                try:
                    click_see_less(browser)
                except:
                    pass


                try:
                    click_see_all(browser)
                    sleep(1)
                except Exception:
                    pass

                click_comment_button(browser)

                while True:
                    try:
                        click_view_more_comments(browser)
                        sleep(0.5)
                    except Exception:
                        break

                comments = get_comments(browser)
                save_text(comments, f"{folder}/comments.txt")
                stats['comments'] += len(comments)

                try:
                    sleep(5)
                    browser_mobile.get(url)
                    sleep(5)
                    video_urls = get_video_urls(browser_mobile)
                    download_videos(video_urls, folder)
                except Exception:
                    pass

            main_progress.update(1)
            
            # Show running statistics
            logger.info(f"Statistics for {page_name}:")
            logger.info(f"📝 Posts: {stats['posts']}")
            logger.info(f"🎥 Videos: {stats['videos']}")
            logger.info(f"📱 Reels: {stats['reels']}")
            logger.info(f"🖼️ Images: {stats['images']}")
            logger.info(f"💬 Comments: {stats['comments']}")
            logger.info(f"❌ Failed: {stats['failed']}")

        except Exception as e:
            stats['failed'] += 1
            logger.warning(f"Failed to process {url}: {str(e)}")
            continue

    main_progress.close()
    
    # Show final statistics
    logger.section(f"Final Statistics for {page_name}")
    logger.success(f"📊 Total processed: {len(post_urls)}")
    logger.success(f"📝 Posts: {stats['posts']}")
    logger.success(f"🎥 Videos: {stats['videos']}")
    logger.success(f"📱 Reels: {stats['reels']}")
    logger.success(f"🖼️ Images: {stats['images']}")
    logger.success(f"💬 Comments: {stats['comments']}")
    logger.error(f"❌ Failed: {stats['failed']}")

    return True

def crawl_page(driver, cookies_path, page, headless=False):
    """Single page crawler function for parallel processing"""
    logger = Logger(f"{page['name']}.log")
    try:
        return crawl(driver, cookies_path, page['link'], page['name'], logger, headless=headless)
    except Exception as e:
        logger.error(f"Failed to process {page['name']}: {str(e)}")
        return False

if __name__ == "__main__":
    logger = Logger()
    driver = "./chromedriver.exe"
    cookies_path = "my_cookies.pkl"
    
    # Handle CTRL+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Check/create cookies
    if not os.path.exists(cookies_path):
        logger.info("Cookies not found. Running save_cookies.py...")
        try:
            subprocess.run(['python', 'save_cookies.py'], check=True)
            logger.success("Cookies created successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create cookies: {str(e)}")
            exit(1)

    total_start = time()
    logger.section("Starting Facebook Crawler")

    # Set headless=False to see the browser window
    headless = False  # Change this to True when running in production
    
    # Parallel processing of pages
    max_workers = min(4, len(PAGES))  # Limit concurrent processes
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all pages for processing
        future_to_page = {
            executor.submit(crawl_page, driver, cookies_path, page, headless): page
            for page in PAGES
        }

        # Process completed pages
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                success = future.result()
                if success:
                    logger.success(f"Completed {page['name']}")
                else:
                    logger.error(f"Failed to process {page['name']}")
            except Exception as e:
                logger.error(f"Error processing {page['name']}: {str(e)}")

    try:
        # Generate reports after crawling
        logger.section("Generating Reports")
        report_gen = ReportGenerator()
        report_path = report_gen.generate_reports()
        logger.success(f"Reports generated successfully at: {report_path}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        total_time = (time() - total_start)/60
        logger.section("Crawl Complete")
        logger.success(f"All pages processed in {total_time:.2f} minutes")