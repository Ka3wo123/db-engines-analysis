import uuid

import psycopg2
from faker import Faker

from measurements.collectors import run_metrics
from measurements.db_config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from measurements.measurement import measure_performance

faker = Faker()


def connection():
    return psycopg2.connect(
        host="localhost",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
    )


def create(records: int = 1000):
    conn = connection()
    cur = conn.cursor()

    user_query = "INSERT INTO users (name, surname, email) VALUES (%s, %s, %s) RETURNING id"
    users = [(faker.first_name(), faker.last_name(), faker.email()) for _ in range(records)]
    cur.executemany(user_query, users)

    cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT %s", (records,))
    user_ids = [row[0] for row in cur.fetchall()]

    transaction_query = """
        INSERT INTO transactions 
        (user_id, amount, is_fraudulent, created_at, receiver_ip_address,
         sender_ip_address, browser_agent, device_id, device_type,
         bank_name, bank_iban, country, currency) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    transactions = [
        (
            faker.random_element(user_ids),
            faker.pydecimal(positive=True, max_value=1_000_000, min_value=0.01, right_digits=2),
            faker.boolean(chance_of_getting_true=1),
            faker.date_time(),
            faker.ipv4_public(),
            faker.ipv4_public(),
            faker.user_agent(),
            str(uuid.uuid4()),
            faker.random_element(['Mobile', 'Desktop', 'Laptop', 'Tablet']),
            faker.company() + " Bank",
            faker.iban(),
            faker.country(),
            faker.currency()[0]
        )
        for _ in range(records)
    ]

    cur.executemany(transaction_query, transactions)
    conn.commit()
    conn.close()

@measure_performance
def read(container):
    conn = connection()
    cur = conn.cursor()
    query = "SELECT * FROM users"

    collect_metrics = run_metrics("postgresql", cur, query, "read")

    conn.close()
    return collect_metrics


@measure_performance
def join(container):
    conn = connection()
    cur = conn.cursor()

    query = """
        SELECT *
        FROM users u
        INNER JOIN transactions t 
        ON u.id = t.user_id       
    """
    collect_metrics = run_metrics("postgresql", cur, query, "join")

    cur.close()
    conn.close()

    return collect_metrics


@measure_performance
def aggregate(container):
    conn = connection()
    cursor = conn.cursor()

    query = """
            SELECT SUM(amount) FROM transactions;                                
        """
    collect_metrics = run_metrics("postgresql", cursor, query, "aggregate")

    cursor.close()
    conn.close()

    return collect_metrics


def update():
    conn = connection()
    cur = conn.cursor()
    query = "UPDATE users SET name='Updated' WHERE id % 10 = 0"

    cur.execute(query)

    conn.commit()
    conn.close()


def delete():
    conn = connection()
    cur = conn.cursor()
    query = "DELETE FROM users WHERE id % 10 = 5"

    cur.execute(query)

    conn.commit()
    conn.close()


def truncate():
    conn = connection()
    cur = conn.cursor()
    query = "TRUNCATE TABLE transactions, users RESTART IDENTITY CASCADE"

    cur.execute(query)

    conn.commit()
    conn.close()
