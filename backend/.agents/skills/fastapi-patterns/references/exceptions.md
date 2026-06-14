# Exception Handling

## Class hierarchy

```
AppException (base)
├── NotFoundException (404)
│   ├── ExpenseNotFoundException
│   └── (add per-domain)
├── UnauthorizedException (401)
│   └── InvalidCredentialsException
├── ForbiddenException (403)
│   └── ExpenseNotInFamilyException
├── ValidationException (422)
│   ├── InvalidCategoryForExpenseException
│   ├── InvalidCreditCardForExpenseException
│   └── InstallmentMisconfigurationException
├── ConflictException (409)
│   └── EmailAlreadyRegisteredException
```

## When to create a new exception

- New 404 case → `NotFoundException("ResourceName", id)` or subclass
- New 401 case → `UnauthorizedException("message")` or subclass
- New 403 case → `ForbiddenException("message")` or subclass
- New 422 input error → `ValidationException("message", details_dict)`
- New 409 conflict → `ConflictException("message")` or subclass

## Global handlers (registered in `main.py`)

| Exception | Status | Response shape |
|---|---|---|
| `AppException` | dynamic | `{success: false, error: {code, message, details?}}` |
| `RequestValidationError` | 422 | `{success: false, error: {code: "ERR_VALIDATION", message, details: {field: msg}}}` |
| `SQLAlchemyError` | 500 | `{success: false, error: {code: "ERR_DATABASE", message: "..."}}` |
| `Exception` | 500 | `{success: false, error: {code: "ERR_INTERNAL", message: "..."}}` |

## DB error wrapping

Every repository method wraps `SQLAlchemyError`:

```python
try:
    result = await self.db.execute(...)
    return result.scalar_one_or_none()
except SQLAlchemyError:
    logger.exception("Database error fetching ...")
    raise AppException("ERR_DATABASE", "Failed to fetch ...")
```
