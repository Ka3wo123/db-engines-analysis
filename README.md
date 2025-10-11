# Analytical Comparison of RDBMS and NoSQL – CRUD Performance

This project analyzes and compares the **CRUD performance** of popular **RDBMS** and **noSQL** databases. \
The aim is to check performance for data at a big scale (from thousands to billions). \
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
git clone git@github.com:Ka3wo123/db-engines-analysis.git
cd FraudDetection
```
2. Setup virtual environment for Python
```
python3 -m venv .venv
source .venv/bin/activate # Linux/MacOS
.venv\Scripts\activate    # Windows PowerShell
```
3. Run `pip install -r requirements.txt` to install required dependencies and libraries (when adding new dependencies make sure to freeze them in requirements.txt file `pip freeze > requirements.txt`)
4. In `docker` directory run `docker-compose up -d` to create and start database engines containers.
5. Run `main.py` file via `python3 main.py` to generate schemas in particular databases.

If `main.py` executes successfully you can check that in databases there are schemas created accordingly. \
Schemas for **PostgreSQL** and **MySQL** are defined in `sql` directory and are created using volumes in `docker-compose.yml`. \
Schemas for **Cassandra** and **Neo4j** are defined in `cql` and `cypher` respectively and are created using `main.py` script.

**PostgreSQL**:
- `docker exec -it postgresql15 psql -U postgres -d frauddb`
- `\d` to show entities

**MySQL**:
- `docker exec -it mysql8 mysql -u root -pmysqlrootpass frauddb`
- `show tables` to show entities

**Cassandra**:
- `docker exec -it cassandra4 cqlsh -u cassandra -p cassandra`
- `describe keyspaces` - should be "fraud"
- `select * from fraud.transactions` - should return empty transactions table

**Neo4j**:
- `docker exec -it neo4j5 cypher-shell -u neo4j -p "cg8&fhjs10LOz"`
- `CALL db.labels();` to show nodes
- `CALL db.relationshipTypes();` to show edges

> Keep in mind to do this **OUTSIDE** venv. Run `deactivate` if in .venv.


## GitHub collaboration
 **LOCAL**
1. `git checkout -b new-feature`
2. Add changes + `git add -A ; git commit -m"Message" ; git push origin new-feature`

**REMOTE**
1. Create pull request
2. Wait for approval
3. Compare and rebase branch with master
4. Delete new-feature branch

**LOCAL**
1. `git switch master`
2. `git fetch origin master`
3. `git rebase new-feature`
4. `git branch -D new-feature`