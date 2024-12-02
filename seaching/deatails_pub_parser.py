from bs4 import BeautifulSoup
from pymongo import MongoClient, InsertOne
import concurrent.futures
import logging
import time
import re

# MongoDB setup
client = MongoClient("mongodb://adminUser:Aa%4012345678@10.128.0.3:27017/admin")
db = client['pressranger']  # Database name
pages_collection = db['scraped_pub_pages']  # Collection with original HTML content
parser_pages_collection = db['details_parser_pages']  # Collection to store parsed data

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create index on 'company_name' and 'href' to speed up duplicate checks
parser_pages_collection.create_index([("company_name", 1)], unique=True)

# Function to parse HTML and extract href and company names


    # Find all publisher cards
def parse_publishers(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    parsed_data = []

    # Extract the company name - handle hidden messages and fallback to other headings.
    company_name = None
    company_name_tag = soup.select_one('#app > main > div > div > div:nth-of-type(2) > h1')
    if company_name_tag:
        company_name = company_name_tag.get_text(strip=True)
    # Extract location details - in this structure, it's inside <p> with specific tags.
    location = ', '.join([badge.get_text(strip=True) for badge in soup.select('p > span.badge')])

    # Extract bio or description if available
    bio_tag = soup.find('div', class_='investment-thesis')
    bio = bio_tag.get_text(strip=True) if bio_tag else None

    # Extract email from 'mailto' link
    info_div = soup.find('div', id='info')
    
    # Extract text from all <p> tags within this <div>
    paragraphs = []
    if info_div:
        # Find all <p> tags inside the info div
        p_tags = info_div.find_all('p')
        for p in p_tags:
            # Get the text content of each <p> tag and strip leading/trailing whitespace
            paragraphs.append(p.get_text(strip=True))
    topics=None
    languages=None
    email=None
    website=None
    # print(paragraphs)
    # ['LocationMarche-en-FamenneBelgium', 'Writes about\n                                                                            Defense & Military', 'Writes in\n                                                                            French', '1 Journalist\n                                    Profile', 'Email Addressfratcha.revue@gmail.com', 'Websitehttp://www.fraternellechasseursardennais.be', 'Mark this profile out of date or request updated information.', 'Request updated information on LE CHASSEUR ARDENNAIS by filling out the form\n                        below.']
    for p in paragraphs:
        if '@' in p:
            email = p.replace('Email Address', '')

        elif 'http' in p:
            if 'Website' in p:
                website = p.replace('Website', '')
        elif 'Writes about' in p:
            topics = str(p).split('\n')[1].strip()
        elif 'Writes in' in p:
            languages = str(p).split('\n')[1].strip()
    
    # Extract social media links using known patterns
    social_media_links = {
        'facebook': None,
        'twitter': None,
        'linkedin': None,
        'instagram': None,
        'youtube': None,
        'tiktok': None,
        'pinterest': None
    }

    # Patterns for known social media platforms
    social_media_patterns = {
        'facebook': r'facebook.com',
        'twitter': r'twitter.com',
        'linkedin': r'linkedin.com',
        'instagram': r'instagram.com',
        'youtube': r'(youtube.com|youtu.be)',
        'tiktok': r'tiktok.com',
        'pinterest': r'pinterest.com'
    }

    # Iterate through all anchor tags to find social media links
    for platform, pattern in social_media_patterns.items():
        tag = soup.find('a', href=re.compile(pattern, re.I))
        if tag:
            social_media_links[platform] = tag['href']

   

    # Extract phone numbers from 'tel:' links
    phone_numbers = set()
    phone_tags = soup.find_all('a', href=re.compile(r'tel:', re.I))
    for tag in phone_tags:
        phone_numbers.add(tag.get_text(strip=True))
    phone_numbers = sorted(phone_numbers)


    # Compile all data into a structured dictionary
    parsed_data.append({
        'company_name': company_name,
        'location': location,
        'bio': bio,
        'email': email,
        'website': website,
        'social_media_links': social_media_links,
        'phone_numbers': phone_numbers,
        'topics': topics,
        'languages': languages
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
def main(batch_size=10000):
    start_time = time.time()
    total_inserted = 0

    # Get the total number of documents in the collection
    total_documents = pages_collection.count_documents({})  # Adjust filter if necessary
    logging.info(f"Total documents in the collection: {total_documents}")

    # Process documents in batches
    for offset in range(0, total_documents, batch_size):
        logging.info(f"Processing batch from {offset} to {offset + batch_size}")

        # Fetch the next batch of documents using a limit and skip
        documents = list(pages_collection.find({}).skip(offset).limit(batch_size))

        if not documents:
            logging.info("No more HTML content found in this batch.")
            break

        # Process the documents in parallel and insert parsed data
        inserted_count = process_html_parallel(documents)
        total_inserted += inserted_count
        logging.info(f"Inserted {inserted_count} documents from this batch. Total inserted so far: {total_inserted}")

    end_time = time.time()
    logging.info(f"Total inserted documents: {total_inserted}")
    logging.info(f"Processing completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
