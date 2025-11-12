CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    is_fraudulent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    receiver_ip_address VARCHAR(15),
    sender_ip_address VARCHAR(15),
    browser_agent VARCHAR(255),
    device_id UUID,
    device_type VARCHAR(128),
    bank_name VARCHAR(255),
    bank_iban VARCHAR(255),
    country VARCHAR(255),
    currency VARCHAR(5)
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);