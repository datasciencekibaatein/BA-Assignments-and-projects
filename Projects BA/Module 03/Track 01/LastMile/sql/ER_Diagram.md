# DataCo Global - Entity Relationship Diagram

The 3NF schema for the Last-Mile Delivery Audit. Render this with any Mermaid-compatible viewer (GitHub, Mermaid Live Editor, or VS Code extension).

```mermaid
erDiagram
    MARKETS ||--o{ REGIONS : "groups"
    REGIONS ||--o{ ROUTES : "destination"
    SHIPPING_MODES ||--o{ ORDERS : "served by"
    DEPARTMENTS ||--o{ CATEGORIES : "contains"
    CATEGORIES ||--o{ PRODUCTS : "contains"
    CUSTOMERS ||--o{ ORDERS : "places"
    ROUTES ||--o{ ORDERS : "follows"
    ORDERS ||--o{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "appears in"

    MARKETS {
        int market_id PK
        string market_name UK
    }
    REGIONS {
        int region_id PK
        string region_name UK
        int market_id FK
    }
    SHIPPING_MODES {
        int mode_id PK
        string mode_name UK
        decimal sla_scheduled_days
        text description
    }
    DEPARTMENTS {
        int department_id PK
        string department_name UK
    }
    CATEGORIES {
        int category_id PK
        string category_name
        int department_id FK
    }
    PRODUCTS {
        int product_id PK
        string product_name
        int category_id FK
        decimal list_price
    }
    CUSTOMERS {
        int customer_id PK
        string customer_fname
        string customer_lname
        string customer_segment
        string customer_city
        string customer_state
        string customer_country
    }
    ROUTES {
        int route_id PK
        string origin_state
        string destination_state
        string destination_country
        int region_id FK
    }
    ORDERS {
        bigint order_id PK
        int customer_id FK
        int route_id FK
        int mode_id FK
        timestamp order_date
        timestamp shipping_date
        decimal days_shipping_real
        decimal days_shipping_sched
        string delivery_status
        boolean late_delivery_risk
        string order_status
        decimal order_profit
    }
    ORDER_ITEMS {
        bigint order_item_id PK
        bigint order_id FK
        int product_id FK
        int quantity
        decimal unit_price
        decimal discount
        decimal item_total
        decimal profit_ratio
    }
```

## Why these tables in 3NF

| Table | What it normalizes | What gets eliminated |
|---|---|---|
| `markets` | 5-value lookup (Africa, Europe, LATAM, Pacific Asia, USCA) | "Market" string repetition across every order row |
| `regions` | 23 sub-market regions | "Region" string repetition; transitive Region→Market dependency |
| `routes` | ~12K origin-destination pairs | Repeated origin/destination state pairs across orders |
| `shipping_modes` | 4-mode SLA lookup | SLA values that would otherwise be hard-coded per row |
| `customers` | 20K customers | Customer name/address repeated for every order they place |
| `categories` | Product taxonomy nested under departments | Department-name repetition across products |

## Row counts after load

| Table | Rows |
|---|---:|
| markets | 5 |
| regions | 23 |
| shipping_modes | 4 |
| departments | 11 |
| categories | 51 |
| products | 118 |
| customers | 20,652 |
| routes | 11,899 |
| **orders** | **65,752** |
| **order_items** | **180,519** |

The 180,519 `order_items` are the rows of the source CSV — each row is one product line, but multiple lines belong to the same `order_id`. This was the most important normalization step: 65,752 unique orders, not 180,519.

## Note on Routes / Vehicles / Fuel_Logs

The brief asks for `Routes`, `Vehicles`, and `Fuel_Logs` tables. The DataCo dataset is a marketplace dataset without per-vehicle or fuel data, so we substitute:

- **Routes** is built (origin-destination state pairs derived from customer and order locations)
- **Vehicles** is replaced by `shipping_modes` — these are the operationally-equivalent service tiers (Standard / First / Second / Same Day Class). Each has its own SLA and OEE profile, exactly like a fleet tier would.
- **Fuel_Logs** is omitted rather than fabricated. The OEE Performance metric (scheduled_days / actual_days) captures the same "energy efficiency" idea fuel logs would.

This is documented at the top of `schema.sql`.
