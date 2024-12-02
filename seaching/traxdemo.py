import json
from pymongo import MongoClient
import itertools
import string

# Connect to MongoDB
client = MongoClient('mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin')  # Replace with your connection string
db = client['tracxn']  # Replace with your database name
collection = db['company_data']  # Replace with your collection name

# Unique identifier for the batch
batch_id = "batch_2024_01"  # Change this for different batches

# Generate 2 million unique combinations
chars = string.ascii_lowercase  # Use string.ascii_letters for both uppercase and lowercase if needed
max_combinations = 2_020_000  # Number of entries to insert
batch_size = 1000  # Number of documents per batch
count = 0
batch_number = 1  # Counter for tracking batches

# Prepare data in batches and insert them into MongoDB
batch = []
ids_to_save = []  # List to store all _id values

for combination in itertools.product(chars, repeat=6):
    if count >= max_combinations:
        break
    unique_id = ''.join(combination)
    demo_data = {
        "_id": unique_id,
        "combination": unique_id,  # Unique combination for each document
        "response": [],  # Empty list for response
        "status": 200  # Status code
    }
    batch.append(demo_data)
    ids_to_save.append(unique_id)  # Save the _id for deletion later
    count += 1

    # Insert when batch is full or at the end of data
    if len(batch) == batch_size or count == max_combinations:
        collection.insert_many(batch)
        print(f"Batch {batch_number} inserted with {len(batch)} documents.")
        batch_number += 1
        batch = []  # Clear the batch for the next set

print(f"Total {count} documents inserted into the collection.")

# Save the _id values to a .json file for later reference
with open('ids_to_delete.json', 'w') as f:
    json.dump({"ids": ids_to_save}, f)

print(f"IDs saved to 'ids_to_delete.json'.")
