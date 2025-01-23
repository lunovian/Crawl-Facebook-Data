from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from time import sleep
import os
import requests
from selenium.webdriver.common.keys import Keys
import keyboard
import re
from random import uniform, choice
import math
from tqdm import tqdm

__all__ = [
    'get_post_links',
    'get_captions_emojis',
    'get_comments',
    'get_image_urls',
    'download_images',
    'click_see_more',
    'get_captions_spe',
    'click_see_less',
    'click_see_all',
    'click_view_more_comments',
    'get_video_urls',
    'download_videos',
    'get_captions_reel',
    'click_comment_button',
    'extract_facebook_post_id',
    'save_text',
    'handle_video_page',
    'verify_post_collection'
]

def show_all_comments(driver):
    '''Change Most relevant to All comments to show all comments'''

    # Click on the Most relevant button
    view_more_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Most relevant')]")))
    view_more_btn.click()
    # Click on the All comment button
    all_comments = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'All comments')]")))
    all_comments.click()
    # Scroll to the bottom, ensure all comments are loaded
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    return None

def click_see_more(driver):
    '''Click see more to show all captions'''

    # Click on the See more button
    see_more_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "See more") or contains(@aria-label, "See more")]')))
    see_more_btn.click()
    return None

def click_see_less(driver):
    '''Click see less to hide captions'''

    # Click on the See more button
    see_more_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'See less')]")))
    see_more_btn.click()
    return None

def click_comment_button(driver):
    # Locate the "Comment" button by its aria-label
    comment_button = driver.find_element(By.XPATH, '//div[@aria-label="Comment"]')
    comment_button.click()
    return None

def click_view_more_comments(driver):

    view_more_cmts_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'View more comments')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", view_more_cmts_btn)  # Scroll into view
    view_more_cmts_btn.click()
    return None

def click_see_all(driver):
    '''Click See all button to show comments'''

    see_all_btn = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'See all')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", see_all_btn)
    driver.execute_script("arguments[0].click();", see_all_btn)

    return None

def get_comments(driver):
    '''Get comments under a post
    Return:  - list of comments.
    '''
    comments_list = []
    last_comment_count = 0

    while True:
        # Find all comment elements
        comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1n2onr6 x1ye3gou x1iorvi4 x78zum5 x1q0g3np x1a2a7pz') or contains(@class, 'x1n2onr6 xurb0ha x1iorvi4 x78zum5 x1q0g3np x1a2a7pz')]")

        # Scroll to the last comment to trigger loading more
        if len(comments) > 0:
            driver.execute_script("arguments[0].scrollIntoView(true);", comments[-1])
            sleep(2)  # Allow time for new comments to load
        
        # Check if new comments have been loaded
        if len(comments) == last_comment_count:
            break  # No more comments loading

        last_comment_count = len(comments)

    try:
        # Find all "See more" buttons using the class name or any other identifiable property
        see_more_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "x11i0hfl"))  # Replace with your button's class or selector
        )

        # Iterate and click on each button
        for button in see_more_buttons:
            try:
                # Scroll into view if necessary
                ActionChains(driver).move_to_element(button).perform()
                button.click()
                sleep(1)  # Add a short delay to allow content to expand
            except Exception as e:
                print(f"Could not click a button: {e}")

    except:
        pass

    for comment in comments:
        try:
            # Check if comment contains text
            text_ele = comment.find_element(By.XPATH, ".//div[contains(@class, 'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs')]")
            if text_ele:
                text = text_ele.text
                comments_list.append(text)
                
        except Exception as e:
            continue

    return comments_list


def get_captions(driver):
    """
    Crawls Facebook posts and extracts their captions.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        A list of the post's captions.
    """
    captions = []
    caption_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a') or contains(@class, 'x11i5rnm xat24cr x1mh8g0r x1vvkbs xtlvy1s x126k92a')]")
    for caption_element in caption_elements:
        caption = caption_element.text
        captions.append(caption)

    return captions


def get_emojis(driver):
    """
    Crawls a Facebook post's caption, extracting each line and any following emojis.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        A list of all emojis of the Facebook post's caption
    """
    # Find the caption element
    caption_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a') or contains(@class, 'x11i5rnm xat24cr x1mh8g0r x1vvkbs xtlvy1s x126k92a')]")

    # Get all lines and emojis, handling <br> tags for line breaks
    lines_and_emojis = []

    for caption_element in caption_elements:
            # Handle image-based emojis
            try:
                img_elements = caption_element.find_elements(By.XPATH, ".//img")  # Find <img> tags within the element
                if img_elements:
                    for img in img_elements:
                        alt_text = img.get_attribute("alt")
                        if alt_text:
                            lines_and_emojis.append(alt_text)

            except NoSuchElementException:
                pass

    return lines_and_emojis


def get_captions_emojis(driver):
    """
    Extracts text and emojis from Facebook post captions.
    """
    caption_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a') or contains(@class, 'x11i5rnm xat24cr x1mh8g0r x1vvkbs xtlvy1s x126k92a')]")
    
    captions = []
    for caption_element in caption_elements:
        try:
            soup = BeautifulSoup(caption_element.get_attribute("outerHTML"), 'html.parser')
            for div in soup.find_all('div', dir="auto"):
                result = []
                for child in div.descendants:
                    if child.name == 'img' and 'alt' in child.attrs:
                        result.append(child['alt'])  # Extract emoji from 'alt' attribute
                    elif child.name is None:  # This is text
                        text = child.strip()
                        if text:
                            result.append(text)
            
                captions.append(' '.join(result))

        except AttributeError as e:
            print(f"Error processing caption: {e}")

    return captions

def get_captions_spe(driver):
    """
    Extracts text and emojis from Facebook post captions.
    """
    captions = []

    try:
        caption_title = driver.find_element(By.XPATH, "//div[contains(@class, 'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs')]")
        try:
            soup = BeautifulSoup(caption_title.get_attribute("outerHTML"), 'html.parser')
            for div in soup.find_all('div', dir="auto"):
                result = []
                for child in div.descendants:
                    if child.name == 'img' and 'alt' in child.attrs:
                        result.append(child['alt'])  # Extract emoji from 'alt' attribute
                    elif child.name is None:  # This is text
                        text = child.strip()
                        if text:
                            result.append(text)
            
                captions.append(' '.join(result))
        except AttributeError as e:
            print(f"Error processing caption: {e}")
    except:
        pass

    caption_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'x11i5rnm xat24cr x1mh8g0r x1vvkbs xtlvy1s')]")

    for caption_element in caption_elements:
        try:
            soup = BeautifulSoup(caption_element.get_attribute("outerHTML"), 'html.parser')
            for div in soup.find_all('div', dir="auto"):
                result = []
                for child in div.descendants:
                    if child.name == 'img' and 'alt' in child.attrs:
                        result.append(child['alt'])  # Extract emoji from 'alt' attribute
                    elif child.name is None:  # This is text
                        text = child.strip()
                        if text:
                            result.append(text)
            
                captions.append(' '.join(result))
        except AttributeError as e:
            print(f"Error processing caption: {e}")

    return captions

def get_captions_reel(driver):

    captions = []

    try:
        click_see_more(driver)
    except:
        pass

    try:

        caption_title = driver.find_element(By.XPATH, "//div[contains(@class, 'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a') ]")

        # print(caption_element.get_attribute("outerHTML"))

        # Parse the HTML
        soup = BeautifulSoup(caption_title.get_attribute("outerHTML"), 'html.parser')

        # Extract caption text
        caption_div = soup.find("div", class_="xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a")
        caption_text = caption_div.get_text(separator=" ").strip()

        # Remove "See less" if present
        if "See less" in caption_text:
            caption_text = caption_text.replace("See less", "").strip()

        captions.append(caption_text)

    except:
        pass
    
    try:
        captions_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'x11i5rnm xat24cr x1mh8g0r x1vvkbs xtlvy1s x126k92a') ]")

        for captions_element in captions_elements:
            # Parse the HTML
            soup = BeautifulSoup(captions_element.get_attribute("outerHTML"), 'html.parser')

            # Extract caption text
            caption_div = soup.find("div", class_="x11i5rnm xat24cr x1mh8g0r x1vvkbs xtlvy1s x126k92a")
            caption_text = caption_div.get_text(separator=" ").strip()

            # Remove "See less" if present
            if "See less" in caption_text:
                caption_text = caption_text.replace("See less", "").strip()

            captions.append(caption_text)
    except:
        pass

    return captions

def get_image_urls(driver):
    """
    Crawls a Facebook post and extracts image URLs.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        A list of image URLs found in the post.
    """

    # Find image elements
    image_elements = driver.find_elements(By.XPATH, ".//div[contains(@class, 'x10l6tqk x13vifvy') or contains(@class, 'xz74otr x1gqwnh9 x1snlj24')]/img")
    image_urls = []
    for img in image_elements:
        image_urls.append(img.get_attribute('src'))

    return image_urls

def download_images(image_urls, download_dir="images"):
    """
    Downloads images from a list of URLs.

    Args:
        image_urls: A list of image URLs.
        download_dir: The directory to save the images to.
    """
    if not image_urls:
        print("No image URLs provided.")
        return

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            with open(os.path.join(download_dir, f"image_{i+1}.jpg"), "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            # print(f"Downloaded image {i+1} from {url}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from {url}: {e}")

def get_video_urls(driver):

    try:
        # Wait until the button is visible and clickable
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "inline-video-icon"))
        )
        # Click the button
        button.click()

    except Exception as e:
        pass
    
    video_elements = driver.find_elements(By.XPATH, ".//div[contains(@class, 'inline-video-container')]/video")
    video_urls = []
    for video in video_elements:
        src = video.get_attribute("src")
        video_urls.append(src)

    return video_urls

def download_videos(video_urls, download_dir="videos"):
    """
    Downloads videos from a list of URLs.

    Args:
        video_urls: A list of video URLs.
        download_dir: The directory to save the videos to.
    """
    if not video_urls:
        print("No video URLs provided.")
        return

    import os
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for i, url in enumerate(video_urls):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(os.path.join(download_dir, f"video_{i+1}.mp4"), "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # print(f"Downloaded video {i+1} from {url}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading video from {url}: {e}")

def smooth_scroll_to(browser, position, duration=1.0, steps=30):
    """
    Perform a smooth scroll animation to a specific position
    """
    current_pos = browser.execute_script("return window.pageYOffset;")
    distance = position - current_pos
    step_size = distance / steps
    step_duration = duration / steps
    
    for i in range(steps + 1):
        step = i / steps  # Progress from 0 to 1
        # Use easeInOutCubic easing function for smoother motion
        current_step = step * step * (3 - 2 * step)
        current_position = current_pos + (distance * current_step)
        browser.execute_script(f"window.scrollTo(0, {current_position});")
        sleep(step_duration)

def natural_scroll(driver, scroll_type="normal"):
    """Enhanced natural scrolling with better coverage"""
    viewport_height = driver.execute_script("return window.innerHeight")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_position = driver.execute_script("return window.pageYOffset")
    
    # Calculate scroll distance based on viewport
    if scroll_type == "small":
        scroll_distance = uniform(viewport_height * 0.2, viewport_height * 0.4)
    else:
        scroll_distance = uniform(viewport_height * 0.6, viewport_height * 0.8)
    
    # Calculate target position with some randomness
    new_position = min(
        current_position + scroll_distance + uniform(-50, 50),
        scroll_height - viewport_height
    )
    
    # Perform smooth scroll with random duration
    smooth_scroll_to(
        driver,
        new_position,
        duration=uniform(0.8, 1.5),
        steps=int(uniform(25, 35))
    )
    
    # Add natural pause with slight variation
    sleep(uniform(0.3, 0.7))
    
    # Check if reached bottom
    final_position = driver.execute_script("return window.pageYOffset")
    max_scroll = scroll_height - viewport_height
    return final_position >= max_scroll * 0.98

def verify_post_collection(driver, initial_posts):
    """Double check for missed posts"""
    print("\nPerforming verification scan...")
    verified_posts = []
    missed_posts = []
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    sleep(2)
    
    with tqdm(total=len(initial_posts), desc="Verifying posts") as pbar:
        for post in initial_posts:
            try:
                # Check if post is actually accessible
                driver.get(post)
                sleep(uniform(0.3, 0.7))
                
                if not any(x in driver.current_url for x in ['page_not_found', 'login', 'checkpoint']):
                    verified_posts.append(post)
                else:
                    missed_posts.append(post)
                pbar.update(1)
            except:
                missed_posts.append(post)
                pbar.update(1)
                continue
    
    return verified_posts, missed_posts

def get_post_links(driver, fanpage_url):
    """Improved post link collection with double verification"""
    post_urls = []
    verified_urls = []
    scan_count = 0
    max_scans = 2  # Number of verification scans
    
    try:
        # Initial post collection
        driver.get(fanpage_url)
        sleep(uniform(3, 4))
        
        print("Initial post collection...")
        # ...existing post collection code...
        
        # Remove duplicates
        initial_posts = list(set(post_urls))
        print(f"\nInitial collection found {len(initial_posts)} posts")
        
        # First verification scan
        verified_posts, missed_posts = verify_post_collection(driver, initial_posts)
        
        # Additional verification scans if posts were missed
        while missed_posts and scan_count < max_scans:
            scan_count += 1
            print(f"\nPerforming verification scan {scan_count}/{max_scans}")
            print(f"Checking {len(missed_posts)} potentially missed posts...")
            
            # Retry missed posts
            additional_verified, still_missed = verify_post_collection(driver, missed_posts)
            verified_posts.extend(additional_verified)
            missed_posts = still_missed
            
            if not missed_posts:
                print("All posts verified successfully!")
                break
        
        # Final results
        total_verified = len(verified_posts)
        total_missed = len(missed_posts)
        
        print(f"\nFinal Results:")
        print(f"✓ Successfully verified: {total_verified} posts")
        if missed_posts:
            print(f"✗ Could not verify: {total_missed} posts")
        
        return verified_posts

    except Exception as e:
        print(f"Error during post collection: {e}")
        return verified_posts if verified_posts else []

# Add easing function for smooth scrolling
def easeInOutQuad(t):
    """Quadratic easing function for smooth scrolling"""
    return t * t * (3 - 2 * t)

def save_text(text_list, file_path):
    """
    Saves a list of strings to a text file, with each string on a new line.

    Args:
        text_list (list): A list of strings to save.
        file_path (str): The file path where the text will be saved.

    Returns:
        None
    """
    # Save each string in the list to a new line in the file
    with open(file_path, "w", encoding="utf-8") as file:
        for item in text_list:
            file.write(item + "\n")  # Add a newline after each string

    # print(f"Strings saved to {file_path}")

def extract_facebook_post_id(url):
    """
    Extracts the post ID from a Facebook post URL.

    Args:
        url: The Facebook post URL.

    Returns:
        The post ID, or None if no ID could be found.
    """
    match = re.search(r"(?:reel/|posts/|videos/|pfbid)([\w\d]+)", url)
    if match:
        return match.group(1)
    return None

def remove_duplicate_links(links):
    """
    Remove links with duplicate IDs and keep only one for each unique ID.
    """
    unique_links = {}
    for link in links:
        post_id = extract_facebook_post_id(link)
        if post_id and post_id not in unique_links:
            unique_links[post_id] = link
    return list(unique_links.values())

def handle_video_page(driver):
    """Stabilize video page and prevent scrolling"""
    try:
        # Stop video autoplay
        video_elements = driver.find_elements(By.TAG_NAME, "video")
        for video in video_elements:
            driver.execute_script("""
                arguments[0].pause();
                arguments[0].removeAttribute('autoplay');
                arguments[0].muted = true;
            """, video)

        # Disable scroll events
        driver.execute_script("""
            window._scrollEnabled = false;
            window.addEventListener('scroll', function(e) {
                if (!window._scrollEnabled) {
                    e.stopPropagation();
                    e.preventDefault();
                }
            }, true);
        """)
        
        return True
    except Exception as e:
        print(f"Error stabilizing video page: {e}")
        return False