# Auth JWKS Cleanup Rollout

## Runtime-first rollout

1. Deploy the JWKS-backed runtime cutover.
2. Validate at least one protected write using a real OrgAuth-issued bearer access token.
3. Confirm missing bearer tokens return `401 Missing bearer token` and invalid tokens return `401 Invalid token`.
4. Confirm public GET routes remain accessible without auth.

## Schema cleanup checkpoint

Apply `migrations/0008_drop_legacy_auth.sql` **only after** the runtime checks above pass in the target environment.

This migration drops the legacy in-house auth tables and related refresh/session artifacts, so rollback to the old runtime is no longer safe after it runs.
