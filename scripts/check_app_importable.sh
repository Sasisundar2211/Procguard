#!/bin/bash
#
# CI/CD Safety Check: Verifies that the main FastAPI application is importable.
#
# This script prevents a common class of deployment failures where refactoring,
# dependency changes, or circular imports break the application entrypoint.
# It fails with a non-zero exit code if `app.main` cannot be imported.

set -e

echo "--- Verifying ASGI application importability ---"

# The -c flag tells Python to execute the command.
# We attempt to import the 'main' module from the 'app' package.
# If this fails, Python will exit with an error, which `set -e` will catch.
python -c "from app import main"

echo "✅ Success: ASGI application (app.main) is importable."
echo "------------------------------------------------"

