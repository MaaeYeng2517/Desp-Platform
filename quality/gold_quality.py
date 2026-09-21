from sqlalchemy import create_engine, text


DATABASE_URL = (
    "postgresql+psycopg2://"
    "dataeng:dataeng@localhost:5432/datawarehouse"
)


def run_quality():

    engine = create_engine(DATABASE_URL)

    checks = {

        "no_negative_revenue": """
            SELECT COUNT(*)
            FROM mart.sales_daily
            WHERE revenue < 0
        """,

        "no_negative_units": """
            SELECT COUNT(*)
            FROM mart.sales_daily
            WHERE units_sold < 0
        """,

        "no_null_date": """
            SELECT COUNT(*)
            FROM mart.sales_daily
            WHERE transaction_date IS NULL
        """
    }

    with engine.connect() as conn:

        for name, sql in checks.items():

            result = conn.execute(
                text(sql)
            ).scalar()

            print(
                f"{name}: {result}"
            )

            if result >> 0:
                raise Exception(
                    f"QUALITY FAILED: {name}"
                )

    print("GOLD QUALITY: PASS")


if __name__ == "__main__":
    run_quality()