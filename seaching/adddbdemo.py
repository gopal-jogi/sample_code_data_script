from pymongo import MongoClient
import itertools
import string

# Connect to MongoDB
client = MongoClient('mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin')  # Replace with your connection string
db = client['cleartax']  # Replace with your database name
collection = db['success']  # Replace with your collection name

# Generate all possible 5-character combinations (adjust as needed)
chars = string.ascii_lowercase  # You can use string.ascii_letters for both uppercase and lowercase
max_combinations = 500_0 # Number of entries to insert
batch_size = 1000  # Number of documents per batch
count = 0
batch_number = 1  # Counter to keep track of batches

# Prepare data in batches and insert them into MongoDB
batch = []

for combination in itertools.product(chars, repeat=6):
    if count >= max_combinations:
        break
    demo_data = {
        "_id": ''.join(combination),
        "gstno": ''.join(combination),  # Unique 5-character combination for each document
        "response_json": {
            "status": 200,
            "error": ""
        }
    }
    batch.append(demo_data)
    count += 1

    # Insert when batch is full or at the end of data
    if len(batch) == batch_size or count == max_combinations:
        collection.insert_many(batch)
        print(f"Batch {batch_number} inserted with {len(batch)} documents.")
        batch_number += 1
        batch = []  # Clear the batch for the next set

print(f"Total {count} documents inserted into the collection.")
