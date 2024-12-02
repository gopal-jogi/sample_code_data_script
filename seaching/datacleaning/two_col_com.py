import sys
import argparse
import asyncio
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import json
import os
import signal
from bson import ObjectId
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
PROGRESS_FILE = 'progress.json'
interrupted = False

def signal_handler(signum, frame):
    global interrupted
    logging.warning("Interrupt signal received. Saving progress and exiting gracefully...")
    interrupted = True

class AsyncMongoDBHandler:
    """Handles asynchronous MongoDB connections and bulk operations."""

    def __init__(self, uri, db_name, collection_name):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = self.connect()
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def connect(self):
        """Connect to MongoDB asynchronously."""
        try:
            client = AsyncIOMotorClient(self.uri)
            logging.info(f"Connected to MongoDB at {self.uri}.")
            return client
        except Exception as e:
            logging.error(f"MongoDB connection error: {e}")
            sys.exit(1)

    async def read_data_in_batches(self, batch_size=1000, last_id=None):
        """Asynchronously read data from MongoDB collection in batches."""
        try:
            query = {}
            if last_id:
                query['_id'] = {'$gt': ObjectId(last_id)}
            cursor = self.collection.find(query).sort('_id', 1).batch_size(batch_size)
            while True:
                batch = await cursor.to_list(length=batch_size)
                if not batch:
                    break
                yield batch
        except Exception as e:
            logging.error(f"Error reading from MongoDB: {e}")
            sys.exit(1)

    async def write_data_in_batches(self, data_batches):
        """Asynchronously write data to MongoDB collection in batches."""
        try:
            async for batch in data_batches:
                if batch:
                    await self.collection.insert_many(batch, ordered=False)
                    logging.info(f"Inserted {len(batch)} documents into '{self.collection_name}'.")
        except Exception as e:
            logging.error(f"Error writing to MongoDB: {e}")
            sys.exit(1)

class DataProcessor:
    """Processes data: removes duplicates within or between datasets."""

    def __init__(self, duplicate_subset=None):
        self.duplicate_subset = duplicate_subset
        self.seen = set()

    async def process_single_batch(self, batch):
        """Process a single batch: clean data and remove duplicates within the batch."""
        df = pd.DataFrame(batch)
        # Data Cleaning: Drop rows with any null values
        df = df.dropna()
        logging.info("Data cleaned (null values dropped).")

        # Remove duplicates within the batch
        if self.duplicate_subset:
            before = len(df)
            df = df.drop_duplicates(subset=self.duplicate_subset)
            after = len(df)
            logging.info(f"Removed {before - after} duplicate records within the batch.")
        return df.to_dict('records')

    async def process_two_batches(self, batch1, batch2):
        """Process two batches: clean data, remove duplicates between batches."""
        df1 = pd.DataFrame(batch1).dropna()
        df2 = pd.DataFrame(batch2).dropna()
        combined_df = pd.concat([df1, df2], ignore_index=True)

        if self.duplicate_subset:
            duplicates = combined_df[self.duplicate_subset].apply(tuple, axis=1)
            unique_mask = ~duplicates.isin(self.seen)
            unique_records = combined_df[unique_mask]
            self.seen.update(duplicates[unique_mask])
            duplicates_removed = combined_df.shape[0] - unique_records.shape[0]
            logging.info(f"Removed {duplicates_removed} duplicate records between batches.")
        else:
            unique_records = combined_df

        return unique_records.to_dict('records')

async def main():
    global interrupted
    # Register the signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(
        description='Flexible MongoDB data processing script with support for single or dual source collections.'
    )
    # Source 1 arguments
    parser.add_argument('--source1-uri', required=True, help='URI of the first source MongoDB.')
    parser.add_argument('--source1-db-name', required=True, help='Database name of the first source.')
    parser.add_argument('--source1-collection-name', required=True, help='Collection name of the first source.')

    # Source 2 arguments (optional)
    parser.add_argument('--source2-uri', help='URI of the second source MongoDB.')
    parser.add_argument('--source2-db-name', help='Database name of the second source.')
    parser.add_argument('--source2-collection-name', help='Collection name of the second source.')

    # Target arguments
    parser.add_argument('--target-uri', required=True, help='URI of the target MongoDB.')
    parser.add_argument('--target-db-name', required=True, help='Target database name.')
    parser.add_argument('--target-collection-name', required=True, help='Target collection name.')

    # Processing arguments
    parser.add_argument('--duplicate-subset', nargs='+', required=True, help='Columns to check for duplicates.')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for processing.')

    args = parser.parse_args()

    # Initialize MongoDB handlers
    source1_db_handler = AsyncMongoDBHandler(
        uri=args.source1_uri,
        db_name=args.source1_db_name,
        collection_name=args.source1_collection_name
    )

    target_db_handler = AsyncMongoDBHandler(
        uri=args.target_uri,
        db_name=args.target_db_name,
        collection_name=args.target_collection_name
    )

    # Initialize Data Processor
    processor = DataProcessor(duplicate_subset=args.duplicate_subset)

    # Load progress if exists
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
        source1_last_id = progress.get('source1_last_id')
        source2_last_id = progress.get('source2_last_id')
        logging.info("Progress file loaded. Resuming from last saved state.")
    else:
        source1_last_id = None
        source2_last_id = None
        logging.info("No progress file found. Starting fresh.")

    # Check if second source is provided
    two_sources = all([args.source2_uri, args.source2_db_name, args.source2_collection_name])

    if two_sources:
        logging.info("Two source collections provided. Proceeding with comparison.")
        source2_db_handler = AsyncMongoDBHandler(
            uri=args.source2_uri,
            db_name=args.source2_db_name,
            collection_name=args.source2_collection_name
        )

        # Create asynchronous generators for source data batches
        source1_batches = source1_db_handler.read_data_in_batches(batch_size=args.batch_size, last_id=source1_last_id)
        source2_batches = source2_db_handler.read_data_in_batches(batch_size=args.batch_size, last_id=source2_last_id)

        # Estimate total documents using estimated_document_count for speed
        source1_estimated = await source1_db_handler.collection.estimated_document_count() - (
            0 if not source1_last_id else await source1_db_handler.collection.count_documents({'_id': {'$gt': ObjectId(source1_last_id)}})
        )
        source2_estimated = await source2_db_handler.collection.estimated_document_count() - (
            0 if not source2_last_id else await source2_db_handler.collection.count_documents({'_id': {'$gt': ObjectId(source2_last_id)}})
        )
        total_docs = source1_estimated + source2_estimated

        # Initialize tqdm progress bar
        pbar = tqdm(total=total_docs, desc="Processing", unit="docs")

        async def merged_batches():
            """Generator that merges batches from two sources, removes duplicates, and yields unique records."""
            global interrupted
            while True:
                if interrupted:
                    break
                try:
                    # Get next batches from both sources
                    batch1 = await source1_batches.__anext__()
                    batch2 = await source2_batches.__anext__()
                except StopAsyncIteration:
                    # If either source is exhausted, break
                    break

                # Process batches to remove duplicates between them
                unique_records = await processor.process_two_batches(batch1, batch2)
                yield unique_records

                # Update progress bar
                pbar.update(len(batch1) + len(batch2))

                # Update progress
                last_id1 = batch1[-1]['_id'] if batch1 else source1_last_id
                last_id2 = batch2[-1]['_id'] if batch2 else source2_last_id
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump({
                        'source1_last_id': str(last_id1),
                        'source2_last_id': str(last_id2)
                    }, f)

            # Process any remaining batches from source1
            async for batch1 in source1_batches:
                if interrupted:
                    break
                unique_records = await processor.process_two_batches(batch1, [])
                yield unique_records
                pbar.update(len(batch1))

                # Update progress
                last_id1 = batch1[-1]['_id'] if batch1 else source1_last_id
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump({
                        'source1_last_id': str(last_id1),
                        'source2_last_id': str(source2_last_id) if source2_last_id else None
                    }, f)

            # Process any remaining batches from source2
            async for batch2 in source2_batches:
                if interrupted:
                    break
                unique_records = await processor.process_two_batches([], batch2)
                yield unique_records
                pbar.update(len(batch2))

                # Update progress
                last_id2 = batch2[-1]['_id'] if batch2 else source2_last_id
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump({
                        'source1_last_id': str(source1_last_id) if source1_last_id else None,
                        'source2_last_id': str(last_id2)
                    }, f)

        # Write unique data to target collection
        await target_db_handler.write_data_in_batches(merged_batches())

        pbar.close()

    else:
        logging.info("Single source collection provided. Proceeding with single-source processing.")
        # Create asynchronous generator for source1 data batches
        source1_batches = source1_db_handler.read_data_in_batches(batch_size=args.batch_size, last_id=source1_last_id)

        # Estimate total documents using estimated_document_count for speed
        if source1_last_id:
            source1_estimated = await source1_db_handler.collection.estimated_document_count() - await source1_db_handler.collection.count_documents({'_id': {'$gt': ObjectId(source1_last_id)}})
        else:
            source1_estimated = await source1_db_handler.collection.estimated_document_count()
        total_docs = source1_estimated

        # Initialize tqdm progress bar
        pbar = tqdm(total=total_docs, desc="Processing", unit="docs")

        async def processed_batches():
            """Generator that processes batches from a single source and yields unique records."""
            global interrupted
            async for batch in source1_batches:
                if interrupted:
                    break
                unique_records = await processor.process_single_batch(batch)
                yield unique_records
                pbar.update(len(batch))

                # Update progress
                last_id = batch[-1]['_id'] if batch else source1_last_id
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump({
                        'source1_last_id': str(last_id)
                    }, f)

        # Write processed data to target collection
        await target_db_handler.write_data_in_batches(processed_batches())

        pbar.close()

    if interrupted:
        logging.warning("Script was interrupted. Progress has been saved.")
    else:
        # Remove progress file upon successful completion
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            logging.info("Progress file removed after successful completion.")

    logging.info('Data processing completed successfully.')

if __name__ == '__main__':
    asyncio.run(main())
