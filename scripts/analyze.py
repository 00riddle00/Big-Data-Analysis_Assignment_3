#!/usr/bin/env python3

# Task 4: Delta t calculation and histogram generation.
# For each vessel in vessels_filtered, calculates the time difference
# between consecutive AIS pings (delta t) in milliseconds.
# Generates a histogram of all delta t values to reveal vessel
# reporting patterns and detect anomalous transmission intervals.

import time
from datetime import datetime
from multiprocessing import Pool

import matplotlib
import matplotlib.pyplot as plt
from pymongo import MongoClient

# Use non-interactive backend — no display available inside Docker container
matplotlib.use("Agg")

MONGOS_HOST = "mongos"
MONGOS_PORT = 27017
DB_NAME = "ais_db"
COLLECTION_FILTERED = "vessels_filtered"
NUM_WORKERS = 8

# Timestamp format used in the Danish AIS dataset
TIMESTAMP_FORMAT = "%d/%m/%Y %H:%M:%S"

# Output path for the histogram image (inside container)
HISTOGRAM_PATH = "/outputs/delta_t_histogram.png"


def parse_timestamp(ts_str):
    """Parse AIS timestamp string to datetime object.
    Returns None if the string is missing or unparseable.
    """
    if not ts_str:
        return None
    try:
        return datetime.strptime(ts_str.strip(), TIMESTAMP_FORMAT)
    except ValueError:
        return None


def compute_delta_t(args):
    """Compute delta t values for a subset of MMSIs.

    For each vessel, sorts records chronologically and calculates
    the time difference between each consecutive pair of pings
    in milliseconds.

    Args:
        args: tuple of (mmsi_subset, worker_id)

    Returns:
        List of delta t values in milliseconds.
    """
    mmsi_subset, worker_id = args

    client = MongoClient(MONGOS_HOST, MONGOS_PORT)
    collection = client[DB_NAME][COLLECTION_FILTERED]

    delta_ts = []

    for mmsi in mmsi_subset:
        # Fetch all records for this vessel, sorted chronologically
        records = list(
            collection.find({"MMSI": mmsi}, {"Timestamp": 1}).sort("Timestamp", 1)
        )

        # Parse timestamps and filter out unparseable ones
        timestamps = [parse_timestamp(r.get("Timestamp")) for r in records]
        timestamps = [t for t in timestamps if t is not None]

        # Calculate delta t between each consecutive pair of pings
        for i in range(1, len(timestamps)):
            delta = (timestamps[i] - timestamps[i - 1]).total_seconds() * 1000
            # Only keep positive deltas — negative would indicate bad data
            if delta > 0:
                delta_ts.append(delta)

    client.close()

    print(
        f"[Worker {worker_id:>3}] Computed {len(delta_ts):>8,} delta t values",
        flush=True,
    )
    return delta_ts


def get_all_mmsis(host, port, db_name, collection_name):
    """Fetch all distinct MMSIs from the filtered collection."""
    client = MongoClient(host, port)
    mmsis = client[db_name][collection_name].distinct("MMSI")
    client.close()
    return mmsis


def split_mmsis(mmsis, num_workers):
    """Split MMSI list into num_workers roughly equal subsets."""
    size = len(mmsis) // num_workers
    subsets = []
    for i in range(num_workers):
        start = i * size
        end = None if i == num_workers - 1 else start + size
        subsets.append(mmsis[start:end])
    return subsets


def generate_histogram(delta_ts, output_path):
    """Generate and save a histogram of delta t values.

    Uses log scale on Y axis to handle the extreme spike at short
    intervals while keeping the long tail visible.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    capped = [d for d in delta_ts if d <= 3_600_000]

    ax.hist(capped, bins=100, color="steelblue", edgecolor="white", linewidth=0.3)

    # Log scale on Y axis — essential given the massive spike at short intervals
    ax.set_yscale("log")

    ax.set_title("Distribution of Delta t Between Consecutive AIS Pings", fontsize=14)
    ax.set_xlabel("Delta t (time between consecutive pings)", fontsize=12)
    ax.set_ylabel("Frequency (number of ping pairs)\n[log scale]", fontsize=12)

    ax.set_xticks([60_000, 300_000, 600_000, 1_800_000, 3_600_000])
    ax.set_xticklabels(
        ["1min", "5min", "10min", "30min", "1h"],
        fontsize=9,
        rotation=30,
    )

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Histogram saved to '{output_path}'")


def main():
    print("=" * 60)
    print("AIS Delta t Analysis — Task 4")
    print("=" * 60)
    print(f"Workers:  {NUM_WORKERS}")
    print(f"Source:   {DB_NAME}.{COLLECTION_FILTERED}")
    print(f"Output:   {HISTOGRAM_PATH}")
    print("=" * 60)

    print("Fetching distinct MMSIs from filtered collection...")
    mmsis = get_all_mmsis(MONGOS_HOST, MONGOS_PORT, DB_NAME, COLLECTION_FILTERED)
    print(f"Found {len(mmsis):,} vessels")

    subsets = split_mmsis(mmsis, NUM_WORKERS)
    args = [(subset, i) for i, subset in enumerate(subsets)]

    start = time.perf_counter()

    # Each worker returns a list of delta t values
    with Pool(NUM_WORKERS) as pool:
        results = list(pool.imap_unordered(compute_delta_t, args))

    # Flatten results from all workers into a single list
    all_delta_ts = [d for worker_result in results for d in worker_result]

    elapsed = time.perf_counter() - start

    print("=" * 60)
    print("Delta t computation complete.")
    print(f"Total delta t values: {len(all_delta_ts):,}")
    print(f"Min delta t:          {min(all_delta_ts):,.0f} ms")
    print(f"Max delta t:          {max(all_delta_ts):,.0f} ms")
    print(f"Mean delta t:         {sum(all_delta_ts) / len(all_delta_ts):,.0f} ms")
    print(f"Time elapsed:         {elapsed:.1f}s")
    print("=" * 60)

    print("\nGenerating histogram...")
    generate_histogram(all_delta_ts, HISTOGRAM_PATH)


if __name__ == "__main__":
    main()
