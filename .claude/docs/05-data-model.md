# Local Data Model

Trino at `localhost:8081`. Two catalogs with sample data. Tables marked **partitioned** have partition keys the agent must filter on.

## Catalog: `hive`

### `hive.sales.customers`

| Column | Type | Notes |
|--------|------|-------|
| customer_id | int | PK |
| customer_name | varchar | |
| region | varchar | NA, EU, APAC |

### `hive.sales.orders` — **partitioned by `order_date`**

| Column | Type | Notes |
|--------|------|-------|
| order_id | int | |
| customer_id | int | FK → customers |
| amount | decimal | |
| order_date | date | Partition key |

### `hive.warehouse.products`

| Column | Type | Notes |
|--------|------|-------|
| product_id | int | |
| product_name | varchar | |
| price | decimal | |
| category | varchar | Electronics, Furniture |

### `hive.warehouse.stock_levels` — **partitioned by `snapshot_date`**

| Column | Type | Notes |
|--------|------|-------|
| product_id | int | FK → products |
| quantity | int | |
| warehouse_location | varchar | US-WEST, US-EAST, EU-CENTRAL |
| snapshot_date | date | Partition key |

## Catalog: `iceberg`

### `iceberg.activity.events` — **partitioned by `event_date`**

| Column | Type | Notes |
|--------|------|-------|
| event_id | int | |
| customer_id | int | FK → hive.sales.customers (cross-catalog) |
| event_name | varchar | page_view, checkout, login |
| event_ts | timestamp | |
| region | varchar | |
| event_date | date | Partition key |

### `iceberg.activity.user_sessions`

| Column | Type | Notes |
|--------|------|-------|
| session_id | varchar | SES### format |
| customer_id | int | FK → hive.sales.customers |
| session_start | timestamp | |
| session_end | timestamp | |
| page_views | int | |

### `iceberg.logistics.shipments` — **partitioned by `shipped_date`**

| Column | Type | Notes |
|--------|------|-------|
| shipment_id | int | |
| order_id | int | FK → hive.sales.orders (cross-catalog) |
| status | varchar | IN_TRANSIT, DELIVERED, PENDING |
| shipped_date | date | Partition key |

### `iceberg.logistics.delivery_routes`

| Column | Type | Notes |
|--------|------|-------|
| route_id | varchar | RT### format |
| origin_location | varchar | Matches warehouse_location style |
| destination_location | varchar | |
| distance_km | decimal | |
| estimated_days | int | |

## Join graph

```
customers ─── customer_id ──► orders ─── order_id ──► shipments
    │
    ├── customer_id ──► events
    │
    └── customer_id ──► user_sessions

products ─── product_id ──► stock_levels

delivery_routes ── location strings (fuzzy) ── stock_levels.warehouse_location
```

## Notes for the agent

- Cross-catalog joins are common. Always use fully qualified names.
- Partition-key filters are essential for orders, stock_levels, events, shipments.
- delivery_routes has no clean FK join — connection is via location strings. Agent should flag this.
- All tables are small (3–4 rows). Dataset is for correctness, not load testing.

## Benchmark questions (20)

1. List all customers.
2. Which customers are in the EU region?
3. What is the total order amount per customer?
4. Which orders were placed in February 2026?
5. Which customers have any pending shipments?
6. What is the average page views per session?
7. Which products are below 50 units in stock?
8. What is the total revenue per region?
9. What was Alice's first action in the system?
10. For each customer, how many orders are delivered vs in transit vs pending?
11. Which warehouse locations stock electronics?
12. How long does the average user session last?
13. Show all events before a checkout, grouped by customer.
14. Which delivery routes are longer than 200 km?
15. For each region, what's the most popular event_name?
16. What's the latest snapshot date in stock_levels?
17. Which orders shipped on the same day they were placed?
18. Are there customers without any recorded activity events?
19. What's the total stock value (quantity × price) per warehouse?
20. List all orders not yet delivered.
