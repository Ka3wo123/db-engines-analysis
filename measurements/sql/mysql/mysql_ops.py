import uuid

import mysql.connector
from faker import Faker
import os
from measurements.collectors import run_metrics
from measurements.db_config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from measurements.measurement import measure_performance

faker = Faker()


def connection():
    return mysql.connector.connect(
        host='localhost',
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        allow_local_infile=True
    )

def load_dataset(records):
    conn = connection()
    cur = conn.cursor()

    cur.execute("SET FOREIGN_KEY_CHECKS=0")

    cur.execute(f"""
        LOAD DATA LOCAL INFILE 'datasets/users.csv'
        INTO TABLE users
        FIELDS TERMINATED BY ','
        IGNORE 1 ROWS
    """)

    cur.execute(f"""
        LOAD DATA LOCAL INFILE 'datasets/transactions.csv'
        INTO TABLE transactions
        FIELDS TERMINATED BY ','
        IGNORE 1 ROWS
    """)

    conn.commit()
    conn.close()


def update():
    conn = connection()
    cursor = conn.cursor()
    query = "UPDATE users SET name='Updated' WHERE id % 10 = 0"

    collect_metrics = run_metrics("mysql", cursor, query)

    cursor.close()
    conn.close()

    return collect_metrics


def delete():
    conn = connection()
    cursor = conn.cursor()
    query = "DELETE FROM users WHERE id % 10 = 0"

    collect_metrics = run_metrics("mysql", cursor, query)

    cursor.close()
    conn.close()
    return collect_metrics


def truncate():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    cursor.execute("TRUNCATE TABLE users;")
    cursor.execute("TRUNCATE TABLE transactions;")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    conn.commit()
    conn.close()

@measure_performance
def read_filter():
    """
    Find user IDs that made fraudulent transactions on Mobile phones
    """
    conn = connection()
    cursor = conn.cursor()
    query = "SELECT user_id FROM transactions WHERE device_type = 'Mobile' AND is_fraudulent = true"
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
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
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
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
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
    conn.close()
    return metrics

@measure_performance
def read_by_user():
    conn = connection()
    cursor = conn.cursor()
    user_id = 1  # przykładowy istniejący user
    query = f"SELECT * FROM transactions WHERE user_id = {user_id}"
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
    conn.close()
    return metrics

@measure_performance
def read_fraud():
    conn = connection()
    cursor = conn.cursor()
    query = "SELECT * FROM transactions WHERE is_fraudulent = true"
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
    conn.close()
    return metrics

@measure_performance
def read_high_value():
    conn = connection()
    cursor = conn.cursor()
    query = "SELECT * FROM transactions WHERE amount >= 100000"
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
    conn.close()
    return metrics

@measure_performance
def read_by_country():
    conn = connection()
    cursor = conn.cursor()
    country = "Russia"
    query = f"""
    SELECT SUM(amount)
    FROM transactions
    WHERE country = '{country}'
"""
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
    conn.close()
    return metrics

@measure_performance
def read_by_device():
    conn = connection()
    cursor = conn.cursor()
    device_id = "some-device-id"
    query = f"SELECT * FROM transactions WHERE device_id = '{device_id}'"
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
    conn.close()
    return metrics

@measure_performance
def read_fraud_high_value():
    conn = connection()
    cursor = conn.cursor()
    query = """
        SELECT * FROM transactions
        WHERE is_fraudulent = true AND amount >= 100000
    """
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
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
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
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
        DATE_FORMAT(created_at, '%Y-%m-%d %H:00:00') AS hour,
        SUM(amount) AS total_amount
    FROM transactions
    WHERE user_id = {user_id}
    GROUP BY hour
"""
    metrics = run_metrics("mysql", cursor, query)
    cursor.fetchall()
    conn.close()
    return metrics
