import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Configure logging to help with debugging
logging.basicConfig(level=logging.INFO)

# MongoDB Setup
client = MongoClient("mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin")  # Adjust URI as needed
db = client['pressranger']  # Replace 'pressranger' with your database name
url_collection = db['parser_pages']  # The collection with the URLs
scraped_collection = db['scraped_pub_pages']  # Collection to store the scraped data
error_collection = db['error_pages']  # New collection to store error URLs

# Ensure indexes are in place for efficient querying
url_collection.create_index("href")
scraped_collection.create_index("url")
error_collection.create_index("url")

def create_webdriver():
    """Set up Chrome WebDriver with faster settings and return the driver instance."""
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
        # Wait for the email input field to be visible
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signinSrEmail"))
        )

        # Find the password field
        password_field = driver.find_element(By.ID, "signinSrPassword")

        # Input email and password
        email_field.send_keys(email)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        # Wait for the URL to change after login
        WebDriverWait(driver, 10).until(EC.url_changes(login_url))
        time.sleep(3)  # Reduced wait time for faster scraping

        logging.info("Login successful!")
    except Exception as e:
        logging.error(f"Error during login: {e}")
        # Save the page source for debugging
        with open('error_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.quit()
        raise

def is_error_page(page_source):
    """Check if the page source indicates an error or anti-scraping measure."""
    # Common indicators of Cloudflare or error pages
    error_indicators = [
        "Attention Required! | Cloudflare",
        "Access denied",
        "Please enable cookies",
        "Service Unavailable",
        "Checking your browser before accessing",
        "One more step",
        "Unauthorized",
        "Forbidden",
        "Error 522",  # Connection timed out
        "Error 521",  # Web server is down
        "Error 524",
        "Just a moment..."  # A timeout occurred
        # Add more indicators as needed
    ]

    for indicator in error_indicators:
        if indicator.lower() in page_source.lower():
            return True
    return False

def scrape_batch(driver, start_index, batch_size):
    """Scrape a batch of URLs starting from the given index and process batch_size URLs."""
    total_scraped = 0
    total_errors = 0
    store_batch = 100

    # Fetch a batch of URLs from url_collection
    urls_cursor = url_collection.find({}).skip(start_index).limit(batch_size)
    urls_to_scrape = []
    url_ids = []  # To keep track of the document IDs in url_collection

    # Collect URLs and their document IDs
    for document in urls_cursor:
        url = document.get("href")
        if url:
            urls_to_scrape.append(url)
            url_ids.append(document["_id"])

    # Bulk check: Find which URLs already exist in scraped_collection
    existing_urls = set()
    if urls_to_scrape:
        existing_urls_cursor = scraped_collection.find({"url": {"$in": urls_to_scrape}}, {"url": 1})
        existing_urls = set(doc["url"] for doc in existing_urls_cursor)

    # Exclude URLs that are already scraped
    urls_to_scrape = [url for url in urls_to_scrape if url not in existing_urls]

    logging.info(f"Total URLs fetched: {len(url_ids)}")
    logging.info(f"URLs already scraped: {len(existing_urls)}")
    logging.info(f"URLs to scrape: {len(urls_to_scrape)}")

    pages_to_insert = []
    error_pages_to_insert = []

    for url in urls_to_scrape:
        try:
            logging.info(f"Scraping URL: {url}")

            # Fetch the page using WebDriver
            driver.get(url)

            # Wait for the page to fully load
            time.sleep(3)  # Adjust as needed

            # Scrape the page content
            page_source = driver.page_source

            # Check if the page is an error page
            if is_error_page(page_source):
                logging.warning(f"Detected error page for URL: {url}")
                # Add to error collection
                error_pages_to_insert.append({
                    "url": url,
                    "reason": "Error page detected",
                    "timestamp": time.time()
                })
                total_errors += 1
                time.sleep(5)  # Add a small delay to avoid detection
                continue  # Skip storing in scraped_collection

            # Add the page content to the list for bulk insertion
            pages_to_insert.append({
                "url": url,
                "content": page_source
            })

            total_scraped += 1

            if len(pages_to_insert) >= store_batch:
                # Insert the scraped data into the scraped_collection
                try:
                    scraped_collection.insert_many(pages_to_insert, ordered=False)
                    logging.info(f"Inserted {len(pages_to_insert)} pages into the scraped_pages collection")
                except Exception as e:
                    logging.error(f"Error inserting pages into MongoDB: {e}")
                pages_to_insert = []

            if len(error_pages_to_insert) >= store_batch:
                # Insert the error data into the error_collection
                try:
                    error_collection.insert_many(error_pages_to_insert, ordered=False)
                    logging.info(f"Inserted {len(error_pages_to_insert)} pages into the error_pages collection")
                except Exception as e:
                    logging.error(f"Error inserting error pages into MongoDB: {e}")
                error_pages_to_insert = []

        except Exception as e:
            logging.error(f"Exception occurred while scraping URL {url}: {e}")
            # Optionally, add to error collection
            error_pages_to_insert.append({
                "url": url,
                "reason": str(e),
                "timestamp": time.time()
            })
            total_errors += 1
            continue  # Skip to the next URL

    if pages_to_insert:
        # Insert the remaining scraped data into the scraped_collection
        try:
            scraped_collection.insert_many(pages_to_insert, ordered=False)
            logging.info(f"Inserted {len(pages_to_insert)} pages into the scraped_pages collection")
        except Exception as e:
            logging.error(f"Error inserting pages into MongoDB: {e}")

    if error_pages_to_insert:
        # Insert the remaining error data into the error_collection
        try:
            error_collection.insert_many(error_pages_to_insert, ordered=False)
            logging.info(f"Inserted {len(error_pages_to_insert)} pages into the error_pages collection")
        except Exception as e:
            logging.error(f"Error inserting error pages into MongoDB: {e}")

    logging.info(f"Total URLs scraped in this batch: {total_scraped}")
    logging.info(f"Total error pages detected in this batch: {total_errors}")

if __name__ == "__main__":
    # Credentials
    email = "zintlr.ltd@gmail.com"  # Replace with your actual email
    password = "Pressranger@123"    # Replace with your actual password

    # Set the start index and batch size
    # Adjust these values based on the script number you're running
    start_index = 0  # Update this value as needed
    batch_size = 120000   # Each script processes 20,000 URLs

    # Create WebDriver instance
    driver = create_webdriver()

    try:
        # Step 2: Login
        login(driver, email, password)

        # Step 3: Scrape and store the pages
        scrape_batch(driver, start_index, batch_size)

    finally:
        # Step 4: Close the browser after scraping
        driver.quit()

    logging.info("Scraping completed. Data stored in MongoDB.")
