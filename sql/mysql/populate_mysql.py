import mysql.connector
from faker import Faker

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="mysql",
    password="mysql",
    database="frauddb"
)

cur = conn.cursor()
fake = Faker()

insert_query = "INSERT INTO users (name, surname, email) VALUES (%s, %s, %s)"

for _ in range(100):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    cur.execute(insert_query, (first_name, last_name, email))

conn.commit()
cur.close()
conn.close()

print("MySQL populated")
