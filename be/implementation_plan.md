# Dataset / Model / Evaluation API — Full Implementation Plan

## 1. Tech Stack

| Concern | Choice |
|---|---|
| Language | Python 3.12 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (sync) |
| DB Driver | psycopg (v3) |
| API framework | FastAPI |
| Validation / schemas | Pydantic v2 |
| Migrations | Alembic |
| Containerization | Docker + docker-compose |
| ASGI server | uvicorn |

**Decisions locked in during planning:**
- Sync SQLAlchemy (simpler code, adequate for this scale, avoids async footguns).
- CRD only (GET/POST/DELETE) — no PUT endpoints. This is a demo; updates aren't needed.
- A standalone insert utility for programmatic/bulk loading, separate from (but reusing validation from) the API.
- Nested reads (`/datasets/{id}`, `/models/{id}`) are **intentionally unbounded** — no pagination or date filtering on the nested TimeStamps/DataSeries collections. This is a known, explicitly-accepted risk to be revisited if/when data volume becomes a problem.
- **All primary keys (and foreign keys) are UUIDs**, not autoincrement integers.
- psycopg (v3) is used instead of psycopg2 for production-readiness and modern API support.

---

## 2. Project Structure

```
be/
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── .env.example
├── main.py                     # FastAPI app + CORS + router registration + exception handlers
├── config.py                   # Settings (env-driven)
├── database.py                 # engine, SessionLocal, get_db dependency
├── alembic/
│   ├── env.py                  # Imports ORM models, reads URL from Settings
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial_schema.py
├── model/
│   ├── __init__.py
│   ├── orm/
│   │   ├── __init__.py         # Re-exports Base + all ORM classes
│   │   ├── base.py             # declarative Base
│   │   ├── model.py            # Model ORM class
│   │   ├── dataset.py          # DataSet ORM class
│   │   ├── dataseries.py       # DataSeries ORM class
│   │   ├── timestamp.py        # TimeStamp ORM class
│   │   ├── metric.py           # Metric ORM class
│   │   └── evaluation.py       # Evaluation ORM class
│   └── schema/
│       ├── __init__.py
│       ├── model.py            # ModelCreate / ModelRead / ModelDetailRead
│       ├── dataset.py          # DataSetCreate / DataSetRead / DataSetDetailRead
│       ├── dataseries.py       # DataSeriesCreate / DataSeriesRead / DataSeriesWithTimestampsRead
│       ├── timestamp.py        # TimeStampCreate / TimeStampRead
│       ├── metric.py           # MetricCreate / MetricRead
│       └── evaluation.py       # EvaluationCreate / EvaluationRead
├── repo/
│   ├── __init__.py
│   ├── base_repo.py            # Standalone CRUD functions (get, get_all, create, delete)
│   ├── model_repo.py
│   ├── dataset_repo.py
│   ├── dataseries_repo.py
│   ├── timestamp_repo.py
│   ├── metric_repo.py
│   └── evaluation_repo.py
├── service/
│   ├── __init__.py
│   ├── model_service.py
│   ├── dataset_service.py
│   ├── dataseries_service.py
│   ├── timestamp_service.py
│   ├── metric_service.py
│   └── evaluation_service.py
├── controller/
│   ├── __init__.py
│   ├── model_controller.py
│   ├── dataset_controller.py
│   ├── dataseries_controller.py
│   ├── timestamp_controller.py
│   ├── metric_controller.py
│   └── evaluation_controller.py
└── util/
    ├── __init__.py
    ├── exceptions.py           # NotFoundError, ConflictError, handlers
    ├── logger.py
    └── db_inserter.py          # Standalone insert utility (no JSON seeding)
```

**Layer responsibilities (request flow):**

`Controller` (FastAPI router — request/response schema only, no logic)
→ `Service` (business rules, FK-existence checks, assembling nested DTOs, raising domain exceptions)
→ `Repo` (SQLAlchemy queries only — no business rules)
→ `Model` (ORM classes + Pydantic schemas)

`Util` sits beside all layers (exceptions, logging, the insert utility) and is imported by whichever layer needs it.

---

## 3. Database Schema

### 3.1 Tables

**models**
| column | type | constraints |
|---|---|---|
| id | UUID | PK, default `uuid4()` |
| name | String(255) | NOT NULL |

**data_sets**
| column | type | constraints |
|---|---|---|
| id | UUID | PK, default `uuid4()` |
| name | String(255) | NOT NULL |
| description | Text | NULL |

**data_series**
| column | type | constraints |
|---|---|---|
| id | UUID | PK, default `uuid4()` |
| name | String(255) | NOT NULL |
| source_model_id | UUID | FK → models.id, **NULL** = ground truth, set = predictions by that model |
| data_set_id | UUID | FK → data_sets.id, NOT NULL |

Indexes: `source_model_id`, `data_set_id`

**timestamps**
| column | type | constraints |
|---|---|---|
| id | UUID | PK, default `uuid4()` |
| date | DateTime (tz-aware) | NOT NULL |
| value | **JSONB** | NOT NULL |
| data_series_id | UUID | FK → data_series.id, NOT NULL |

Indexes: `data_series_id`, composite `(data_series_id, date)` for time-range lookups.

> **UUID strategy:** all primary keys use Postgres native `UUID` columns (UUIDv4), generated at the application layer via SQLAlchemy's `default=uuid.uuid4` rather than a DB-side `gen_random_uuid()`. This means no Postgres extension is required, and IDs are known in Python before the row is actually inserted (useful for the insert utility). FastAPI path parameters (`{id}`) are typed as `uuid.UUID`, which gives automatic `422` validation for malformed IDs for free, with no extra code.

> **Deviation from spec:** the spec lists `Value` as `str (json)`. This plan stores it as native Postgres `JSONB` instead of a plain string. Reasoning: JSONB is directly queryable/indexable in Postgres, validates that the value is actually valid JSON at the DB level, and costs nothing extra to use. If literal string storage is actually required (e.g. you need to preserve exact formatting/whitespace of the original JSON text), swap the column type to `Text` — it's a one-line change in `model/orm/timestamp.py`.

**metrics**
| column | type | constraints |
|---|---|---|
| id | UUID | PK, default `uuid4()` |
| name | String(255) | NOT NULL |
| description | Text | NULL |

**evaluations**
| column | type | constraints |
|---|---|---|
| id | UUID | PK, default `uuid4()` |
| metric_id | UUID | FK → metrics.id, NOT NULL |
| true_data_series_id | UUID | FK → data_series.id, NOT NULL |
| pred_data_series_id | UUID | FK → data_series.id, NOT NULL |
| value | Float | NOT NULL |

Indexes: `metric_id`, `true_data_series_id`, `pred_data_series_id`

### 3.2 Relationships

- `Model` 1 → * `DataSeries` (as source, nullable)
- `DataSet` 1 → * `DataSeries`
- `DataSeries` 1 → * `TimeStamp`
- `Metric` 1 → * `Evaluation`
- `DataSeries` 1 → * `Evaluation` **twice** (as `true_data_series` and as `pred_data_series`)

**Implementation note:** because `Evaluation` has two foreign keys pointing at the same table (`DataSeries`), SQLAlchemy cannot infer which FK a relationship should use. Both relationships must declare `foreign_keys=` explicitly and use distinct `back_populates` names, e.g.:

```python
true_data_series = relationship("DataSeries", foreign_keys=[true_data_series_id], back_populates="true_evaluations")
pred_data_series = relationship("DataSeries", foreign_keys=[pred_data_series_id], back_populates="pred_evaluations")
```

Skipping this raises `AmbiguousForeignKeysError` at import time — this is the single most common SQLAlchemy mistake for this schema shape, worth getting right on the first pass.

### 3.3 Delete policy

| FK | ON DELETE | Rationale |
|---|---|---|
| `data_series.data_set_id` → `data_sets.id` | RESTRICT | Don't silently wipe a dataset's series; force explicit cleanup |
| `data_series.source_model_id` → `models.id` | RESTRICT | Don't orphan-or-cascade a model's predictions silently |
| `timestamps.data_series_id` → `data_series.id` | **CASCADE** | Timestamps have no independent meaning without their series |
| `evaluations.metric_id` → `metrics.id` | RESTRICT | Preserve evaluation history integrity |
| `evaluations.true/pred_data_series_id` → `data_series.id` | RESTRICT | Don't silently destroy evaluation cross-references |

The service layer catches the resulting `IntegrityError` on RESTRICT violations and returns `409 Conflict` with a clear message instead of letting a raw DB error leak out as a 500.

---

## 4. API Routes (CRD — no PUT)

### `/models`
| Method | Path | Description |
|---|---|---|
| GET | `/models` | List all models |
| POST | `/models` | Create a model |
| GET | `/models/{id}` | Model + **all DataSeries** sourced from it |
| DELETE | `/models/{id}` | Delete a model (409 if DataSeries still reference it) |

### `/datasets`
| Method | Path | Description |
|---|---|---|
| GET | `/datasets` | List all datasets |
| POST | `/datasets` | Create a dataset |
| GET | `/datasets/{id}` | Dataset + **all DataSeries** + **all TimeStamps** for those series |
| DELETE | `/datasets/{id}` | Delete a dataset (409 if DataSeries still reference it) |

### `/dataseries`
| Method | Path | Description |
|---|---|---|
| GET | `/dataseries` | List all data series (flat, no nested timestamps) |
| POST | `/dataseries` | Create a data series (`data_set_id` required, `source_model_id` optional) |
| GET | `/dataseries/{id}` | Single data series + its TimeStamps |
| DELETE | `/dataseries/{id}` | Delete (cascades TimeStamps; 409 if referenced by an Evaluation) |

### `/timestamps`
| Method | Path | Description |
|---|---|---|
| GET | `/timestamps` | List all timestamps (flat — primarily an admin/debug route) |
| POST | `/timestamps` | Create a timestamp (`data_series_id` required) |
| GET | `/timestamps/{id}` | Single timestamp |
| DELETE | `/timestamps/{id}` | Delete a timestamp |

### `/metrics`
| Method | Path | Description |
|---|---|---|
| GET | `/metrics` | List all metrics |
| POST | `/metrics` | Create a metric |
| GET | `/metrics/{id}` | Single metric |
| DELETE | `/metrics/{id}` | Delete (409 if referenced by an Evaluation) |

### `/evaluations`
| Method | Path | Description |
|---|---|---|
| GET | `/evaluations` | List all evaluations |
| POST | `/evaluations` | Create (`metric_id`, `true_data_series_id`, `pred_data_series_id`, `value`) |
| GET | `/evaluations/{id}` | Single evaluation |
| DELETE | `/evaluations/{id}` | Delete an evaluation |

---

## 5. Layer Details

### 5.1 `model/orm/*.py`
Plain SQLAlchemy 2.0 declarative classes (`Mapped[...]`, `mapped_column(...)`), one file per table, all inheriting from a shared `Base` in `base.py`. Relationships declared per Section 3.2/3.3.

Primary keys use the Postgres-native UUID type with a Python-side default:
```python
import uuid
from sqlalchemy.dialects.postgresql import UUID

id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```
Foreign key columns use the same `UUID(as_uuid=True)` type.

### 5.2 `model/schema/*.py`
Per entity, at minimum:
- `XCreate` — fields required to create (no `id`)
- `XRead` — flat representation returned by list/create endpoints
- `XDetailRead` — nested representation for special routes (`DataSetDetailRead` embeds `data_series: list[DataSeriesWithTimestampsRead]`; `ModelDetailRead` embeds `data_series: list[DataSeriesRead]`)

**No `XUpdate` schemas** — PUT operations are intentionally omitted for this demo.

All `Read` schemas use `model_config = ConfigDict(from_attributes=True)` so they can be built directly from ORM objects.

### 5.3 `repo/*.py`
`base_repo.py` defines standalone functions parametrized by model class: `get(db, model_class, id)`, `get_all(db, model_class)`, `create(db, model_class, **kwargs)`, `delete(db, obj)`. Entity repos extend with query-specific methods, e.g.:

```python
class DataSetRepo:
    @staticmethod
    def get_with_series_and_timestamps(db: Session, id: uuid.UUID) -> DataSet | None:
        return (
            db.query(DataSet)
            .options(selectinload(DataSet.data_series).selectinload(DataSeries.timestamps))
            .filter(DataSet.id == id)
            .first()
        )
```

`selectinload` (not `joinedload`) is used for the one-to-many nested fetch — it issues a second query with `WHERE id IN (...)` rather than one giant join, avoiding a row-multiplication blowup when a dataset has many series with many timestamps each.

### 5.4 `service/*.py`
Owns business rules the repo layer shouldn't know about:
- Verify `data_set_id` exists before creating a `DataSeries`
- Verify `source_model_id` exists (if provided) before creating a `DataSeries`
- Verify `metric_id`, `true_data_series_id`, `pred_data_series_id` exist before creating an `Evaluation`
- Catch `IntegrityError` from RESTRICT-policy deletes and re-raise as `ConflictError` (→ 409)
- Assemble `*DetailRead` schemas for nested-read endpoints

**No `update` methods** — PUT is intentionally excluded.

### 5.5 `controller/*.py`
Thin FastAPI routers. No business logic — parse request → call service → return response schema. One `APIRouter` per entity, all included in `main.py` with plural prefixes (`/models`, `/datasets`, `/dataseries`, `/timestamps`, `/metrics`, `/evaluations`). No PUT route handlers.

### 5.6 `util/exceptions.py`
```python
class NotFoundError(Exception): ...
class ConflictError(Exception): ...
```
Registered in `main.py` via `@app.exception_handler(...)` mapping `NotFoundError → 404`, `ConflictError → 409`, and a catch-all handler for unmapped `IntegrityError` → 409 as a safety net.

### 5.7 `util/db_inserter.py` — the insert utility
A standalone module for bulk-loading data outside the HTTP API (seeding, backfills, batch loads). Provides individual `insert_*` methods for programmatic use.

**No JSON file seeding** — the `load_from_json` method and CLI entrypoint are intentionally omitted for this demo.

```python
class DBInserter:
    def __init__(self, db: Session):
        self.db = db

    def insert_model(self, name: str) -> Model: ...
    def insert_dataset(self, name: str, description: str | None) -> DataSet: ...
    def insert_dataseries(self, name: str, data_set_id: uuid.UUID, source_model_id: uuid.UUID | None) -> DataSeries: ...
    def insert_timestamps_bulk(self, data_series_id: uuid.UUID, records: list[dict]) -> int:
        # uses session.execute(insert(TimeStamp), records) for batch performance
        ...
    def insert_metric(self, name: str, description: str | None) -> Metric: ...
    def insert_evaluation(self, metric_id: uuid.UUID, true_id: uuid.UUID, pred_id: uuid.UUID, value: float) -> Evaluation: ...
```

### 5.8 `util/logger.py`
Standard `logging` config (structured, level from env), imported wherever needed.

---

## 6. Configuration & Database Setup

**`config.py`** — Pydantic `BaseSettings` reading from environment/`.env`:
```python
class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
```

**`database.py`**:
```python
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**`.env.example`**:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=koop
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 7. Docker Setup

**`Dockerfile`**:
```dockerfile
FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`docker-compose.yml`**:
```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: koop
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  app:
    build: .
    container_name: fastapi_app
    restart: always
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - .:/code
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

Migrations are applied manually:
```bash
docker-compose exec app alembic upgrade head
```

**`requirements.txt`**:
```
fastapi
uvicorn[standard]
sqlalchemy>=2.0
psycopg[binary]
pydantic>=2
pydantic-settings
alembic
```

---

## 8. Migrations

**Alembic:** `alembic.ini` points to `alembic/` directory. `alembic/env.py`:
1. Imports `Base` from `model.orm` (which re-exports all ORM models, ensuring `Base.metadata` is populated)
2. Reads DB URL from `config.Settings` and sets it on the Alembic config
3. Sets `target_metadata = Base.metadata`

The initial migration creates all six tables with the FKs/indexes/ON DELETE rules from Section 3.

---

## 9. Known Risks / Explicitly Accepted Tradeoffs

1. **Unbounded nested reads (accepted, deferred).** `/datasets/{id}` returns every DataSeries and every TimeStamp for that dataset; `/models/{id}` returns every DataSeries for that model. No pagination, no date-range filtering. TimeStamps grows unboundedly over time by nature, so this endpoint's response size and latency will get worse over time even with zero other changes. You've chosen to keep this as-is for now — the query-param based fix (`?from=&to=&limit=&offset=`) is straightforward to retrofit later without changing the route shape.

2. **RESTRICT-by-default delete policy.** Deleting a `DataSet`/`Model`/`Metric` with dependents requires explicit cleanup first, surfaced as a 409.

3. **`TimeStamps.Value` implemented as JSONB, not a literal string**, despite the spec listing `str (json)`. Easy to revert to `Text` if literal string preservation is actually required.

4. **UUIDv4 primary keys will fragment the index on high-insert-volume tables, especially `timestamps`.** Random UUIDs insert in random order into a B-tree index. For a table that grows continuously by nature (time series data), this means more index bloat and slower writes over time than integer keys would have. On the current scale (~20 datasets with ~7k timestamps each) this is not a concern. If write throughput on `timestamps` ever becomes a bottleneck, a time-ordered UUID variant (UUIDv7) or a separate internal clustering column are both options.

5. **Sync SQLAlchemy with FastAPI.** The event loop blocks on every DB call. Under high concurrent load, this serializes database operations. Adequate for demo scale; switch to `AsyncSession` + `asyncpg` if concurrency becomes a bottleneck.

---

## 10. Suggested Build Order

1. Scaffold folders, `requirements.txt`, Docker files → confirm `docker-compose up` gets a bare FastAPI health-check talking to Postgres.
2. ORM models (`model/orm/*.py`) with correct relationships, `foreign_keys=` disambiguation on `Evaluation`, and ON DELETE rules.
3. Alembic init → generate & apply the initial migration.
4. Pydantic schemas (`model/schema/*.py`), including the two `*DetailRead` nested schemas.
5. `base_repo.py` with standalone CRUD functions → entity repos, including the `selectinload`-based nested fetch queries.
6. Services (FK validation, exception translation, DTO assembly for nested reads).
7. Controllers/routers for all six entities, wired into `main.py`.
8. `util/db_inserter.py` (individual insert methods, no JSON seeding).
9. Global exception handlers (404 / 409 / 422 / 500 formatting) in `main.py`.
10. Seed sample data through the insert utility; manually exercise the two nested GET routes end-to-end.
