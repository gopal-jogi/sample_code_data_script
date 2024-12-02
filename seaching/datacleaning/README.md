a. Single Source Processing
Processes data from one source collection, removes duplicates within it, and stores the cleaned data into the target collection.

code
```python data_processor.py \
    --source1-uri "mongodb://localhost:27017" \
    --source1-db-name "source_db" \
    --source1-collection-name "source_collection" \
    --target-uri "mongodb://localhost:27017" \
    --target-db-name "target_db" \
    --target-collection-name "target_collection" \
    --duplicate-subset "id" "email" \
    --batch-size 1000
```

b. Dual Source Processing
Compares two source collections, removes duplicates between them based on specified fields, and stores the unique records into the target collection.

code
```python data_processor.py \
    --source1-uri "mongodb://localhost:27017" \
    --source1-db-name "source_db1" \
    --source1-collection-name "collection1" \
    --source2-uri "mongodb://localhost:27017" \
    --source2-db-name "source_db2" \
    --source2-collection-name "collection2" \
    --target-uri "mongodb://localhost:27017" \
    --target-db-name "target_db" \
    --target-collection-name "merged_collection" \
    --duplicate-subset "id" "email" \
    --batch-size 1000
```