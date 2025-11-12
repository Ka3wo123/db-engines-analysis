CREATE KEYSPACE IF NOT EXISTS fraud
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE fraud;

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    user_id UUID,
    amount DECIMAL,
    is_fraudulent BOOLEAN,
    created_at TIMESTAMP,
    receiver_ip_address TEXT,
    sender_ip_address TEXT,
    browser_agent TEXT,
    device_id UUID,
    device_type TEXT,
    bank_name TEXT,
    bank_iban TEXT,
    country TEXT,
    currency TEXT
);
