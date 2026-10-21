# AWY Automotive Backend

Production-grade data retrieval layer, hybrid search engine, and financial calculation backbone for **AWY**, an AI-powered automotive assistant covering both 4-wheelers and 2-wheelers in the Indian market.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11+** (Python 3.13 tested)
- *(Optional for Containerization)* **Docker & Docker Compose**

---

### Option 1: Standalone Local Run (No Docker Required)

The project includes an automatic embedded fallback for both relational storage (`SQLite`) and vector search (`Embedded Qdrant on disk`), enabling instant zero-dependency local development.

#### 1. Activate the Virtual Environment
On Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```
*(Or create a new one if starting from scratch)*:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 2. Run Data Ingestion (Initial Setup)
Ingests the 20 pilot Indian vehicles (specs, multi-state pricing, and review vectors):
```powershell
python scripts/ingest_data.py
```

#### 3. Start the FastAPI Dev Server
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. Open Interactive API Documentation
- **Swagger UI**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **ReDoc**: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Option 2: Docker Compose (Full Production Stack)

Runs PostgreSQL 16 with the `pgvector` extension, Qdrant Vector Engine, and FastAPI inside isolated containers.

```bash
docker compose up --build -d
```
To view logs:
```bash
docker compose logs -f api
```
To stop:
```bash
docker compose down
```

---

## 🧪 Running Automated Tests

Run the full test suite (database schema, health check, knowledge base, and 35-query hybrid search benchmark):
```powershell
pytest -v
```

To run only the hybrid search benchmark with latency printouts:
```powershell
pytest tests/test_hybrid_search.py -v -s
```

---

## 📡 Sample API Requests

### 1. Hybrid Search (`POST /api/v1/search`)
Query with natural language hard constraints (enforces category, price ceiling, and ABS type):
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bikes with dual-channel ABS under 2L",
    "top_k": 3
  }'
```

### 2. Vehicle Structured Specs (`GET /api/v1/vehicles/{id}/specs`)
Retrieve vehicle variants, dimensions, NCAP ratings, and state-wise pricing history (<20ms):
```bash
curl "http://localhost:8000/api/v1/vehicles/<VEHICLE_UUID>/specs"
```

### 3. Vehicle Comparison Matrix (`GET /api/v1/vehicles/compare`)
Compare multiple vehicles side-by-side:
```bash
curl "http://localhost:8000/api/v1/vehicles/compare?ids=<UUID_1>,<UUID_2>"
```

### 4. On-Road Price Estimation (`POST /api/v1/calculate/on-road-price`)
```bash
curl -X POST "http://localhost:8000/api/v1/calculate/on-road-price" \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "00000000-0000-0000-0000-000000000000",
    "state_code": "MH",
    "ex_showroom_price": 1100000.0
  }'
```

### 5. Reducing-Balance EMI Calculation (`POST /api/v1/calculate/emi`)
```bash
curl -X POST "http://localhost:8000/api/v1/calculate/emi" \
  -H "Content-Type: application/json" \
  -d '{
    "on_road_price": 1250000.0,
    "down_payment": 250000.0,
    "tenure_months": 60,
    "interest_rate_annual": 9.5
  }'
```

---

## 🏗️ Architecture & Core Components

- **`app/services/query_parser.py`**: Rule-based natural language query understanding that extracts hard constraints (budget ceilings, 2W vs 4W categories, ABS types, NCAP safety ratings) before semantic vector search to eliminate semantic drift.
- **`app/services/embedding_service.py`**: Local CPU-optimized embedding pipeline via FastEmbed (`BAAI/bge-small-en-v1.5`, 384 dimensions).
- **`app/services/bm25_service.py`**: Sparse Okapi BM25 engine for technical nomenclature, trims, and feature codes.
- **`app/services/hybrid_search_service.py`**: Combines dense vector retrieval with BM25 using Reciprocal Rank Fusion (RRF).
- **`app/services/ingestion_service.py`**: Idempotent data ingestion with SHA-256 chunk hashing and version auditing.
