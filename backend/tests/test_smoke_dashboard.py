"""API smoke tests for the dashboard endpoints.

These tests run against the real database and the seeded admin user
(``backend/.env`` + running MariaDB). Run them before/after any backend change:

    pytest tests/test_smoke_dashboard.py -v

Coverage:
- Every dashboard read endpoint returns 200 with a successful envelope.
- Expense CRUD round-trip, including installment generation and reading
  persisted installments (guards the ``InstallmentStatus`` enum mapping).
- Budget upsert/progress/list/delete round-trip.
- Debt create/list round-trip (guards ``DebtType``/``DebtStatus`` mappings).
- Bounded SQL statement counts, to catch the eager-loading cascade regression
  where a single request fanned out into 20+ SELECTs.
"""
import uuid
from datetime import date

import httpx
import pytest
from loguru import logger
from sqlalchemy import event, text

from app.db.session import AsyncSessionLocal, engine
from app.main import app

logger.remove()

ADMIN_EMAIL = "admin@family.com"
ADMIN_PASSWORD = "admin123"

TODAY = date.today()

READ_ENDPOINTS = [
    "/api/v1/auth/me",
    "/api/v1/auth/users",
    "/api/v1/categories",
    "/api/v1/credit-cards",
    "/api/v1/debts",
    "/api/v1/expenses?page=1&page_size=25",
    f"/api/v1/expenses/analytics/monthly-summary?year={TODAY.year}&month={TODAY.month}",
    f"/api/v1/expenses/analytics/category-distribution?year={TODAY.year}&month={TODAY.month}",
    f"/api/v1/expenses/analytics/monthly-trend?year={TODAY.year}",
    "/api/v1/expenses/installments/overdue",
    f"/api/v1/budgets/progress?year={TODAY.year}&month={TODAY.month}",
    "/api/v1/audit-logs?page=1&page_size=10",
]


class QueryCounter:
    """Count SQL statements emitted while the context is active."""

    def __init__(self) -> None:
        self.statements = 0

    def _on_execute(self, conn, cursor, statement, parameters, context, executemany) -> None:
        self.statements += 1

    def __enter__(self) -> "QueryCounter":
        event.listen(engine.sync_engine, "before_cursor_execute", self._on_execute)
        return self

    def __exit__(self, *exc_info) -> None:
        event.remove(engine.sync_engine, "before_cursor_execute", self._on_execute)


def _unique(prefix: str) -> str:
    return f"{prefix} {uuid.uuid4().hex[:8]}"


async def _soft_delete(table: str, name: str) -> None:
    async with AsyncSessionLocal() as db:
        await db.execute(
            text(f"UPDATE {table} SET deleted_at = NOW() WHERE name = :name AND deleted_at IS NULL"),
            {"name": name},
        )
        await db.commit()


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await engine.dispose()


@pytest.fixture
async def auth_headers(client) -> dict:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


@pytest.mark.parametrize("path", READ_ENDPOINTS)
async def test_dashboard_read_endpoint_returns_200(client, auth_headers, path):
    response = await client.get(path, headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json()["success"] is True


async def test_expense_and_installment_roundtrip(client, auth_headers):
    category_name = _unique("Smoke Cat")
    response = await client.post(
        "/api/v1/categories",
        json={"name": category_name, "color": "#336699"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    category_id = response.json()["data"]["id"]

    created_card_name = None
    try:
        response = await client.get("/api/v1/credit-cards", headers=auth_headers)
        cards = response.json()["data"]
        if cards:
            card_id = cards[0]["id"]
        else:
            created_card_name = _unique("Smoke Card")
            response = await client.post(
                "/api/v1/credit-cards",
                json={
                    "name": created_card_name,
                    "limit": "1000.00",
                    "closing_day": 5,
                    "due_day": 10,
                },
                headers=auth_headers,
            )
            assert response.status_code == 201, response.text
            card_id = response.json()["data"]["id"]

        response = await client.post(
            "/api/v1/expenses",
            json={
                "amount": "10.50",
                "description": "smoke cash expense",
                "date": "2027-03-15T12:00:00",
                "payment_method": "cash",
                "category_id": category_id,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201, response.text
        expense_id = response.json()["data"]["id"]

        response = await client.put(
            f"/api/v1/expenses/{expense_id}",
            json={"amount": "11.00"},
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        assert float(response.json()["data"]["amount"]) == 11.0

        response = await client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
        assert response.status_code == 200, response.text

        response = await client.post(
            "/api/v1/expenses",
            json={
                "amount": "300.00",
                "description": "smoke installment expense",
                "date": "2027-03-10T12:00:00",
                "payment_method": "credit",
                "category_id": category_id,
                "credit_card_id": card_id,
                "is_installment": True,
                "total_installments": 3,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201, response.text
        installment_expense_id = response.json()["data"]["id"]

        async with AsyncSessionLocal() as db:
            await db.execute(
                text(
                    "UPDATE installments SET due_date = NOW() - INTERVAL 1 DAY "
                    "WHERE expense_id = :expense_id"
                ),
                {"expense_id": installment_expense_id},
            )
            await db.commit()

        response = await client.get("/api/v1/expenses/installments/overdue", headers=auth_headers)
        assert response.status_code == 200, response.text
        overdue = response.json()["data"]
        assert any(item["expense_id"] == installment_expense_id for item in overdue)

        for expense in (expense_id, installment_expense_id):
            response = await client.delete(f"/api/v1/expenses/{expense}", headers=auth_headers)
            assert response.status_code == 200, response.text
    finally:
        response = await client.delete(f"/api/v1/categories/{category_id}", headers=auth_headers)
        assert response.status_code == 200, response.text
        if created_card_name:
            await _soft_delete("credit_cards", created_card_name)


async def test_budget_roundtrip(client, auth_headers):
    year, month = 2099, 12
    response = await client.get("/api/v1/categories", headers=auth_headers)
    categories = response.json()["data"]
    assert categories, "Expected at least one seeded category"
    category_id = categories[0]["id"]

    response = await client.put(
        f"/api/v1/budgets/{year}/{month}",
        json={
            "total_budget": "1234.00",
            "categories": [{"category_id": category_id, "amount": "100.00"}],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    budget_id = response.json()["data"]["id"]

    try:
        response = await client.get(
            f"/api/v1/budgets/progress?year={year}&month={month}", headers=auth_headers
        )
        assert response.status_code == 200, response.text
        progress = response.json()["data"]
        assert progress["budget_id"] == budget_id
        assert progress["total_budget"] == 1234.0

        response = await client.get(f"/api/v1/budgets?year={year}", headers=auth_headers)
        assert response.status_code == 200, response.text
        assert any(budget["id"] == budget_id for budget in response.json()["data"])
    finally:
        response = await client.delete(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
        assert response.status_code == 200, response.text


async def test_debt_create_and_list(client, auth_headers):
    debt_name = _unique("Smoke Debt")
    response = await client.post(
        "/api/v1/debts",
        json={"name": debt_name, "original_amount": "100.00", "type": "we_owe"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    debt = response.json()["data"]
    assert debt["type"] == "we_owe"
    assert debt["status"] == "active"

    try:
        response = await client.get("/api/v1/debts", headers=auth_headers)
        assert response.status_code == 200, response.text
        assert any(item["name"] == debt_name for item in response.json()["data"])
    finally:
        await _soft_delete("debts", debt_name)


async def test_category_list_query_count_is_bounded(client, auth_headers):
    with QueryCounter() as counter:
        response = await client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert counter.statements <= 6, f"category list fanned out into {counter.statements} SQL statements"


async def test_monthly_trend_is_single_aggregation(client, auth_headers):
    with QueryCounter() as counter:
        response = await client.get(
            f"/api/v1/expenses/analytics/monthly-trend?year={TODAY.year}",
            headers=auth_headers,
        )
    assert response.status_code == 200, response.text
    assert len(response.json()["data"]) == 12
    assert counter.statements <= 6, f"monthly trend fanned out into {counter.statements} SQL statements"
