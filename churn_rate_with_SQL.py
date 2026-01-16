import psycopg2
import pandas as pd

#Basic connenction to the database
conn = psycopg2.connect(
    host = "localhost",
    database = "analytics_practice",
    user = "postgres",
    password = "Sandeep/2006"
)


#churn rate hai ye 
query = """
WITH churned AS (
    SELECT DISTINCT user_id
    FROM subscriptions
    WHERE end_date IS NOT NULL
      AND user_id NOT IN (
          SELECT DISTINCT user_id
          FROM subscriptions
          WHERE end_date IS NULL
      )
),
total AS (
    SELECT COUNT(DISTINCT user_id) AS total_users
    FROM subscriptions
)
SELECT 
    COUNT(*) * 1.0 / MAX(total.total_users) AS churn_rate
FROM churned, total;
"""
df = pd.read_sql_query(query, conn)
# Extract churn rate value
churn_rate = df.loc[0, "churn_rate"]







#Calculating the number of active users here
Active_users_query = ''' SELECT COUNT(DISTINCT user_id) AS active_users
FROM subscriptions WHERE end_date IS NULL;'''

active_users_df = pd.read_sql_query(Active_users_query, conn)
#Extract active users value
active_users = active_users_df.loc[0,"active_users"]





#Calculation the MRR here
mrr_query = ''' SELECT SUM(monthly_price) AS MRR
FROM subscriptions s
join plans p
ON s.plan_id = p.plan_id
WHERE s.end_date IS NULL
AND p.monthly_price IS NOT NULL; '''
mrr_df = pd.read_sql_query (mrr_query, conn)
#Extract MRR value 
mrr = mrr_df.loc[0,"mrr"]




metrics = {
    "active_users": active_users,
    "churn rate": churn_rate,
    "MRR": mrr
}

for key,value in metrics.items():
    print(f"{key} : {value}")



mrr_by_plan_query = ''' SELECT p.plan_name, SUM(monthly_price) AS mrr
FROM subscriptions s
JOIN plans p 
ON p.plan_id = s.plan_id
WHERE end_date IS NULL AND monthly_price IS NOT NULL
GROUP BY plan_name;'''

mrr_by_plan_df = pd.read_sql_query(mrr_by_plan_query, conn)
print(mrr_by_plan_df)


import matplotlib.pyplot as plt
#Plotting the MRR by plan
plt.figure(figsize=(10,6))
plt.bar(mrr_by_plan_df['plan_name'], mrr_by_plan_df['mrr'], color = 'skyblue')
plt.xlabel('plan_name')
plt.ylabel('MRR')
plt.title('Monthly Recurring Revenue by Plan')
plt.xticks(rotation = 45)
plt.tight_layout()
plt.show() 