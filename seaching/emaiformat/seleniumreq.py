from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# --- Set Up Selenium WebDriver ---
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
# Uncomment the next line to run in headless mode (without opening a browser window)
# options.add_argument('--headless')

# Set the User-Agent if needed
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(options=options)

try:
    # --- Navigate to the Website ---
    driver.get('https://www.signalhire.com')

    # Wait for the page to load
    time.sleep(2)

    # --- Locate the Search Input ---
    # Adjust the selectors based on the actual HTML structure of the website
    search_input = driver.find_element(By.NAME, 'q')  # Assuming the search input has the name 'q'

    # --- Enter the Search Query ---
    search_query = 'your search term'  # Replace with your actual search term
    search_input.send_keys(search_query)

    # --- Submit the Search ---
    search_input.submit()

    # Wait for the search results to load
    time.sleep(3)

    # --- Retrieve Search Results ---
    # Adjust the selectors based on the actual HTML structure of the search results page
    results = driver.find_elements(By.CSS_SELECTOR, '.result-item')  # Replace with the actual selector

    # --- Process and Print the Results ---
    for result in results:
        title = result.find_element(By.CSS_SELECTOR, '.result-title').text
        link = result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        print(f'Title: {title}')
        print(f'Link: {link}')
        print('---')

finally:
    # --- Close the Driver ---
    driver.quit()
