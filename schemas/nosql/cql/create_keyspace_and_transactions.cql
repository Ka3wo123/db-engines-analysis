CREATE KEYSPACE IF NOT EXISTS fraud
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE fraud;

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    user_id UUID,
    amount DECIMAL,
    is_fraudulent BOOLEAN,
    created_at TIMESTAMP
);
