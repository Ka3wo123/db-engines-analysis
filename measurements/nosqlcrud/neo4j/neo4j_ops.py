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


# @measure_performance
def create(records: int = 1000):
    driver = connection()
    with driver.session() as session:
        for _ in range(records):
            sender_id = str(uuid.uuid4())
            receiver_id = str(uuid.uuid4())
            transaction_id = str(uuid.uuid4())

            session.run("""
            MERGE (s:User {id: $sender_id})
            ON CREATE SET s.name = $sender_name, s.email = $sender_email
            
            MERGE (r:User {id: $receiver_id})
            ON CREATE SET r.name = $receiver_name, r.email = $receiver_email
            
            CREATE (t:Transaction {
                id: $transaction_id,
                amount: $amount,
                currency: $currency,
                transferred_at: datetime(),
                is_fraudulent: $is_fraudulent,
                receiver_ip_address: $receiver_ip_address,
                sender_ip_address: $sender_ip_address,
                browser_agent: $browser_agent,
                device_id: $device_id,
                device_type: $device_type,
                bank_name: $bank_name,
                bank_iban: $bank_iban,
                country: $country
            })
            
            MERGE (s)-[:MADE]->(t)
            MERGE (t)-[:TO]->(r)                
            """, {
                "sender_id": sender_id,
                "sender_name": faker.first_name(),
                "sender_email": faker.email(),
                "receiver_id": receiver_id,
                "receiver_name": faker.first_name(),
                "receiver_email": faker.email(),
                "transaction_id": transaction_id,
                "amount": float(faker.pydecimal(right_digits=2, positive=True, max_value=1_000_000, min_value=0.01)),
                "currency": faker.currency()[0],
                "is_fraudulent": faker.boolean(),
                "receiver_ip_address": faker.ipv4_public(),
                "sender_ip_address": faker.ipv4_public(),
                "browser_agent": faker.user_agent(),
                "device_id": str(uuid.uuid4()),
                "device_type": faker.random_element(['Mobile', 'Laptop', 'Desktop', 'Tablet']),
                "bank_name": faker.company() + " Bank",
                "bank_iban": faker.iban(),
                "country": faker.country()
            })


@measure_performance
def read():
    driver = connection()
    query = "MATCH (s:User)-[:MADE]->(t:Transaction)-[:TO]->(r:User) RETURN s, t, r"
    metrics = run_metrics("neo4j", driver, query, "read")
    return metrics




@measure_performance
def update():
    driver = connection()
    with driver.session() as session:
        session.run("""
        MATCH (t:Transaction)
        SET t.amount = t.amount * 1.05
        """)


@measure_performance
def delete():
    driver = connection()
    with driver.session() as session:
        session.run("""
        MATCH (t:Transaction)
        WHERE t.amount > 100000
        DETACH DELETE t
        """)


@measure_performance
def truncate():
    driver = connection()
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


def _run_profile_query(driver, query: str):
    with driver.session() as session:
        profile_result = session.run(f"PROFILE {query}")
        summary = profile_result.consume().profile if profile_result else None
    return summary