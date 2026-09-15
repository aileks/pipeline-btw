# Pipeline - Breweries To Watch

Pipeline practice on the [Breweries API](https://openbrewerydb.org) using ETL and Pydantic validation.

Airflow runs two supported ways: locally or through Docker Compose.

## Python environment

```bash
uv sync
source .venv/bin/activate

# to exit the venv
deactivate
```

## Local Airflow

Requires a local postgres instance. Both the `airflow` metadata database and the `breweries` pipeline database live there.

Copy `.env.example` to `.env` and set:

- `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` - the `airflow` metadata database (create it once with `createdb airflow`)
- `DB_URL` - the `breweries` pipeline database the DAG writes to
- `AIRFLOW_HOME`, `AIRFLOW__CORE__EXECUTOR`, `AIRFLOW__CORE__DAGS_FOLDER` - defaults in `.env.example`; run airflow from the repo root so the relative `dags` path resolves

```bash
uv run --env-file .env airflow standalone
```

That starts the `api-server`, `scheduler`, `dag-processor`, and `triggerer`, runs database migrations, and creates an admin user. A password is generated and printed on first startup. Open [http://localhost:8080](http://localhost:8080) for the web UI.

Useful commands:

```bash
uv run --env-file .env airflow dags list
uv run --env-file .env airflow dags list-import-errors
uv run --env-file .env airflow dags test breweries_etl
```

`.airflow/` holds the local state (logs, generated config) and is gitignored.

## Docker Compose

For Docker, `docker-compose.yaml` provides the full stack including postgres. Make sure to copy `.env.example` to `.env` and set your variables.

```bash
docker compose up -d
docker compose ps
docker compose logs -f airflow-scheduler
docker compose exec airflow-scheduler airflow dags list
docker compose down    # add -v to also delete the postgres data volume
```

### Extended image

The compose file builds an extended image instead of using the stock one. The `Dockerfile` layers the DAG's dependencies from `requirements.txt`, pinned to the versions in `uv.lock`, on top of the stock airflow image. This ensures imports work in the containers without installing anything at startup. Rebuild after changing dependencies with:

```bash
docker compose build
```

To use the stock image instead, swap the commented `image:`/`build:` lines in `docker-compose.yaml` and set `_PIP_ADDITIONAL_REQUIREMENTS` in `.env` - it pip-installs on every container start, which is slower but avoids image builds.

## Podman

The compose path is Docker-only on purpose. Podman is rootless and daemonless, which is great for security, but it makes orchestrating a stack of interconnected containers like Airflow much harder.

- UID mapping: rootless podman maps container uids to host subuids, so the `airflow-init` container's `chown -R $AIRFLOW_UID:0` hands your bind-mounted directories to a subuid. This causes files to become inaccessible to your own user. Setting `AIRFLOW_UID=0` fixes it, at the cost of container processes running with your full identity.
- HOME: podman sets `HOME` to the image workdir for uids missing from `/etc/passwd`, which broke the airflow import.
- File modes: restrictive file modes (600/700) plus the `chown` run in `airflow-init` locked files away from both sides. Keep mounted files at 644/755.

### A note on DockerOperator

DockerOperator (from `apache-airflow-providers-docker`, or the `@task.docker` decorator) is the modern solution for the Airflow docker stack. It allows running Airflow itself directly and launches each task in its own container. Since this pipeline is pure Python with nothing beyond the venv, I'm not using here. If a task ever needs a heavy or conflicting dependency, that is when I'd reach for it.

## Database

Pipeline tables live in `src/pipeline_btw/db/`: `schema.sql` plus numbered SQL files in `migrations/`. There is no migration runner, so apply them by hand with psql, in filename order. `schema.sql` is idempotent; the migrations are not, so re-running one fails on the existing columns.

Local path:

```bash
psql "$DB_URL" -f src/pipeline_btw/db/schema.sql
psql "$DB_URL" -f src/pipeline_btw/db/migrations/001_add_timestamps.sql
```

Docker path (postgres is only reachable inside the compose network as `postgres:5432`):

```bash
# separate database so pipeline tables don't sit next to airflow's metadata tables
docker exec pipeline-btw_postgres_1 createdb -U airflow breweries

docker exec -i pipeline-btw_postgres_1 psql -v ON_ERROR_STOP=1 -U airflow -d breweries -f - < src/pipeline_btw/db/schema.sql
docker exec -i pipeline-btw_postgres_1 psql -v ON_ERROR_STOP=1 -U airflow -d breweries -f - < src/pipeline_btw/db/migrations/001_add_timestamps.sql
```

### DAG targets

DAG code reads `DB_URL`. Locally that is your postgres (`breweries` database). Under compose, the compose file overrides `DB_URL` so DAG code uses the in-network postgres (`postgresql://airflow:airflow@postgres:5432/breweries`).
