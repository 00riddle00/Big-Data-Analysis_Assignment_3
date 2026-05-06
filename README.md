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
- [Part I — Assignment Specification](#part-i-assignment-specification)
    - [Task 1: Create a NoSQL Database Cluster](#task-1-create-a-nosql-database-cluster)
    - [Task 2: Data Insertion in Parallel](#task-2-data-insertion-in-parallel)
    - [Task 3: Data Noise Filtering in Parallel](#task-3-data-noise-filtering-in-parallel)
    - [Task 4: Calculation of Delta t and Histogram Generation](#task-4-calculation-of-delta-t-and-histogram-generation)
    - [Task 5: Presentation of the Solution](#task-5-presentation-of-the-solution)
    - [Submission Guidelines:](#submission-guidelines)
    - [Note](#note)
- [Part II — Our Implementation](#part-ii-our-implementation)
<!--toc:end-->

# Part I — Assignment Specification

Data set link: http://aisdata.ais.dk/aisdk-2026-04-18.zip

**Assignment Description:** The objective of this assignment is to filter out noise from
a given dataset using NoSQL databases and perform data analysis. The dataset contains
vessel information, and your task is to apply various filters to eliminate noise and
calculate the time difference between data points for each vessel.

### Task 1: Create a NoSQL Database Cluster

- Set up a cluster of NoSQL databases either on your personal machine or on MIF virtual
  machines.
- Configure the cluster and ensure its proper functioning, can be replication setup or
  sharding setup. (sharding will graded higher)
- Docker compose is recommended, but not mandatory

### Task 2: Data Insertion in Parallel

- Implement a program to read data from a CSV file.
- Use separate instances of the MongoClient for each parallel thread or task.
- Please insert in the database such an amount of data that is sufficient to your PC or
  visual machine memory.

### Task 3: Data Noise Filtering in Parallel

- Implement a parallel data noise filtering process that operates on the inserted data.
- Identify and filter out noise based on specific criteria, including vessels with less
  than 100 data points and missing or invalid fields (e.g., Navigational status, MMSI,
  Latitude, Longitude, ROT, SOG, COG, Heading).
- Store the filtered data in a separate collation within the NoSQL databases.
- Consider creating appropriate indexes for efficient filtering.

### Task 4: Calculation of Delta t and Histogram Generation

- Calculate the time difference (delta t) in milliseconds between two subsequent data
  points for each filtered vessel.
- Generate a histogram based on the calculated delta t values.
- Analyze the histogram to gain insights into vessel behavior.

### Task 5: Presentation of the Solution

- Record a short video, where you showcase one of the Mongo database instance failures
  and how it's continued to work.

### Submission Guidelines

- Upload the code and solution to the "Big data analysis".
- Late submissions will be penalized by deducting 0.5 points from the total score per
  hour.

### Note

All groups have the same assignment version, and collaboration within the group is
encouraged. Good luck with the assignment!

---

# Part II — Our Implementation

