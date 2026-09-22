# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

import pandas as pd
from sqlalchemy import create_engine, text


from os import getenv


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"dataeng:{getenv('PGPASSWORD', 'dataeng')}"
    f"@{getenv('DB_HOST', 'postgres')}:5432/datawarehouse"
)

CSV_FILE = "data/raw/sales.csv"


def extract():
    return pd.read_csv(CSV_FILE)


def validate(df):
    required_columns = [
        "transaction_id",
        "transaction_date",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    if df["transaction_id"].duplicated().any():
        raise ValueError(
            "Duplicate transaction_id found"
        )

    if (df["quantity"] <= 0).any():
        raise ValueError(
            "Quantity must be greater than zero"
        )

    if (df["unit_price"] < 0).any():
        raise ValueError(
            "Unit price cannot be negative"
        )

    return True


def transform(df):

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"]
    )

    df["total_amount"] = (
        df["quantity"] *
        df["unit_price"]
    )

    return df


def load(df):

    engine = create_engine(DATABASE_URL)

    columns = [
        "transaction_id",
        "transaction_date",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
    ]

    df[columns].to_sql(
        "sales",
        engine,
        schema="raw",
        if_exists="append",
        index=False,
    )


def main():

    print("Extract")

    df = extract()

    print(df)

    print("Validate")

    validate(df)

    print("Transform")

    df = transform(df)

    print(df)

    print("Load")

    load(df)

    print("Pipeline completed")


if __name__ == "__main__":
    main()