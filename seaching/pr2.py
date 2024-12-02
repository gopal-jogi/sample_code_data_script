import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configure logging to help with debugging
logging.basicConfig(level=logging.INFO)

# MongoDB Setup
client = MongoClient("mongodb://adminUser:Aa%4012345678@10.128.0.3:27017/admin")  # Adjust URI as needed
db = client['pressranger']  # Replace 'pressranger' with your database name
collection = db['journalists_pages']  # Replace 'journalists_pages' with your collection name

# Ensure index exists for faster duplicate checking
collection.create_index("page", unique=True)

def create_webdriver():
    """Set up Chrome WebDriver with optimized settings and return the driver instance."""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Headless mode for faster scraping
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--incognito")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)")

        # Disable images and CSS to speed up scraping
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        options.add_experimental_option("prefs", prefs)

        # Use webdriver_manager to handle ChromeDriver installation
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver
    except Exception as e:
        logging.error(f"Error creating WebDriver: {e}")
        raise

def login(driver, email, password):
    """Logs into the website using the provided credentials."""
    login_url = 'https://pressranger.com/login'
    driver.get(login_url)

    try:
        # Wait for the email input field to become visible
        email_field = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "signinSrEmail"))
        )

        # Wait for the password field to become visible
        password_field = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "signinSrPassword"))
        )

        # Input email and password
        email_field.send_keys(email)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        # Wait for the URL to change, indicating successful login
        WebDriverWait(driver, 15).until(EC.url_changes(login_url))
        logging.info("Login successful!")

    except TimeoutException as e:
        logging.error(f"Error during login: {e}")
        with open('error_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.quit()
        raise

def retry_login(driver, email, password, retries=3):
    """Retries the login process if it fails initially."""
    for attempt in range(retries):
        try:
            login(driver, email, password)
            return  # Exit if login is successful
        except Exception as e:
            logging.error(f"Login attempt {attempt + 1} failed: {e}")
            time.sleep(5)  # Wait before retrying
    logging.error("All login attempts failed.")
    driver.quit()
    raise TimeoutException("Unable to login after multiple attempts.")

def scrape_pages(driver):
    """Scrapes pages from the publishers list, checks for duplicates, and stores HTML content in MongoDB."""
    base_url = 'https://pressranger.com/journalists?page='
    pages_to_insert = []
    batch_size = 100  # Store pages in a list for bulk insertion

    for page_num in range(200, 2500):  # Adjust range for actual pagination
        try:
            url = base_url + str(page_num)
            if collection.find_one({"page": page_num}):
                logging.info(f"Page {page_num} already exists, skipping...")
                continue

            driver.get(url)

            # Wait for the page to load
            time.sleep(3)  # Reduced wait time for faster scraping

            # Scrape the page content
            page_source = driver.page_source

            # Add the page content to the list for bulk insertion
            pages_to_insert.append({
                "page": page_num,
                "content": page_source
            })

            logging.info(f"Prepared page {page_num} for insertion")
            if len(pages_to_insert) >= batch_size:
                # Bulk insert into MongoDB
                collection.insert_many(pages_to_insert)
                logging.info(f"Inserted {batch_size} pages into MongoDB")
                pages_to_insert = []  # Reset the list

        except Exception as e:
            logging.error(f"Error on page {page_num}: {e}")
            break

    # Insert any remaining pages into MongoDB
    if pages_to_insert:
        collection.insert_many(pages_to_insert)
        logging.info(f"Inserted remaining pages into MongoDB")

if __name__ == "__main__":
    # Credentials
    email = "zintlr.ltd@gmail.com"  # Replace with your actual email
    password = "Pressranger@123"  # Replace with your actual password

    # Create WebDriver instance
    driver = create_webdriver()

    try:
        # Attempt login with retries
        retry_login(driver, email, password)

        # Scrape and store the pages
        scrape_pages(driver)

    finally:
        # Close the browser after scraping
        driver.quit()

    logging.info("Scraping completed and data stored in MongoDB.")
