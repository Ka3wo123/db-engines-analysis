# Analytical Comparison of RDBMS and NoSQL – CRUD Performance

This project analyzes and compares the **CRUD performance** of popular **RDBMS** and **noSQL** databases. \
The aim is to check performance for data at a big scale. \
All engines are run in Docker containers.

## Databases Used

| Type              | Database           | Port                     | Purpose               |
|-------------------|--------------------|--------------------------|-----------------------|
| RDBMS             | PostgreSQL 15      | 5432                     | Relational benchmark  |
| RDBMS             | MySQL 8            | 3306                     | Relational benchmark  |
| Columnar-oriented | Apache Cassandra 4 | 9042                     | Wide-column benchmark |
| Graph-oriented    | Neo4j 5            | 7474 (HTTP), 7687 (Bolt) | Graph benchmark       |

---

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.13+](https://www.python.org/)

---

## Setup & Run

1. Clone repository and enter rootdir.
    ```
    git clone https://github.com/Ka3wo123/db-engines-analysis.git
    cd FraudDetection
    ```
2. Setup virtual environment for Python
    ```
    python3 -m venv .venv
    source .venv/bin/activate # Linux/MacOS
    .venv\Scripts\activate    # Windows PowerShell
    ```
3. Run `pip install -r requirements.txt` to install required dependencies and libraries (when adding new dependencies
   make sure to freeze them in requirements.txt file `pip freeze > requirements.txt`)
4. In `docker` directory run `docker-compose up -d` to create and start database engines containers.

## Run benchmarks as described below:

- in root dir run `python3 main.py` in order to run benchmarks.
- specifying arguments like `python3 main.py mysql cassandra` runs benchmarks only for MySQL and Cassandra.
- specifying options like `python3 main.py --records=1234` runs benchmarks with provided records amount (default is
  1000).
- e.g. `python3 main.py postgresql --records=10` will run benchmarks on PostgreSQL with 10 records.
- to exclude container resoruces retrieval add `--no-resources` flag

> [!IMPORTANT]
> Cassandra driver on Linux requires such steps in order to work:
> - install `libev` on OS with pacakge manager
> - install dependency with `CFLAGS="-O2" pip install --no-binary :all: cassandra-driver`

# How to add new DQL to measure?
1. In [nosql](measurements/nosql) or [sql](measurements/sql) directories there are python files. Add new function with DQL query for corresponding database.
2. Annotate it with @measure_performance annotation.