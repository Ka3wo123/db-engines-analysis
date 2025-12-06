import uuid

import mysql.connector
from faker import Faker

from measurements.collectors import run_metrics
from measurements.db_config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from measurements.measurement import measure_performance

faker = Faker()


def connection():
    return mysql.connector.connect(
        host='localhost',
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )


def create(records: int = 1000):
    conn = connection()
    cur = conn.cursor()

    user_query = "INSERT INTO users (name, surname, email) VALUES (%s, %s, %s)"
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
            faker.random_element(user_ids),  # pick a valid user_id
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
    cursor = conn.cursor()
    query = "SELECT * FROM users"
    collect_metrics = run_metrics("mysql", cursor, query, "read")
    cursor.fetchall()
    conn.close()

    return collect_metrics

@measure_performance
def join(container):
    conn = connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM users u
        INNER JOIN transactions t ON u.id = t.user_id        
    """
    collect_metrics = run_metrics("mysql", cursor, query, "join")

    cursor.close()
    conn.close()

    return collect_metrics

@measure_performance
def aggregate(container):
    conn = connection()
    cursor = conn.cursor()

    query = """
            SELECT SUM(amount) FROM transactions;                                
        """
    collect_metrics = run_metrics("mysql", cursor, query, "aggregate")

    cursor.close()
    conn.close()

    return collect_metrics

def update():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name='Updated' WHERE id % 10 = 0")
    conn.commit()
    conn.close()


def delete():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id % 10 = 0")
    conn.commit()
    conn.close()


def truncate():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    cursor.execute("TRUNCATE TABLE users;")
    cursor.execute("TRUNCATE TABLE transactions;")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    conn.commit()
    conn.close()
