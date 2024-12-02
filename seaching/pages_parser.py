from bs4 import BeautifulSoup
from pymongo import MongoClient, InsertOne
import concurrent.futures
import logging
import time

# MongoDB setup
client = MongoClient("mongodb://adminUser:Aa%4012345678@10.128.0.3:27017/admin")
db = client['pressranger']  # Database name
pages_collection = db['journalists_pages']  # Collection with original HTML content
parser_pages_collection = db['journalists_parser_pages']  # Collection to store parsed data

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create index on 'company_name' and 'href' to speed up duplicate checks
parser_pages_collection.create_index([("journalist", 1), ("href", 1)], unique=True)

# Function to parse HTML and extract href and company names
def parse_publishers(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    parsed_data = []

    # Find all publisher cards
    for item in soup.find_all('div', class_='card-body pl-lg-0 d-flex flex-column'):
        href_tag = item.find('a')
        if href_tag:
            href = href_tag.get('href')
            company_name = href_tag.text.strip()
            parsed_data.append({
                "journalist_name": company_name,
                "href": href
            })
    return parsed_data

# Function to check for duplicates and bulk insert parsed data
def bulk_insert(parsed_data):
    operations = [InsertOne(data) for data in parsed_data]  # Prepare bulk operations
    
    if operations:
        try:
            # Perform bulk insert (ignores duplicates)
            result = parser_pages_collection.bulk_write(operations, ordered=False)
            return result.inserted_count
        except Exception as e:
            # Handle duplicate key errors only and ignore other errors
            if "E11000" in str(e):
                logging.warning(f"Duplicate key error encountered. Continuing with valid inserts.")
            else:
                logging.error(f"Error during bulk insert: {e}")
            return 0
    return 0

# Function to process a single HTML document
def process_single_document(doc):
    html_content = doc.get("content")
    if html_content:
        parsed_data = parse_publishers(html_content)
        inserted_count = bulk_insert(parsed_data)
        return inserted_count
    return 0

# Function to handle parallel parsing
def process_html_parallel(documents):
    total_inserted = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:  # Increased parallelism
        futures = {executor.submit(process_single_document, doc): doc for doc in documents}
        for future in concurrent.futures.as_completed(futures):
            inserted = future.result()
            total_inserted += inserted
            logging.info(f"Inserted {inserted} new records. Total so far: {total_inserted}")
    return total_inserted

# Retrieve data in bulk from the parser_pages collection
def retrieve_bulk_data(limit=100):
    return list(parser_pages_collection.find().limit(limit))

# Main function to process all documents
def main():
    start_time = time.time()

    # Fetch all HTML documents from MongoDB (you can paginate this if needed)
    documents = list(pages_collection.find({}))  # You can add filters if necessary
    
    if not documents:
        logging.info("No HTML content found in MongoDB.")
        return

    # Process the documents in parallel and insert parsed data
    total_inserted = process_html_parallel(documents)
    logging.info(f"Total inserted documents: {total_inserted}")

    # Retrieve and print bulk data to verify
    retrieved_data = retrieve_bulk_data()
    for entry in retrieved_data:
        print(entry)

    end_time = time.time()
    logging.info(f"Processing completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
