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

- Set `AIRFLOW_UID` to your user id so the bind-mounted `dags/`, `logs/`, `config/`, and `plugins/` directories stay owned by you. With Podman, this should match the container's UID (usually 50000).
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
