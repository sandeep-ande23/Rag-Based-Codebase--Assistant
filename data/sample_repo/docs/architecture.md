# Architecture

The application exposes a FastAPI backend. Database access is isolated in
the database module. Orders call the database layer rather than creating
their own engine.

## Deployment

The application can run in Docker. Environment variables provide deployment
configuration such as the database URL.
