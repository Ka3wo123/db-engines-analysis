import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'docker', '.env'))

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE")
CASSANDRA_AUTHENTICATOR = os.getenv("CASSANDRA_AUTHENTICATOR")
CASSANDRA_AUTHORIZER = os.getenv("CASSANDRA_AUTHORIZER")
CASSANDRA_ROLE_MANAGER = os.getenv("CASSANDRA_ROLE_MANAGER")

NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
