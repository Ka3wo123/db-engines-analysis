import uuid

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from faker import Faker

from measurements.collectors import run_metrics
from measurements.db_config import CASSANDRA_KEYSPACE
from measurements.measurement import measure_performance

faker = Faker()


def connection():
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect()
    session.set_keyspace(CASSANDRA_KEYSPACE)
    return session

def create(records: int = 1000):
    session = connection()
    insert_stmt = session.prepare("""
        INSERT INTO transactions 
        (id, user_id, amount, is_fraudulent, created_at, receiver_ip_address, sender_ip_address, browser_agent,
        device_id, device_type, bank_name, bank_iban, country, currency)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    for _ in range(records):
        session.execute(
            insert_stmt,
            (
                uuid.UUID(faker.uuid4()),
                uuid.UUID(faker.uuid4()),
                faker.pydecimal(positive=True, max_value=1_000_000, min_value=0.01, right_digits=2),
                faker.boolean(chance_of_getting_true=1),
                faker.date_time(),
                faker.ipv4_public(),
                faker.ipv4_public(),
                faker.user_agent(),
                uuid.UUID(faker.uuid4()),
                faker.random_element(['Mobile', 'Desktop', 'Laptop', 'Tablet']),
                faker.company() + " Bank",
                faker.iban(),
                faker.country(),
                faker.currency()[0]
            ))


@measure_performance
def read(container):
    session = connection()
    query = "SELECT * FROM transactions"
    collect_metrics = run_metrics("cassandra", session, query)
    return collect_metrics

@measure_performance
def aggregate(container):
    session = connection()
    query = "SELECT SUM(amount) FROM transactions"
    metrics = run_metrics("cassandra", session, query)
    return metrics


def update(container):
    session = connection()
    stmt = session.prepare("UPDATE transactions SET amount = ? WHERE id = ? IF EXISTS")
    rows = session.execute(SimpleStatement("SELECT id FROM transactions LIMIT 20"))
    for row in rows:
        session.execute(stmt, (1.00, row.id))


def delete(container):
    session = connection()
    stmt = session.prepare("DELETE FROM transactions WHERE id = ?")
    rows = session.execute(SimpleStatement("SELECT id FROM transactions LIMIT 20"))

    for row in rows:
        session.execute(stmt, (row.id,))

@measure_performance
def truncate(container):
    session = connection()
    query = "TRUNCATE TABLE transactions"
    return run_metrics("cassandra", session, query)


@measure_performance
def read_fraud(container):
    session = connection()
    query = """
        SELECT * FROM transactions
        WHERE is_fraudulent = true
        ALLOW FILTERING
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def read_amount_range(container):
    session = connection()
    query = """
        SELECT * FROM transactions
        WHERE amount > 100000
        ALLOW FILTERING
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def read_fraud_and_amount(container):
    session = connection()
    query = """
        SELECT * FROM transactions
        WHERE is_fraudulent = true AND amount > 100000
        ALLOW FILTERING
    """
    return run_metrics("cassandra", session, query)


#@measure_performance
def group_by_country(container):
    session = connection()
    query = """
        SELECT country, SUM(amount)
        FROM transactions
        GROUP BY country
    """
    return run_metrics("cassandra", session, query)


#@measure_performance
def distinct_users(container):
    session = connection()
    query = """
        SELECT DISTINCT user_id
        FROM transactions
    """
    return run_metrics("cassandra", session, query)
