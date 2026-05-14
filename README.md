<!-- vim: set ft=markdown fenc=utf-8 tw=88 nu ai si et ts=2 sw=2: -->

# Assignment 3: Scalable Maritime AIS Noise Filtering and Temporal Analysis with MongoDB Sharding

**Course:** Big Data Analysis (10 ECTS), VU MIF, Spring 2026

**Study program:** MSc Data Science

**Team:** [Gedas Beržinskas](https://github.com/Berzinskass), [Jonas
Adomaitis](https://github.com/JonasIBM), [Tomas
Giedraitis](https://github.com/00riddle00)

## Table of Contents:

<!--toc:start-->
- [Assignment 3: Scalable Maritime AIS Noise Filtering and Temporal Analysis with MongoDB Sharding](#assignment-3-scalable-maritime-ais-noise-filtering-and-temporal-analysis-with-mongodb-sharding)
  - [Table of Contents:](#table-of-contents)
  - [Pinned: Demo: MongoDB Instance Failure and Recovery (Task 5)](#pinned-demo-mongodb-instance-failure-and-recovery-task-5)
- [Part I — Assignment Specification](#part-i-assignment-specification)
  - [Objective](#objective)
  - [Dataset](#dataset)
  - [Instructions](#instructions)
    - [Task 1: Create a NoSQL Database Cluster](#task-1-create-a-nosql-database-cluster)
    - [Task 2: Data Insertion in Parallel](#task-2-data-insertion-in-parallel)
    - [Task 3: Data Noise Filtering in Parallel](#task-3-data-noise-filtering-in-parallel)
    - [Task 4: Calculation of `delta t` and Histogram Generation](#task-4-calculation-of-delta-t-and-histogram-generation)
    - [Task 5: Presentation of the Solution](#task-5-presentation-of-the-solution)
    - [Submission Guidelines](#submission-guidelines)
    - [Note](#note)
  - [Additional - Dataset Schema](#additional-dataset-schema)
- [Part II — Our Implementation](#part-ii-our-implementation)
  - [Development](#development)
<!--toc:end-->

## Pinned: Demo: MongoDB Instance Failure and Recovery (Task 5)

[![MongoDB Failure Recovery Demo](https://img.youtube.com/vi/vY6sZFBE_JU/0.jpg)](https://www.youtube.com/watch?v=vY6sZFBE_JU)

# Part I — Assignment Specification

## Objective

The objective of this assignment is to filter out noise from a given dataset using NoSQL
databases and perform data analysis. The dataset contains vessel information, and your
task is to apply various filters to eliminate noise and calculate the time difference
between data points for each vessel.

## Dataset

Link:
[http://aisdata.ais.dk/aisdk-2026-04-18.zip](http://aisdata.ais.dk/aisdk-2026-04-18.zip)

If browser does not permit to open this HTTP link, you will need to use `wget` or `curl`
to download the dataset. But at first try not clicking on the link, but copying it and
pasting in the browser address bar, that could work.

---

## Instructions

### Task 1: Create a NoSQL Database Cluster

- Set up a cluster of NoSQL databases either on your personal machine or on MIF
  virtual machines.
- Configure the cluster and ensure its proper functioning. This can be either a
  replication setup or a sharding setup (*sharding* will be graded higher).
- `Docker Compose` is recommended, but not mandatory.

### Task 2: Data Insertion in Parallel

- Implement a program to read data from a `CSV` file.
- Use separate instances of the `MongoClient` for each parallel thread or task.
- Please insert into the database an amount of data sufficient for your PC or
  virtual machine memory.

### Task 3: Data Noise Filtering in Parallel

- Implement a parallel data noise filtering process that operates on the
  inserted data.
- Identify and filter out noise based on specific criteria, including vessels
  with fewer than `100` data points and missing or invalid fields (e.g.,
  `Navigational status`, `MMSI`, `Latitude`, `Longitude`, `ROT`, `SOG`, `COG`,
  `Heading`).
- Store the filtered data in a separate `collection` within the NoSQL
  databases.
- Consider creating appropriate indexes for efficient filtering.

### Task 4: Calculation of `delta t` and Histogram Generation

- Calculate the time difference (`delta t`) in milliseconds between two
  subsequent data points for each filtered vessel.
- Generate a histogram based on the calculated `delta t` values.
- Analyze the histogram to gain insights into vessel behavior.

### Task 5: Presentation of the Solution

- Record a short video where you showcase one of the MongoDB database instance
  failures and how the system continues to operate.

### Submission Guidelines

- Upload the code and solution to the *Big data analysis* system.
- Late submissions will be penalized by deducting `0.5` points from the total
  score per hour.

### Note

All groups have the same assignment version, and collaboration within the group is
encouraged. Good luck with the assignment!

---

## Additional - Dataset Schema

The AIS CSV files contain 26 columns:

| #  | Columns in `*.csv` file        | Format                                                                                                       |
| -- | ------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| 1  | Timestamp                      | Timestamp from the AIS basestation, format: `31/12/2015 23:59:59`                                            |
| 2  | Type of mobile                 | Describes what type of target this message is received from (class A AIS Vessel, Class B AIS vessel, etc)    |
| 3  | MMSI                           | MMSI number of vessel                                                                                        |
| 4  | Latitude                       | Latitude of message report (e.g. `57,8794`)                                                                  |
| 5  | Longitude                      | Longitude of message report (e.g. `17,9125`)                                                                 |
| 6  | Navigational status            | Navigational status from AIS message if available, e.g.: `Engaged in fishing`, `Under way using engine`, mv. |
| 7  | ROT                            | Rot of turn from AIS message if available                                                                    |
| 8  | SOG                            | Speed over ground from AIS message if available                                                              |
| 9  | COG                            | Course over ground from AIS message if available                                                             |
| 10 | Heading                        | Heading from AIS message if available                                                                        |
| 11 | IMO                            | IMO number of the vessel                                                                                     |
| 12 | Callsign                       | Callsign of the vessel                                                                                       |
| 13 | Name                           | Name of the vessel                                                                                           |
| 14 | Ship type                      | Describes the AIS ship type of this vessel                                                                   |
| 15 | Cargo type                     | Type of cargo from the AIS message                                                                           |
| 16 | Width                          | Width of the vessel                                                                                          |
| 17 | Length                         | Length of the vessel                                                                                         |
| 18 | Type of position fixing device | Type of positional fixing device from the AIS message                                                        |
| 19 | Draught                        | Draught field from AIS message                                                                               |
| 20 | Destination                    | Destination from AIS message                                                                                 |
| 21 | ETA                            | Estimated Time of Arrival, if available                                                                      |
| 22 | Data source type               | Data source type, e.g. AIS                                                                                   |
| 23 | Size A                         | Length from GPS to the bow                                                                                   |
| 24 | Size B                         | Length from GPS to the stern                                                                                 |
| 25 | Size C                         | Length from GPS to starboard side                                                                            |
| 26 | Size D                         | Length from GPS to port side                                                                                 |

---

# Part II — Our Implementation

## Development

Prerequisites:

- Docker + Docker Compose
- [uv](https://docs.astral.sh/uv/) for Python dependency management

Install dependencies:

```bash
uv sync
```

Lint and auto-fix:

```bash
uv run ruff check --fix .
```

Sort and format imports:

```bash
uv run ruff check --select I --fix .
```

Format code:

```bash
uv run ruff format .
```

Apply Black string processing normalization:

```bash
uv run black .
```

or using full flags:

```bash
uv run black --line-length=88 --preview --enable-unstable-feature=string_processing .
```

