from neo4j import GraphDatabase
from faker import Faker

uri = "bolt://localhost:7687"
user = "neo4j"
password = "cg8&fhjs10LOz"

driver = GraphDatabase.driver(uri, auth=(user, password))
fake = Faker()


def populate_neo4j(tx, n=50):
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        tx.run(
            "CREATE (p:Person {first_name: $first_name, last_name: $last_name, email: $email})",
            first_name=first_name, last_name=last_name, email=email
        )


def create_friendships(tx, n=100):
    for _ in range(n):
        tx.run("""
            MATCH (a:Person), (b:Person)
            WHERE a <> b
            WITH a, b
            CREATE (a)-[:FRIENDS_WITH]->(b)
        """)


with driver.session() as session:
    session.execute_write(populate_neo4j)
    session.execute_write(create_friendships)

driver.close()
print("Neo4j populated")
