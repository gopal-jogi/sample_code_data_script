import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin')  # Replace with your connection string
db = client['tracxn']  # Replace with your database name
collection = db['company_data']  # Replace with your collection name

# Load the _id values from the .json file
with open('ids_to_delete.json', 'r') as f:
    data = json.load(f)
    ids_to_delete = data['ids']

# Define the batch size for deletion
batch_size = 1000  # Adjust this as needed
deleted_count = 0

# Delete the documents in batches
for i in range(0, len(ids_to_delete), batch_size):
    batch_ids = ids_to_delete[i:i + batch_size]
    result = collection.delete_many({"_id": {"$in": batch_ids}})
    deleted_count += result.deleted_count
    print(f"Deleted {result.deleted_count} documents in this batch.")

print(f"Total deleted {deleted_count} documents from the collection using the provided _id values.")
