#!/usr/bin/env python3

# Task 2: Parallel AIS data insertion into MongoDB sharded cluster.
# Each worker uses its own MongoClient connection to mongos, which routes
# documents to the correct shard based on hashed MMSI.

import csv
import time
from multiprocessing import Pool

from pymongo import ASCENDING, MongoClient
from pymongo.errors import BulkWriteError

MONGOS_HOST = "mongos"
MONGOS_PORT = 27017
DB_NAME = "ais_db"
COLLECTION_RAW = "vessels_raw"
CSV_PATH = "/data_arch/aisdk-2026-04-18.csv"
CHUNK_SIZE = 50_000  # same value found optimal in Assignment 1
NUM_WORKERS = 8


def parse_row(row):
    """Map a raw CSV row to a MongoDB document.

    The Timestamp header in the AIS dataset starts with '# ', so both
    variants are handled. Returns None if MMSI is missing — documents
    without the shard key cannot be routed correctly by mongos.
    """
    try:
        doc = {
            # Timestamp header in raw AIS CSV starts with '# '
            "Timestamp": (row.get("# Timestamp") or row.get("Timestamp", "")).strip(),
            "Type_of_mobile": row.get("Type of mobile", "").strip(),
            "MMSI": row.get("MMSI", "").strip(),
            "Latitude": row.get("Latitude", "").strip(),
            "Longitude": row.get("Longitude", "").strip(),
            "Navigational_status": row.get("Navigational status", "").strip(),
            "ROT": row.get("ROT", "").strip(),
            "SOG": row.get("SOG", "").strip(),
            "COG": row.get("COG", "").strip(),
            "Heading": row.get("Heading", "").strip(),
            "IMO": row.get("IMO", "").strip(),
            "Callsign": row.get("Callsign", "").strip(),
            "Name": row.get("Name", "").strip(),
            "Ship_type": row.get("Ship type", "").strip(),
            "Cargo_type": row.get("Cargo type", "").strip(),
            "Width": row.get("Width", "").strip(),
            "Length": row.get("Length", "").strip(),
            "Type_of_position_fixing_device": (
                row.get("Type of position fixing device", "").strip()
            ),
            "Draught": row.get("Draught", "").strip(),
            "Destination": row.get("Destination", "").strip(),
            "ETA": row.get("ETA", "").strip(),
            "Data_source_type": row.get("Data source type", "").strip(),
            "Size_A": row.get("Size A", "").strip(),
            "Size_B": row.get("Size B", "").strip(),
            "Size_C": row.get("Size C", "").strip(),
            "Size_D": row.get("Size D", "").strip(),
        }
        # MMSI is the shard key — skip rows where it is absent
        if not doc["MMSI"]:
            return None
        return doc
    except Exception:
        return None


def insert_chunk(args):
    """Insert one chunk of documents using a dedicated MongoClient connection."""
    chunk, worker_id = args

    # Each worker opens its own connection — required by spec, avoids
    # connection sharing issues across processes
    client = MongoClient(MONGOS_HOST, MONGOS_PORT)
    collection = client[DB_NAME][COLLECTION_RAW]

    # Parse rows and discard any that failed validation
    docs = [parse_row(row) for row in chunk]
    docs = [d for d in docs if d is not None]

    if not docs:
        client.close()
        return 0

    try:
        # ordered=False lets MongoDB continue past individual failures,
        # maximising throughput on bulk inserts
        result = collection.insert_many(docs, ordered=False)
        inserted = len(result.inserted_ids)
    except BulkWriteError as e:
        # Count only successful inserts from a partially failed batch
        inserted = e.details.get("nInserted", 0)
    finally:
        client.close()

    print(f"[Worker {worker_id:>3}] Inserted {inserted:>6,} documents", flush=True)
    return inserted


def read_chunks(filepath, chunk_size):
    """Stream the CSV file and yield (chunk, worker_id) tuples.

    Uses csv.DictReader to avoid loading the full 3.6 GB file into memory.
    """
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        chunk = []
        worker_id = 0
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                yield (chunk, worker_id)
                chunk = []
                worker_id += 1
        # Yield the final partial chunk if any rows remain
        if chunk:
            yield (chunk, worker_id)


def create_index(host, port, db_name, collection_name):
    """Create MMSI index after bulk insertion.

    Index is created after insertion rather than before — maintaining it
    during bulk inserts would significantly slow down throughput.
    """
    client = MongoClient(host, port)
    client[db_name][collection_name].create_index([("MMSI", ASCENDING)])
    client.close()
    print(f"Index created on MMSI in '{collection_name}'")


def main():
    print("=" * 60)
    print("AIS Parallel Insertion — Task 2")
    print("=" * 60)
    print(f"Workers:    {NUM_WORKERS}")
    print(f"Chunk size: {CHUNK_SIZE:,} rows")
    print(f"Source:     {CSV_PATH}")
    print(f"Target:     {MONGOS_HOST}:{MONGOS_PORT} / {DB_NAME}.{COLLECTION_RAW}")
    print("=" * 60)

    start = time.perf_counter()

    # imap_unordered processes chunks lazily — only one chunk per worker
    # in memory at a time, preventing OOM on large files
    with Pool(NUM_WORKERS) as pool:
        results = list(
            pool.imap_unordered(insert_chunk, read_chunks(CSV_PATH, CHUNK_SIZE))
        )

    total_inserted = sum(results)
    elapsed = time.perf_counter() - start

    print("=" * 60)
    print("Insertion complete.")
    print(f"Total documents inserted: {total_inserted:,}")
    print(f"Time elapsed:             {elapsed:.1f}s")
    print(f"Throughput:               {total_inserted / elapsed:,.0f} docs/sec")
    print("=" * 60)

    # Index created after bulk insertion for maximum throughput
    print("\nCreating index on MMSI...")
    create_index(MONGOS_HOST, MONGOS_PORT, DB_NAME, COLLECTION_RAW)


if __name__ == "__main__":
    main()
