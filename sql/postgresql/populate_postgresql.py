import psycopg2
from faker import Faker

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="frauddb",
    user="postgres",
    password="postgres"
)

fake = Faker()
cur = conn.cursor()

insert_query = "INSERT INTO users(name, surname, email) VALUES (%s, %s, %s)"

for _ in range(100):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    cur.execute(insert_query, (first_name, last_name, email))

conn.commit()
cur.close()
conn.close()

print("PostgreSQL populated")
