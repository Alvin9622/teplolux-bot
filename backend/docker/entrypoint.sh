#!/bin/sh
# ============================================================================
# Container entrypoint.
# Applies pending database migrations, then hands off to the main process.
# ============================================================================
set -e

echo "[entrypoint] Applying database migrations (prisma migrate deploy)..."
npx prisma migrate deploy

echo "[entrypoint] Starting application: $*"
exec "$@"
