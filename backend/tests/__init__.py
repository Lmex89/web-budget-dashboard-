"""Cross-tenant isolation tests (no DB required).

Covers the defense-in-depth tenant guard and the 404 exception contract for
cross-family object access. Service-level DB-dependent flows are tested
against a live DB separately.
"""
