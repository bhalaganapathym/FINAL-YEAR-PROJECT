# REST API Specification: Persistent AI Data Analyst

The backend exposes a high-performance REST API built on FastAPI.

---

## Base URL
```
http://127.0.0.1:8000
```

---

## Endpoints

### 1. Health Check
Checks backend health and verifies live MySQL database connectivity and latency.

- **Method**: `GET`
- **Route**: `/health`
- **Response**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": {
    "connected": true,
    "database_name": "business_analytics",
    "latency_ms": 2.45,
    "error": null
  }
}
```

---

### 2. Process Natural Language Query
Executes the full LangGraph multi-agent pipeline for a given user query.

- **Method**: `POST`
- **Route**: `/query`
- **Request Body**:
```json
{
  "query": "Show total sales and profit by region for 2024.",
  "conversation_id": "optional-uuid-string"
}
```
- **Response Payload**:
```json
{
  "conversation_id": "7b8e5c12-34f2-498b-9801-6c2e8c9d10ef",
  "question": "Show total sales and profit by region for 2024.",
  "answer": "In 2024, the South region was the top performing territory...",
  "sql": "SELECT r.region_name AS region, SUM(s.revenue) AS total_sales, SUM(s.profit) AS total_profit FROM sales s JOIN regions r ON s.region_id = r.region_id WHERE s.year = 2024 GROUP BY r.region_id, r.region_name ORDER BY total_sales DESC;",
  "data": [
    {"region": "South", "total_sales": 7349140.0, "total_profit": 1501490.0},
    {"region": "West", "total_sales": 6120400.0, "total_profit": 1284500.0},
    {"region": "North", "total_sales": 5410200.0, "total_profit": 1102300.0},
    {"region": "East", "total_sales": 3200100.0, "total_profit": 650000.0}
  ],
  "columns": ["region", "total_sales", "total_profit"],
  "insights": [
    "**Top Territory:** South region led 2024 with INR 7.35M in revenue.",
    "**Profit Contribution:** South and West regions combined accounted for over 60% of total company profit."
  ],
  "visualization": {
    "type": "bar",
    "figure": {
      "data": [...],
      "layout": {...}
    },
    "title": "Total Sales by Region"
  },
  "forecast": null,
  "execution_time_ms": 345.8,
  "error": null
}
```

---

### 3. Retrieve Conversation History
Fetches chronological turn history for a persistent conversation thread.

- **Method**: `GET`
- **Route**: `/conversation/{conversation_id}`
- **Response Payload**:
```json
{
  "conversation_id": "7b8e5c12-34f2-498b-9801-6c2e8c9d10ef",
  "messages": [
    {
      "role": "user",
      "content": "Show total sales by region in 2024",
      "sql": null,
      "data_summary": null
    },
    {
      "role": "assistant",
      "content": "In 2024, the South region was the top performing territory...",
      "sql": "SELECT ...",
      "data_summary": "4 rows returned"
    }
  ]
}
```
