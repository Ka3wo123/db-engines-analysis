import random
import uuid
from datetime import datetime

from cassandra.cluster import Cluster
from faker import Faker

fake = Faker()

cluster = Cluster(['localhost'])
session = cluster.connect('fraud')

insert_query = session.prepare("""
    INSERT INTO transactions (id, user_id, amount, is_fraudulent, created_at)
    VALUES (?, ?, ?, ?, ?)
""")

for _ in range(100):
    session.execute(
        insert_query,
        (uuid.uuid4(), uuid.uuid4(), random.uniform(10, 1000),
         random.choice([True, False]), datetime.utcnow())
    )

print("Cassandra populated")
