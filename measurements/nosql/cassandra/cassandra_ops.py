import uuid
from decimal import Decimal

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


def amount_bucket(amount: float, bucket_size: int = 10000): return int(amount // bucket_size)


def generate_fake_transaction(user_ids):
    return {
        "id": uuid.uuid4(),
        "user_id": faker.random_element(user_ids),
        "amount": Decimal(str(faker.pydecimal(positive=True, max_value=1_000_000,
                                              min_value=0.01, right_digits=2))),
        "is_fraudulent": faker.boolean(chance_of_getting_true=1),
        "created_at": faker.date_time(),
        "receiver_ip_address": faker.ipv4_public(),
        "sender_ip_address": faker.ipv4_public(),
        "browser_agent": faker.user_agent(),
        "device_id": uuid.uuid4(),
        "device_type": faker.random_element(['Mobile', 'Desktop', 'Laptop', 'Tablet']),
        "bank_name": faker.company() + " Bank", "bank_iban": faker.iban(),
        "country": faker.country(), "currency": faker.currency()[0]
    }


def insert_transaction(session, tx):
    if not hasattr(session, "stmts"):
        session.stmts = {}

        session.stmts["transactions_by_user"] = session.prepare("""
            INSERT INTO transactions_by_user (
                user_id, created_at, id, amount, country, device_id, is_fraudulent
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        session.stmts["fraudulent_transactions"] = session.prepare("""
            INSERT INTO fraudulent_transactions (
                is_fraudulent, created_at, id, user_id, amount, country, device_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        session.stmts["transactions_by_amount_bucket"] = session.prepare("""
            INSERT INTO transactions_by_amount_bucket (
                amount_bucket, created_at, id, user_id, amount, is_fraudulent, country
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        session.stmts["transactions_by_country"] = session.prepare("""
            INSERT INTO transactions_by_country (
                country, created_at, id, user_id, amount, is_fraudulent
            ) VALUES (?, ?, ?, ?, ?, ?)
        """)

        session.stmts["transactions_by_device"] = session.prepare("""
            INSERT INTO transactions_by_device (
                device_id, created_at, id, user_id, amount, is_fraudulent, country
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        session.stmts["transactions_by_user_hour"] = session.prepare("""
            UPDATE transactions_by_user_hour
            SET total_amount = total_amount + ?
            WHERE user_id = ? AND hour = ?
        """)

        session.stmts["fraud_high_value"] = session.prepare("""
            INSERT INTO fraud_high_value (
                is_fraudulent, amount_bucket, created_at, id, user_id, amount, country
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        session.stmts["transactions_by_bank"] = session.prepare("""
            INSERT INTO transactions_by_bank (
                bank_name, created_at, id, user_id, amount, is_fraudulent, country
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

    # --- Execute prepared statements ---

    # 1. transactions_by_user
    session.execute(
        session.stmts["transactions_by_user"],
        (tx["user_id"], tx["created_at"], tx["id"], tx["amount"],
         tx["country"], tx["device_id"], tx["is_fraudulent"])
    )

    # 2. fraudulent_transactions
    session.execute(
        session.stmts["fraudulent_transactions"],
        (tx["is_fraudulent"], tx["created_at"], tx["id"], tx["user_id"],
         tx["amount"], tx["country"], tx["device_id"])
    )

    # 3. transactions_by_amount_bucket
    bucket = amount_bucket(int(tx["amount"]))
    session.execute(
        session.stmts["transactions_by_amount_bucket"],
        (bucket, tx["created_at"], tx["id"], tx["user_id"],
         tx["amount"], tx["is_fraudulent"], tx["country"])
    )

    # 4. transactions_by_country
    session.execute(
        session.stmts["transactions_by_country"],
        (tx["country"], tx["created_at"], tx["id"], tx["user_id"],
         tx["amount"], tx["is_fraudulent"])
    )

    # 5. transactions_by_device
    session.execute(
        session.stmts["transactions_by_device"],
        (tx["device_id"], tx["created_at"], tx["id"], tx["user_id"],
         tx["amount"], tx["is_fraudulent"], tx["country"])
    )

    # 6. transactions_by_user_hour (counter)
    hour_bucket = tx["created_at"].replace(minute=0, second=0, microsecond=0)
    session.execute(
        session.stmts["transactions_by_user_hour"],
        (int(tx["amount"]), tx["user_id"], hour_bucket)
    )

    # 7. fraud_high_value (only if fraudulent)
    if tx["is_fraudulent"]:
        session.execute(
            session.stmts["fraud_high_value"],
            (True, bucket, tx["created_at"], tx["id"], tx["user_id"],
             tx["amount"], tx["country"])
        )

    # 8. transactions_by_bank
    session.execute(
        session.stmts["transactions_by_bank"],
        (tx["bank_name"], tx["created_at"], tx["id"], tx["user_id"],
         tx["amount"], tx["is_fraudulent"], tx["country"])
    )


def create(records: int = 1000):
    session = connection()
    user_ids = [uuid.uuid4() for _ in range(100)]

    for _ in range(records):
        tx = generate_fake_transaction(user_ids)
        insert_transaction(session, tx)

def truncate():
    session = connection()
    query = "TRUNCATE TABLE transactions"
    return run_metrics("cassandra", session, query)


@measure_performance
def read_by_user():
    session = connection()
    user_id = uuid.uuid4()
    query = f"""
        SELECT * FROM transactions_by_user
        WHERE user_id = {user_id}
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def read_fraud():
    session = connection()
    query = """
        SELECT * FROM fraudulent_transactions
        WHERE is_fraudulent = true
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def read_high_value():
    session = connection()
    bucket = amount_bucket(100000)
    query = f"""
        SELECT * FROM transactions_by_amount_bucket
        WHERE amount_bucket = {bucket}
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def read_by_country():
    session = connection()
    country = "Russia"
    query = f"""
        SELECT * FROM transactions_by_country
        WHERE country = '{country}'
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def read_by_device():
    session = connection()
    device_id = uuid.uuid4()
    query = f"""
        SELECT * FROM transactions_by_device
        WHERE device_id = {device_id}
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def read_fraud_high_value():
    session = connection()
    bucket = amount_bucket(100000)
    query = f"""
        SELECT * FROM fraud_high_value
        WHERE is_fraudulent = true AND amount_bucket = {bucket}
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def aggregate_by_country():
    session = connection()
    country = "Russia"
    query = f"""
        SELECT amount FROM transactions_by_country
        WHERE country = '{country}'
    """
    return run_metrics("cassandra", session, query)


@measure_performance
def read_hourly_user_stats():
    session = connection()
    user_id = uuid.uuid4()
    query = f"""
        SELECT * FROM transactions_by_user_hour
        WHERE user_id = {user_id}
    """
    return run_metrics("cassandra", session, query)
