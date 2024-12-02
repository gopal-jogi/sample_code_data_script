from pymongo import MongoClient, errors

def connect_to_db(uri, db_name):
    """
    Establish a connection to the MongoDB server and return the database object.
    """
    client = MongoClient(uri)
    return client[db_name]

def create_index(collection, field):
    """
    Ensure an index on the specified field to improve query performance.
    """
    collection.create_index(field, unique=True)
    print(f"Index created on '{field}' field.")

def process_documents_in_batches(source_collection, destination_collection, batch_size):
    """
    Process documents from the source collection in batches, remove duplicates based on 'url',
    and insert unique documents into the destination collection.
    
    Args:
        source_collection: MongoDB collection to fetch the documents from.
        destination_collection: MongoDB collection to insert unique documents.
        batch_size: Number of documents to process in each batch.
    
    Returns:
        Total number of documents processed and inserted into the destination collection.
    """
    cursor = source_collection.find({}, no_cursor_timeout=True).batch_size(batch_size)

    documents_processed = 0
    documents_inserted = 0
    batch = []

    for document in cursor:
        # Extract 'url' for deduplication check
        url = document.get('url')
        
        # Skip the document if 'url' is missing
        if not url:
            continue
        
        batch.append(document)

        # Process the batch when it's full
        if len(batch) >= batch_size:
            documents_inserted += insert_unique_documents(destination_collection, batch)
            batch.clear()  # Clear the batch to free memory

        documents_processed += 1

    # Insert any remaining documents after the final batch
    if batch:
        documents_inserted += insert_unique_documents(destination_collection, batch)

    cursor.close()  # Close the cursor to release resources

    return documents_processed, documents_inserted

def insert_unique_documents(collection, documents):
    """
    Insert only unique documents based on 'url' into the destination collection.

    Args:
        collection: MongoDB collection to insert documents into.
        documents: List of documents to filter and insert.

    Returns:
        The number of successfully inserted documents.
    """
    # Extract URLs from the batch for bulk duplicate check
    urls = [doc['url'] for doc in documents if 'url' in doc]

    # Retrieve existing URLs in chunks to avoid performance issues with large datasets
    existing_urls = set()
    for existing_doc in collection.find({"url": {"$in": urls}}, {"url": 1}).batch_size(10000):
        existing_urls.add(existing_doc["url"])

    # Filter out documents that have URLs already present in the destination collection
    unique_documents = [doc for doc in documents if doc['url'] not in existing_urls]

    # Insert the unique documents and return the count of successfully inserted documents
    return insert_documents(collection, unique_documents)

def insert_documents(collection, documents):
    """
    Insert a batch of documents into the collection. Handle duplicate key errors gracefully.

    Args:
        collection: MongoDB collection to insert documents into.
        documents: List of documents to insert.

    Returns:
        The number of successfully inserted documents.
    """
    try:
        if documents:
            collection.insert_many(documents, ordered=False)  # Use ordered=False to continue even on duplicate errors
        return len(documents)
    except errors.BulkWriteError as bwe:
        # Handle duplicate key errors and continue
        write_errors = bwe.details.get('writeErrors', [])
        successful_inserts = len(documents) - len(write_errors)
        print(f"BulkWriteError: {len(write_errors)} duplicate(s) found and skipped.")
        return successful_inserts

def main():
    # MongoDB connection string (replace with your actual URI)
    mongo_uri = "mongodb://b86f17cb557086808ac128d61a67bf7e6cb8abd15845d0d33b9dfe0bcec8c1bc:123507e88d1cfa1b7b2ffe87a50265cb6d47d5529083df46832e08d50236ce64@10.142.0.2:27017/?authMechanism=DEFAULT&authSource=admin"
    
    # Database and collection names
    db_name = 'linkedin_india'
    source_collection_name = 'results'
    destination_collection_name = 'cleaned_results'
    
    # Connect to MongoDB and select the database and collections
    db = connect_to_db(mongo_uri, db_name)
    source_collection = db[source_collection_name]
    destination_collection = db[destination_collection_name]

    # Create an index on 'url' for the destination collection to speed up duplicate checks
    create_index(destination_collection, "url")

    # Define batch size for processing (you can adjust based on memory availability)
    batch_size = 10000

    # Process documents in batches and insert into destination collection
    processed, inserted = process_documents_in_batches(source_collection, destination_collection, batch_size)

    # Print results
    print(f"Processed {processed} documents.",
          f"Inserted {inserted} unique documents into the '{destination_collection_name}' collection.",
          sep="\n")

if __name__ == "__main__":
    main()
