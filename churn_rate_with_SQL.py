import os

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load local settings from .env; never commit real credentials.
load_dotenv()

required_settings = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
missing_settings = [key for key in required_settings if not os.getenv(key)]
if missing_settings:
    raise RuntimeError(
        "Missing database settings: "
        + ", ".join(missing_settings)
        + ". Copy .env.example to .env and fill in your local values."
    )

conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
)

try:
    # This is the share of users who have ended a subscription and have no
    # currently active subscription. It is not a time-windowed churn rate.
    inactive_customer_query = """
        WITH all_customers AS (
            SELECT DISTINCT user_id
            FROM subscriptions
        ),
        active_customers AS (
            SELECT DISTINCT user_id
            FROM subscriptions
            WHERE end_date IS NULL
        ),
        inactive_customers AS (
            SELECT DISTINCT s.user_id
            FROM subscriptions AS s
            WHERE s.end_date IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM active_customers AS a
                  WHERE a.user_id = s.user_id
              )
        )
        SELECT
            COUNT(i.user_id)::double precision
            / NULLIF(COUNT(a.user_id), 0) AS inactive_customer_rate
        FROM all_customers AS a
        LEFT JOIN inactive_customers AS i ON i.user_id = a.user_id;
    """
    inactive_customer_rate = pd.read_sql_query(
        inactive_customer_query, conn
    ).loc[0, "inactive_customer_rate"]

    active_users_query = """
        SELECT COUNT(DISTINCT user_id) AS active_users
        FROM subscriptions
        WHERE end_date IS NULL;
    """
    active_users = pd.read_sql_query(active_users_query, conn).loc[
        0, "active_users"
    ]

    mrr_query = """
        SELECT SUM(p.monthly_price) AS mrr
        FROM subscriptions AS s
        JOIN plans AS p ON p.plan_id = s.plan_id
        WHERE s.end_date IS NULL
          AND p.monthly_price IS NOT NULL;
    """
    mrr = pd.read_sql_query(mrr_query, conn).loc[0, "mrr"]

    metrics = {
        "Active users": active_users,
        "Inactive former-customer share": inactive_customer_rate,
        "Monthly recurring revenue (MRR)": mrr,
    }
    for metric, value in metrics.items():
        print(f"{metric}: {value}")

    mrr_by_plan_query = """
        SELECT p.plan_name, SUM(p.monthly_price) AS mrr
        FROM subscriptions AS s
        JOIN plans AS p ON p.plan_id = s.plan_id
        WHERE s.end_date IS NULL
          AND p.monthly_price IS NOT NULL
        GROUP BY p.plan_name
        ORDER BY mrr DESC;
    """
    mrr_by_plan_df = pd.read_sql_query(mrr_by_plan_query, conn)
    print("\nMRR by plan:")
    print(mrr_by_plan_df.to_string(index=False))

    if not mrr_by_plan_df.empty:
        plt.figure(figsize=(10, 6))
        plt.bar(mrr_by_plan_df["plan_name"], mrr_by_plan_df["mrr"])
        plt.xlabel("Subscription plan")
        plt.ylabel("Monthly recurring revenue")
        plt.title("Monthly Recurring Revenue by Plan")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()
finally:
    conn.close()
