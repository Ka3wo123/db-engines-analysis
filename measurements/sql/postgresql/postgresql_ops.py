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

    cur.execute(f"""
        LOAD DATA LOCAL INFILE 'datasets/users.csv'
        INTO TABLE users
        FIELDS TERMINATED BY ','
        IGNORE 1 ROWS
        LIMIT {records}
    """)

    cur.execute(f"""
        LOAD DATA LOCAL INFILE 'datasets/transactions.csv'
        INTO TABLE transactions
        FIELDS TERMINATED BY ','
        IGNORE 1 ROWS
        LIMIT {records}
    """)

    conn.commit()
    conn.close()

def update():
    conn = connection()
    cur = conn.cursor()
    query = "UPDATE users SET name='Updated' WHERE id % 10 = 0"

    metrics = run_metrics("postgresql", cur, query)
    conn.close()
    return metrics


def delete():
    conn = connection()
    cur = conn.cursor()
    query = "DELETE FROM users WHERE id % 10 = 5"

    metrics = run_metrics("postgresql", cur, query)
    conn.close()
    return metrics


def truncate():
    conn = connection()
    cur = conn.cursor()
    query = "TRUNCATE TABLE transactions, users RESTART IDENTITY CASCADE"

    cur.execute(query)

    conn.commit()
    conn.close()

@measure_performance
def read_filter():
    """
    Find user IDs that made fraudulent transactions on Mobile phones
    """
    conn = connection()
    cur = conn.cursor()
    query = "SELECT user_id FROM transactions WHERE device_type = 'Mobile' AND is_fraudulent = true"
    metrics = run_metrics("postgresql", cur, query)
    conn.close()
    return metrics


@measure_performance
def read_amount_range():
    """
    Find user IDs that transfer amount was greater or equal to 500 000
    """
    conn = connection()
    cursor = conn.cursor()
    query = "SELECT user_id FROM transactions WHERE amount >= 500000"
    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics


@measure_performance
def read_date_range():
    """
    Find user IDs that made transactions in the first quarter of 2020
    """
    conn = connection()
    cursor = conn.cursor()
    query = "SELECT user_id FROM transactions WHERE created_at BETWEEN '2020-01-01' AND '2020-03-31'"
    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

@measure_performance
def read_by_user():
    conn = connection()
    cursor = conn.cursor()
    user_id = 1

    query = f"""
        SELECT *
        FROM transactions
        WHERE user_id = {user_id}
    """

    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

@measure_performance
def read_fraud():
    conn = connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM transactions
        WHERE is_fraudulent = true
    """

    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

@measure_performance
def read_high_value():
    conn = connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM transactions
        WHERE amount >= 100000
    """

    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

@measure_performance
def read_by_country():
    conn = connection()
    cursor = conn.cursor()
    country = "Russia"

    query = f"""
        SELECT *
        FROM transactions
        WHERE country = '{country}'
    """

    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

@measure_performance
def read_by_device():
    conn = connection()
    cursor = conn.cursor()
    device_type = "Mobile"

    query = f"""
        SELECT *
        FROM transactions
        WHERE device_type = '{device_type}'
    """

    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

@measure_performance
def read_fraud_high_value():
    conn = connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM transactions
        WHERE is_fraudulent = true
          AND amount >= 100000
    """

    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

@measure_performance
def aggregate_by_country():
    conn = connection()
    cursor = conn.cursor()
    country = "Russia"

    query = f"""
        SELECT SUM(amount)
        FROM transactions
        WHERE country = '{country}'
    """

    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

@measure_performance
def read_hourly_user_stats():
    conn = connection()
    cursor = conn.cursor()
    user_id = 1

    query = f"""
        SELECT
            user_id,
            date_trunc('hour', created_at) AS hour,
            SUM(amount) AS total_amount
        FROM transactions
        WHERE user_id = {user_id}
        GROUP BY user_id, hour
        ORDER BY hour
    """

    metrics = run_metrics("postgresql", cursor, query)
    conn.close()
    return metrics

