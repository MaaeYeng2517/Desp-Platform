# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

from sqlalchemy import create_engine, text
from os import getenv


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"dataeng:{getenv('PGPASSWORD', 'dataeng')}"
    f"@{getenv('DB_HOST', 'postgres')}:5432/datawarehouse"
)


def check_quality():

    engine = create_engine(DATABASE_URL)

    checks = {

        "duplicate_transaction": """
            SELECT COUNT(*)
            FROM (
                SELECT transaction_id
                FROM mart.sales
                GROUP BY transaction_id
                HAVING COUNT(*) > 1
            ) x
        """,

        "invalid_quantity": """
            SELECT COUNT(*)
            FROM mart.sales
            WHERE quantity <= 0
        """,

        "invalid_price": """
            SELECT COUNT(*)
            FROM mart.sales
            WHERE unit_price < 0
        """,

        "null_customer": """
            SELECT COUNT(*)
            FROM mart.sales
            WHERE customer_id IS NULL
        """
    }

    with engine.connect() as connection:

        for name, query in checks.items():

            result = connection.execute(
                text(query)
            ).scalar()

            print(
                f"{name}: {result}"
            )

            if result > 0:  
                raise ValueError(
                    f"Quality check failed: {name}"
                )   

    print("DATA QUALITY: PASS")


if __name__ == "__main__":
    check_quality()