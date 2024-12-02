import requests
import threading
import pymongo
import urllib3
import argparse
from queue import Queue
import vobject  # For parsing vCard data

# Disable warnings for insecure HTTPS requests (since verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class QRCodeProcessor:
    def __init__(self, num_threads=2, batch_size=1000, db_name="emp_info"):
        self.num_threads = num_threads
        self.batch_size = batch_size
        self.db_name = db_name
        self.headers = self.get_headers()
        self.base_url_prefix = 'https://hybrid.chkdin.com/visitorv2/downloadVCard/117859/'
        self.q_queue = Queue()
        self.processed_qr_codes = set()
        self.processed_qr_codes_lock = threading.Lock()
        self.mongo_client = pymongo.MongoClient("mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin")
        self.db = self.mongo_client[self.db_name]
        # Collections
        self.success_col = self.db["success_col"]
        self.no_data_col = self.db["no_data_col"]
        self.error_col = self.db["error_col"]
        # Create indexes
        self.success_col.create_index("qr_code", unique=True)
        self.no_data_col.create_index("qr_code", unique=True)
        self.error_col.create_index("qr_code", unique=True)
        self.exception_lock = threading.Lock()
        self.exceptions = []

    def get_headers(self):
        return {
            'Host': 'hybrid.chkdin.com',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-site',
            'Origin': 'https://bts2024.chkdin.com',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 '
                          'Mobile/15E148 Safari/604.1 PWAShell',
            'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyRW1haWwiOiJyYXZpQHppbnRsci5jb20iLCJBUElfVElNRSI6MTczMDcxODM2MX0.lvJtcY1pHe3o7Yz4ZRBe-R2aAFQpL0pEuoL25NQfVtE',
            'Connection': 'keep-alive',
        }

    def load_processed_qr_codes(self):
        # Load existing qr_codes from all collections to avoid re-processing
        with self.processed_qr_codes_lock:
            collections = [self.success_col, self.no_data_col, self.error_col]
            for col in collections:
                cursor = col.find({}, {"qr_code": 1})
                self.processed_qr_codes.update(doc["qr_code"] for doc in cursor)

    def process_qr_codes_batch(self, qr_codes_batch):
        qr_codes_to_process = []
        with self.processed_qr_codes_lock:
            # Exclude qr_codes already processed
            qr_codes_to_process = [code for code in qr_codes_batch if code not in self.processed_qr_codes]
            # Update the set to include these qr_codes
            self.processed_qr_codes.update(qr_codes_to_process)

        success_documents = []
        no_data_documents = []
        error_documents = []

        for qr_code in qr_codes_to_process:
            url = self.base_url_prefix + qr_code
            try:
                # Make the HTTP GET request
                response = requests.get(url, headers=self.headers, verify=False, timeout=5)
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'text/vcard' in content_type or 'text/x-vcard' in content_type:
                        vcard_text = response.text
                        try:
                            # Parse the vCard data
                            vcard = vobject.readOne(vcard_text)
                            # Extract name components safely
                            name_data = {}
                            if hasattr(vcard, 'n') and vcard.n.value:
                                name_data = {
                                    "family": vcard.n.value.family or '',
                                    "given": vcard.n.value.given or '',
                                    "additional": vcard.n.value.additional or '',
                                    "prefix": vcard.n.value.prefix or '',
                                    "suffix": vcard.n.value.suffix or ''
                                }
                            else:
                                name_data = {}

                            data = {
                                "qr_code": qr_code,
                                "full_name": vcard.fn.value if hasattr(vcard, 'fn') else '',
                                "name": name_data,
                                "email": vcard.email.value if hasattr(vcard, 'email') else '',
                                "phone": vcard.tel.value if hasattr(vcard, 'tel') else '',
                                "organization": vcard.org.value[0] if hasattr(vcard, 'org') else '',
                                "title": vcard.title.value if hasattr(vcard, 'title') else ''
                            }
                            # Check if data is sufficient to consider as success
                            print(f"Data for qr_code {qr_code}: {data}")
                            if data["full_name"] or data["email"] or (data["phone"] and data['phone']!='+'):
                                success_documents.append(data)
                                print(f"Prepared success qr_code: {qr_code}")
                            else:
                                # If essential data is missing, store in no_data_col
                                no_data_documents.append({"qr_code": qr_code, "vcard_text": vcard_text})
                                print(f"Prepared no data qr_code: {qr_code}")
                        except Exception as e:
                            print(f"Failed to parse vCard for qr_code {qr_code}: {e}")
                            # Store the error information
                            error_documents.append({
                                "qr_code": qr_code,
                                "error": str(e),
                                "vcard_text": vcard_text
                            })
                            continue
                    else:
                        print(f"Unexpected Content-Type for qr_code {qr_code}: {content_type}")
                        print(f"Response content: {response.text}")
                        # Store the no data information
                        no_data_documents.append({"qr_code": qr_code, "content": response.text})
                        continue
                else:
                    print(f"Received status code {response.status_code} for qr_code {qr_code}")
                    # Store the error information
                    error_documents.append({
                        "qr_code": qr_code,
                        "error": f"HTTP status code {response.status_code}",
                        "response_text": response.text
                    })
            except requests.exceptions.RequestException as e:
                print(f"Request failed for qr_code {qr_code}: {e}")
                # Store the error information
                error_documents.append({"qr_code": qr_code, "error": str(e)})
            except Exception as e:
                print(f"An error occurred for qr_code {qr_code}: {e}")
                # Store the error information
                error_documents.append({"qr_code": qr_code, "error": str(e)})

        # Insert documents into respective collections
        if success_documents:
            try:
                self.success_col.insert_many(success_documents, ordered=False)
                print(f"Inserted {len(success_documents)} documents into success_col.")
            except pymongo.errors.BulkWriteError as bwe:
                self.handle_bulk_write_error(bwe, self.success_col)

        if no_data_documents:
            try:
                self.no_data_col.insert_many(no_data_documents, ordered=False)
                print(f"Inserted {len(no_data_documents)} documents into no_data_col.")
            except pymongo.errors.BulkWriteError as bwe:
                self.handle_bulk_write_error(bwe, self.no_data_col)

        if error_documents:
            try:
                self.error_col.insert_many(error_documents, ordered=False)
                print(f"Inserted {len(error_documents)} documents into error_col.")
            except pymongo.errors.BulkWriteError as bwe:
                self.handle_bulk_write_error(bwe, self.error_col)

    def handle_bulk_write_error(self, bwe, collection):
        write_errors = bwe.details.get('writeErrors', [])
        for error in write_errors:
            if error['code'] == 11000:
                print(f"Duplicate key error for qr_code: {error['op']['qr_code']} in collection {collection.name}")
            else:
                print(f"Bulk write error in collection {collection.name}: {error}")

    def worker(self):
        while True:
            qr_codes_batch = self.q_queue.get()
            if qr_codes_batch is None:
                break
            self.process_qr_codes_batch(qr_codes_batch)
            self.q_queue.task_done()

    def start_workers(self):
        self.threads = []
        for i in range(self.num_threads):
            t = threading.Thread(target=self.worker)
            t.start()
            self.threads.append(t)

    def stop_workers(self):
        # Stop workers
        for i in range(self.num_threads):
            self.q_queue.put(None)
        for t in self.threads:
            t.join()

    def enqueue_qr_codes(self, start=0, end=1000000):
        current_batch = []
        for i in range(start, end):
            qr_code_str = str(i).zfill(6)
            current_batch.append(qr_code_str)

            if len(current_batch) >= self.batch_size:
                self.q_queue.put(current_batch)
                current_batch = []

        # Put any remaining qr_codes into the queue
        if current_batch:
            self.q_queue.put(current_batch)

    def run(self):
        # Load already processed qr_codes
        self.load_processed_qr_codes()

        # Start worker threads
        self.start_workers()

        # Enqueue qr_codes
        self.enqueue_qr_codes()

        # Block until all tasks are done
        self.q_queue.join()

        # Stop workers
        self.stop_workers()

        # Close MongoDB connection
        self.mongo_client.close()

        print("All qr_codes have been processed.")

        if self.exceptions:
            print("\nExceptions encountered during processing:")
            for exc in self.exceptions:
                print(f"qr_code: {exc[0]}, Error: {exc[1]}")

def main():
    parser = argparse.ArgumentParser(description="Process qr_codes and store data in MongoDB.")
    parser.add_argument("--threads", type=int, default=2, help="Number of worker threads.")
    parser.add_argument("--batch_size", type=int, default=1000, help="Size of qr_code batches.")
    parser.add_argument("--start", type=int, default=0, help="Start range of qr_codes.")
    parser.add_argument("--end", type=int, default=1000000, help="End range of qr_codes.")
    parser.add_argument("--db_name", type=str, default="emp_info", help="MongoDB database name.")
    args = parser.parse_args()

    processor = QRCodeProcessor(
        num_threads=args.threads,
        batch_size=args.batch_size,
        db_name=args.db_name
    )
    processor.run()

if __name__ == "__main__":
    main()

