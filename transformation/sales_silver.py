import pandas as pd
from pathlib import Path


SOURCE = Path(
    "data/bronze/sales/sales.csv"
)

TARGET = Path(
    "data/silver/sales/sales_clean.csv"
)


def transform():

    df = pd.read_csv(SOURCE)

    # Remove duplicate transactions
    df = df.drop_duplicates(
        subset=["transaction_id"]
    )

    # Convert date
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"]
    )

    # Remove invalid values
    df = df[
        (df["quantity"] > 0)
        &
        (df["unit_price"] >= 0)
    ]

    # Calculate amount
    df["total_amount"] = (
        df["quantity"]
        * df["unit_price"]
    )

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        TARGET,
        index=False
    )

    print(
        f"Silver records: {len(df)}"
    )


if __name__ == "__main__":
    transform()