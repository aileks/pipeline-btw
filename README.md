# Pipeline BTW

Pipeline practice on the [Breweries API](https://openbrewerydb.org) using ETL and Pydantic validation.

## Python environment

```bash
uv sync
source .venv/bin/activate

# to exit the venv
deactivate
```

## Airflow

`docker-compose.yaml` defines the full Airflow 3.3 stack: postgres, redis, api-server, scheduler, dag-processor, celery worker, and triggerer. The first startup runs database migrations, creates the config file, and adds an admin user.

### Setup

```bash
cp .env.example .env
```

Edit `.env`:

> [!NOTE]  
> When using rootless Podman, you will run into permissions issues due to containers getting assigned a subuid.
> Set `AIRFLOW_UID=0` so the container acts as your host user.

- Set `AIRFLOW_UID` to your user id so the bind-mounted `dags/`, `logs/`, `config/`, and `plugins/` directories stay owned by you.
- Every other variable in `.env` is passed into the Airflow containers, e.g. `DB_URL`.
- Optional: set `FERNET_KEY` to encrypt saved connections. Generate one with:

  ```bash
  podman run --rm docker.io/apache/airflow:3.3.1 python -c \
    "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

The web UI is at [http://localhost:8080](http://localhost:8080), log in with `airflow` as both username and password. Override the credentials with `_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD` in `.env` before the first startup.

### Docker

```bash
docker compose up -d
docker compose ps
docker compose logs -f airflow-scheduler
docker compose exec airflow-scheduler airflow dags list
docker compose down    # add -v to also delete the postgres data volume
```

### Podman

Image names in `docker-compose.yaml` are fully qualified (`docker.io/...`) so rootless podman can resolve them.

```bash
podman-compose up -d
podman-compose ps
podman-compose logs -f airflow-scheduler
podman-compose exec airflow-scheduler airflow dags list
podman-compose down    # add -v to also delete the postgres data volume
```

### DAGs

Drop DAG files into `dags/`; the dag-processor picks them up without a restart. New DAGs start paused, so unpause in the UI or run `airflow dags unpause <dag_id>`. Airflow's example DAGs ship enabled; set `AIRFLOW__CORE__LOAD_EXAMPLES` to `"false"` in `docker-compose.yaml` to turn them off.

Optional services live behind compose profiles, e.g. Flower (celery monitor) on port 5555:

```bash
docker compose --profile flower up -d
podman-compose --profile flower up -d
```

## Database

Pipeline tables live in `src/pipeline_btw/db/`: `schema.sql` plus numbered SQL files in `migrations/`. There is no migration runner, so apply them by hand. Both a local postgres and the stack's postgres are supported targets; they are reached differently.

### Local postgres

When `DB_URL` in `.env` points at your own postgres, apply the files with psql from the host as usual:

```bash
psql "$DB_URL" -f src/pipeline_btw/db/schema.sql
psql "$DB_URL" -f src/pipeline_btw/db/migrations/001_add_timestamps.sql
```

### Airflow stack postgres

Airflow's postgres database is only reachable inside the compose network as `postgres:5432`. Pipe the files through `psql` in the container:

```bash
# separate database so pipeline tables don't sit next to airflow's metadata tables
docker exec pipeline-btw_postgres_1 createdb -U airflow breweries

docker exec -i pipeline-btw_postgres_1 psql -v ON_ERROR_STOP=1 -U airflow -d breweries -f - < src/pipeline_btw/db/schema.sql
docker exec -i pipeline-btw_postgres_1 psql -v ON_ERROR_STOP=1 -U airflow -d breweries -f - < src/pipeline_btw/db/migrations/001_add_timestamps.sql
```

To apply them from the host venv instead, publish a port on the `postgres` service (e.g. `55432:5432`, since 5432 is often taken by a local postgres) and point `DB_URL` at `postgresql://airflow:airflow@127.0.0.1:55432/breweries`.

In both cases, apply `migrations/` in filename order.

### DAG targets

DAG code runs inside the containers, where `DB_URL` comes from `docker-compose.yaml` and defaults to the stack postgres (`postgresql://airflow:airflow@postgres:5432/breweries`). To target your local postgres instead, set `PIPELINE_DB_URL` in `.env`, e.g. `postgresql://postgres@host.docker.internal:5432/postgres` (`host.containers.internal` for podman).

### Python requirements in the containers

The airflow image only ships its own dependencies, so anything your DAG imports must be installed into the containers with `_PIP_ADDITIONAL_REQUIREMENTS` in `.env`:

```
_PIP_ADDITIONAL_REQUIREMENTS="httpx psycopg psycopg-binary pydantic python-dotenv"
```

That covers everything `pipeline_btw` imports (httpx, psycopg, pydantic, dotenv). It reinstalls on every container start - fine for practice; switch to an extended image when it isn't.
