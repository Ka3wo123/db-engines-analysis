# dataset_generator/generate_dataset.py

import csv
import uuid
from datetime import datetime
from faker import Faker

faker = Faker()

USERS = 1000
TRANSACTIONS = 1000

def main():
    user_ids = [i for i in range(USERS)]

    # ---------- USERS ----------
    with open("../datasets/users.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "name", "email"])

        for uid in user_ids:
            writer.writerow([
                uid,
                faker.first_name(),
                faker.last_name(),
                faker.email()
            ])

    print(f"users.csv generated ({USERS})")

    # ---------- TRANSACTIONS ----------
    with open("../datasets/transactions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "tx_id",
            "user_id",
            "amount",
            "is_fraudulent",
            "created_at",
            "device_type",
            "country",
            "device_id"
        ])

        for _ in range(TRANSACTIONS):
            writer.writerow([
            faker.random_element(user_ids),
            faker.pydecimal(positive=True, max_value=1_000_000, min_value=0.01, right_digits=2),
            faker.boolean(chance_of_getting_true=1),
            faker.date_time(),
            faker.ipv4_public(),
            faker.ipv4_public(),
            faker.user_agent(),
            str(uuid.uuid4()),
            faker.random_element(['Mobile', 'Desktop', 'Laptop', 'Tablet']),
            faker.company() + " Bank",
            faker.iban(),
            faker.country(),
            faker.currency()[0]
            ])

    print(f"transactions.csv generated ({TRANSACTIONS})")


if __name__ == "__main__":
    main()
