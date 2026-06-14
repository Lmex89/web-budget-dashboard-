# Loguru Conventions

## Setup (`core/logging.py`)

- Removes default stderr sink
- Adds colored stdout with format: `time | level | module:func:line | message`
- Production: adds rotating file sink at `logs/app_*.log` (10 MB, 30 days retention)
- Suppresses health check noise via `HealthCheckFilter`
- Sets third-party loggers (`aiomysql`, `asyncio`, `urllib3`) to `WARNING`

## Per-module usage

```python
from loguru import logger
```

## Log level guide

| Level | When |
|---|---|
| `logger.debug(...)` | SQL queries, parameter dumps, internal state |
| `logger.info(...)` | CRUD operations, auth events, successful mutations |
| `logger.warning(...)` | Validation failures, unauthorized access, not-found |
| `logger.error(...)` | Database failures, unhandled paths |
| `logger.exception(...)` | **Inside `except` blocks only** (auto-captures traceback) |

## Rules

- **Always** use f-strings: `logger.info(f"User {user_id} created")`
- **Never** use `logger.error("msg", exc_info=True)` — use `logger.exception`
- **Never** use `.format()` or `%`-style in log messages

## Route logging convention

```python
# GET (read)
logger.info(f"GET /resource - user={current_user.id}, filters...")

# POST (create)
logger.info(f"POST /resource - user={current_user.id}, data_description")

# PUT (update)
logger.info(f"PUT /resource/{id} - user={current_user.id}, fields...")

# DELETE (delete)
logger.warning(f"DELETE /resource/{id} - user={current_user.id}")
```
