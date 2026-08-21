"""Tests for the global SQLAlchemy tenant guard."""
import pytest
from fastapi import status
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import ExpenseNotInFamilyException, NotFoundException
from app.core.tenant import set_tenant_context, clear_tenant_context
from app.db.tenant_guard import _apply_tenant_guard, _TENANT_MODELS
from app.models import Expense


class _FakeExecuteState:
    """Minimal stand-in for a SQLAlchemy do_orm_execute event state."""

    def __init__(self, statement, is_select=True, is_column_load=False, is_relationship_load=False):
        self.statement = statement
        self.is_select = is_select
        self.is_column_load = is_column_load
        self.is_relationship_load = is_relationship_load


@pytest.fixture
def enabled_guard(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_GLOBAL_TENANT_GUARD", True)


@pytest.fixture(autouse=True)
def clean_tenant_context():
    clear_tenant_context()
    yield
    clear_tenant_context()


def _compiled_sql(state) -> str:
    return str(state.statement.compile(compile_kwargs={"literal_binds": False}))


def _has_family_predicate(state) -> bool:
    return "family_id" in _compiled_sql(state)


def test_guard_injects_criteria_for_tenant_models(enabled_guard):
    set_tenant_context("family-A")
    state = _FakeExecuteState(select(Expense.id), is_select=True)
    _apply_tenant_guard(state)
    assert _has_family_predicate(state)


def test_guard_skipped_when_flag_disabled():
    # default flag is disabled unless explicitly enabled
    set_tenant_context("family-A")
    state = _FakeExecuteState(select(Expense.id))
    _apply_tenant_guard(state)
    assert not _has_family_predicate(state)


def test_guard_skipped_without_tenant_context(enabled_guard):
    state = _FakeExecuteState(select(Expense.id))
    _apply_tenant_guard(state)
    assert not _has_family_predicate(state)


def test_guard_skipped_for_column_and_relationship_loads(enabled_guard):
    set_tenant_context("family-A")
    state = _FakeExecuteState(select(Expense.id), is_column_load=True)
    _apply_tenant_guard(state)
    assert not _has_family_predicate(state)


def test_guard_skipped_for_non_select(enabled_guard):
    set_tenant_context("family-A")
    state = _FakeExecuteState(select(Expense.id), is_select=False)
    _apply_tenant_guard(state)
    assert not _has_family_predicate(state)


def test_guard_filters_any_tenant_model(enabled_guard):
    """Each guarded model independently carries the family predicate."""
    set_tenant_context("family-A")
    for model in _TENANT_MODELS:
        state = _FakeExecuteState(select(model.id), is_select=True)
        _apply_tenant_guard(state)
        assert _has_family_predicate(state), f"Missing family predicate for {model.__name__}"


def test_parametrized_tenant_models_have_family_id(enabled_guard):
    """Every guarded model must expose a family_id column."""
    for model in _TENANT_MODELS:
        assert "family_id" in model.__table__.columns


def test_cross_family_exception_is_404():
    exc = ExpenseNotInFamilyException("expense-1")
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert "expense-1" in exc.message
    assert isinstance(exc, NotFoundException)
