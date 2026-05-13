#!/usr/bin/env python3

# Task 3: Parallel noise filtering of AIS data in MongoDB.
# Reads from vessels_raw, filters out noise, and writes clean documents
# to a separate collection (vessels_filtered).
#
# Noise filtering criteria (applied in order):
#   1. Remove records with missing or invalid required fields
#   2. Remove vessels with fewer than 100 valid data points
#
# Filtering is done in parallel — each worker handles a distinct subset
# of MMSIs, using its own MongoClient connection to avoid shared state.

import time
from multiprocessing import Pool

from pymongo import ASCENDING, MongoClient

MONGOS_HOST = "mongos"
MONGOS_PORT = 27017
DB_NAME = "ais_db"
COLLECTION_RAW = "vessels_raw"
COLLECTION_FILTERED = "vessels_filtered"
NUM_WORKERS = 8
MIN_DATAPOINTS = 100

# Required fields — records missing or empty in any of these are discarded
REQUIRED_FIELDS = [
    "Navigational_status",
    "MMSI",
    "Latitude",
    "Longitude",
    "ROT",
    "SOG",
    "COG",
    "Heading",
]


def is_valid_record(doc):
    """Return True if all required fields are present and non-empty."""
    for field in REQUIRED_FIELDS:
        value = doc.get(field, "")
        if not value or value.strip() == "":
            return False
    return True


def filter_worker(args):
    """Filter a subset of MMSIs and write clean documents to vessels_filtered.

    Each worker:
      1. Fetches all records for its assigned MMSIs from vessels_raw
      2. Discards records with missing/invalid required fields
      3. Discards vessels with fewer than MIN_DATAPOINTS valid records
      4. Inserts the remaining clean documents into vessels_filtered

    Args:
        args: tuple of (mmsi_subset, worker_id)

    Returns:
        tuple of (vessels_kept, records_inserted)
    """
    mmsi_subset, worker_id = args

    # Each worker opens its own connection — same pattern as insert.py
    client = MongoClient(MONGOS_HOST, MONGOS_PORT)
    raw = client[DB_NAME][COLLECTION_RAW]
    filtered = client[DB_NAME][COLLECTION_FILTERED]

    vessels_kept = 0
    records_inserted = 0

    for mmsi in mmsi_subset:
        # Fetch all records for this vessel
        records = list(raw.find({"MMSI": mmsi}))

        # Step 1: discard records with missing/invalid required fields
        valid_records = [r for r in records if is_valid_record(r)]

        # Step 2: discard vessels with fewer than MIN_DATAPOINTS valid records
        if len(valid_records) < MIN_DATAPOINTS:
            continue

        # Insert clean records into the filtered collection
        filtered.insert_many(valid_records, ordered=False)
        vessels_kept += 1
        records_inserted += len(valid_records)

    client.close()

    print(
        f"[Worker {worker_id:>3}] "
        f"Kept {vessels_kept:>5} vessels, "
        f"{records_inserted:>8,} records",
        flush=True,
    )
    return (vessels_kept, records_inserted)


def get_all_mmsis(host, port, db_name, collection_name):
    """Fetch the list of all distinct MMSIs from the raw collection."""
    client = MongoClient(host, port)
    mmsis = client[db_name][collection_name].distinct("MMSI")
    client.close()
    return mmsis


def split_mmsis(mmsis, num_workers):
    """Split the MMSI list into num_workers roughly equal subsets."""
    size = len(mmsis) // num_workers
    subsets = []
    for i in range(num_workers):
        start = i * size
        # Last worker gets any remaining MMSIs
        end = None if i == num_workers - 1 else start + size
        subsets.append(mmsis[start:end])
    return subsets


def create_indexes(host, port, db_name, collection_name):
    """Create indexes on the filtered collection for efficient querying.

    MMSI index speeds up delta t calculation in analyze.py.
    Timestamp index speeds up chronological sorting per vessel.
    """
    client = MongoClient(host, port)
    col = client[db_name][collection_name]
    col.create_index([("MMSI", ASCENDING)])
    col.create_index([("Timestamp", ASCENDING)])
    client.close()
    print(f"Indexes created on MMSI and Timestamp in '{collection_name}'")


def main():
    print("=" * 60)
    print("AIS Parallel Filtering — Task 3")
    print("=" * 60)
    print(f"Workers:        {NUM_WORKERS}")
    print(f"Min datapoints: {MIN_DATAPOINTS}")
    print(f"Source:         {DB_NAME}.{COLLECTION_RAW}")
    print(f"Target:         {DB_NAME}.{COLLECTION_FILTERED}")
    print("=" * 60)

    # Fetch all distinct MMSIs and split across workers
    print("Fetching distinct MMSIs...")
    mmsis = get_all_mmsis(MONGOS_HOST, MONGOS_PORT, DB_NAME, COLLECTION_RAW)
    print(f"Found {len(mmsis):,} distinct MMSIs")

    subsets = split_mmsis(mmsis, NUM_WORKERS)
    args = [(subset, i) for i, subset in enumerate(subsets)]

    start = time.perf_counter()

    with Pool(NUM_WORKERS) as pool:
        results = list(pool.imap_unordered(filter_worker, args))

    total_vessels = sum(r[0] for r in results)
    total_records = sum(r[1] for r in results)
    elapsed = time.perf_counter() - start

    print("=" * 60)
    print("Filtering complete.")
    print(f"Vessels kept:    {total_vessels:,}")
    print(f"Records kept:    {total_records:,}")
    print(f"Time elapsed:    {elapsed:.1f}s")
    print("=" * 60)

    # Create indexes on filtered collection for analyze.py
    print("\nCreating indexes on filtered collection...")
    create_indexes(MONGOS_HOST, MONGOS_PORT, DB_NAME, COLLECTION_FILTERED)


if __name__ == "__main__":
    main()
