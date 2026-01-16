# SaaS Subscription Analytics

## Overview
This project analyzes a simulated SaaS subscription business using PostgreSQL and Python.  
The focus is on **correct analytical logic**, not just visualization.

## Metrics Analyzed
- Active Users
- Churn Rate
- Monthly Recurring Revenue (MRR)
- MRR by Subscription Plan

## Tech Stack
- PostgreSQL
- SQL (joins, CTEs, aggregation)
- Python (psycopg2, pandas, matplotlib)

## Key Learnings
- Designed a relational schema for a SaaS product
- Modeled subscription lifecycle using start and end dates
- Calculated churn correctly without relying on payment history
- Integrated SQL analytics into Python
- Visualized revenue distribution across plans

## Sample Visualization
![MRR by Plan](screenshots/mrr_by_plan.png)
