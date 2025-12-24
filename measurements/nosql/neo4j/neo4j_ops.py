import random
import uuid

from faker import Faker
from neo4j import GraphDatabase

from measurements.collectors import run_metrics
from measurements.db_config import NEO4J_USER, NEO4J_PASSWORD
from measurements.measurement import measure_performance

faker = Faker()


def connection():
    uri = "bolt://localhost:7687"
    return GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))


USER_POOL_SIZE = 1000
USER_POOL = [str(uuid.uuid4()) for _ in range(USER_POOL_SIZE)]


def create(records: int = 1000):
    driver = connection()
    with driver.session() as session:
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Transaction) REQUIRE t.id IS UNIQUE")
        session.run("CREATE INDEX user_id_index IF NOT EXISTS FOR (u:User) ON (u.id)")
        session.run("CREATE INDEX transaction_id_index IF NOT EXISTS FOR (t:Transaction) ON (t.id)")

    data = []
    batch_size = 1000

    for _ in range(records):
        data.append({
            "sender_id": random.choice(USER_POOL),
            "sender_name": faker.first_name(),
            "sender_email": faker.email(),

            "receiver_id": random.choice(USER_POOL),
            "receiver_name": faker.first_name(),
            "receiver_email": faker.email(),

            "transaction_id": str(uuid.uuid4()),
            "amount": float(faker.pydecimal(right_digits=2, positive=True, max_value=1_000_000, min_value=0.01)),
            "currency": faker.currency()[0],
            "is_fraudulent": faker.boolean(chance_of_getting_true=1),
            "receiver_ip_address": faker.ipv4_public(),
            "sender_ip_address": faker.ipv4_public(),
            "browser_agent": faker.user_agent(),
            "device_id": str(uuid.uuid4()),
            "device_type": faker.random_element(['Mobile', 'Laptop', 'Desktop', 'Tablet']),
            "bank_name": faker.company() + " Bank",
            "bank_iban": faker.iban(),
            "country": faker.country()
        })

    cypher = """
        UNWIND $batch AS row

        MERGE (s:User {id: row.sender_id})
          ON CREATE SET s.name = row.sender_name,
                        s.email = row.sender_email

        MERGE (r:User {id: row.receiver_id})
          ON CREATE SET r.name = row.receiver_name,
                        r.email = row.receiver_email

        CREATE (t:Transaction {
            id: row.transaction_id,
            amount: row.amount,
            currency: row.currency,
            transferred_at: datetime(),
            is_fraudulent: row.is_fraudulent,
            receiver_ip_address: row.receiver_ip_address,
            sender_ip_address: row.sender_ip_address,
            browser_agent: row.browser_agent,
            device_id: row.device_id,
            device_type: row.device_type,
            bank_name: row.bank_name,
            bank_iban: row.bank_iban,
            country: row.country
        })

        MERGE (s)-[:MADE]->(t)
        MERGE (t)-[:TO]->(r)
        """

    with driver.session() as session:
        for i in range(0, records, batch_size):
            batch = data[i:i + batch_size]
            session.run(cypher, batch=batch)


def update():
    driver = connection()
    query = """
        MATCH (t:Transaction)
        SET t.amount = t.amount * 1.05
        """
    return run_metrics("neo4j", driver, query)


def delete():
    driver = connection()
    query = """
        MATCH (t:Transaction)
        WHERE t.amount > 100000
        DETACH DELETE t
        """

    return run_metrics("neo4j", driver, query)


def truncate():
    driver = connection()
    query = "MATCH (n) DETACH DELETE n"
    return run_metrics("neo4j", driver, query)


@measure_performance
def read_filter():
    """
    Find fraudulent transactions made on Mobile phones
    """
    driver = connection()
    query = """
        MATCH (t:Transaction)
        WHERE t.is_fraudulent = true
        AND t.device_type = 'Mobile'
        RETURN t
    """

    return run_metrics("neo4j", driver, query)


@measure_performance
def read_amount_range():
    """
    Find transactions that transactions amount were grater or equal to 500 000
    """
    driver = connection()
    query = """
        MATCH (t:Transaction)
        WHERE t.amount > 500000
        RETURN t
    """

    return run_metrics("neo4j", driver, query)


@measure_performance
def read_amount_range():
    """
    Find user IDs that made transactions in the first quarter of 2020
    """
    driver = connection()
    query = """
        MATCH (t:Transaction)
        WHERE t.amount > 500000
        RETURN t        
    """

    return run_metrics("neo4j", driver, query)
