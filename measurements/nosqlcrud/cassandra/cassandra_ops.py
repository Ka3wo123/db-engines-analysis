import uuid

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

from faker import Faker
from measurements.measurement import measure_performance
from measurements.db_config import CASSANDRA_KEYSPACE


faker = Faker()

def connection():
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect()
    session.set_keyspace(CASSANDRA_KEYSPACE)
    return session


@measure_performance
def create(records: int = 1000):
    session = connection()
    insert_stmt = session.prepare("""
        INSERT INTO transactions (id, user_id, amount, is_fraudulent, created_at)
        VALUES (?, ?, ?, ?, ?)
    """)

    for _ in range(records):
        session.execute(
            insert_stmt,
            (uuid.UUID(faker.uuid4()), uuid.UUID(faker.uuid4()), faker.pyfloat(left_digits=2, positive=True, min_value=0.01), faker.boolean(), faker.date_time())
        )


@measure_performance
def read():
    session = connection()
    session.execute(SimpleStatement("SELECT * FROM transactions"))


@measure_performance
def update():
    session = connection()
    stmt = session.prepare("UPDATE transactions SET amount = ? WHERE id = ? IF EXISTS")
    rows = session.execute(SimpleStatement("SELECT id FROM transactions LIMIT 20"))
    for row in rows:
        session.execute(stmt, (1.00, row.id))


@measure_performance
def delete():
    session = connection()
    stmt = session.prepare("DELETE FROM transactions WHERE id = ?")
    rows = session.execute(SimpleStatement("SELECT id FROM transactions LIMIT 20"))

    for row in rows:
        session.execute(stmt, (row.id,))

@measure_performance
def truncate():
    session = connection()
    session.execute("TRUNCATE TABLE transactions")
    session.shutdown()
