import psycopg2

from measurements.collectors import _postgres_collect_metrics, run_metrics
from measurements.measurement import measure_performance
from faker import Faker
from measurements.db_config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

faker = Faker()


def connection():
    return psycopg2.connect(
        host="localhost",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
    )


@measure_performance
def create(records: int = 1000):
    conn = connection()
    cur = conn.cursor()
    query = "INSERT INTO users (name, surname, email) VALUES (%s, %s, %s)"
    users = [(faker.first_name(), faker.last_name(), faker.email()) for _ in range(records)]

    cur.executemany(query, users)

    conn.commit()
    conn.close()


@measure_performance
def read():
    conn = connection()
    cur = conn.cursor()
    query = "SELECT * FROM users"

    collect_metrics = run_metrics("postgresql", cur, query, "read")

    conn.close()
    return collect_metrics


@measure_performance
def update():
    conn = connection()
    cur = conn.cursor()
    query = "UPDATE users SET name='Updated' WHERE id % 10 = 0"

    cur.execute(query)

    conn.commit()
    conn.close()


@measure_performance
def delete():
    conn = connection()
    cur = conn.cursor()
    query = "DELETE FROM users WHERE id % 10 = 5"

    cur.execute(query)

    conn.commit()
    conn.close()

# @measure_performance
# def truncate():
#     conn = connection()
#     cur = conn.cursor()
#     query = "TRUNCATE TABLE transactions, users RESTART IDENTITY CASCADE"
#
#     cur.execute(query)
#
#     conn.commit()
#     conn.close()
