import mysql.connector
from faker import Faker
import os
from measurements.measurement import measure_performance
from measurements.db_config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
fake = Faker()


def connection():
    return mysql.connector.connect(
        host='localhost',
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )



@measure_performance
def create(records: int = 1000):
    conn = connection()
    cursor = conn.cursor()

    users = [
        (fake.first_name(), fake.last_name(), fake.email())
        for _ in range(records)
    ]
    cursor.executemany(
        "INSERT INTO users (name, surname, email) VALUES (%s, %s, %s)",
        users
    )
    conn.commit()
    conn.close()


@measure_performance
def read():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    cursor.fetchall()
    conn.close()


@measure_performance
def update():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name='Updated' WHERE id % 10 = 0")
    conn.commit()
    conn.close()


@measure_performance
def delete():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id % 10 = 0")
    conn.commit()
    conn.close()

@measure_performance
def truncate():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    cursor.execute("TRUNCATE TABLE users;")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    conn.commit()
    conn.close()