import psycopg2

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

    users = [
        (faker.first_name(), faker.last_name(), faker.email())
        for _ in range(records)
    ]
    cur.executemany(
        "INSERT INTO users (name, surname, email) VALUES (%s, %s, %s)",
        users
    )
    conn.commit()
    conn.close()


@measure_performance
def read():
    conn = connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    cur.fetchall()
    conn.close()


@measure_performance
def update():
    conn = connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name='Updated' WHERE id % 10 = 0")
    conn.commit()
    conn.close()


@measure_performance
def delete():
    conn = connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id % 10 = 5")
    conn.commit()
    conn.close()


@measure_performance
def truncate():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE transactions, users RESTART IDENTITY CASCADE;")
    conn.commit()
    conn.close()
