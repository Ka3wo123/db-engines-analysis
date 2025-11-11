import os

from measurements.measurement import measure_performance
from neo4j import GraphDatabase
from measurements.db_config import NEO4J_USER, NEO4J_PASSWORD


def connection():
    uri = "bolt://localhost:7687"
    return GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))


@measure_performance
def create():
    driver = connection()
    with driver.session() as session:
        session.run("CREATE (u:User {name: 'Alice'})")


@measure_performance
def read():
    driver = connection()
    with driver.session() as session:
        session.run("MATCH (u:User) RETURN u")


@measure_performance
def update():
    driver = connection()
    with driver.session() as session:
        session.run("MATCH (u:User {name: 'Alice'}) SET u.name = 'Bob'")


@measure_performance
def delete():
    driver = connection()
    with driver.session() as session:
        session.run("MATCH (u:User {name: 'Bob'}) DELETE u")


@measure_performance
def truncate():
    driver = connection()
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    driver.close()
