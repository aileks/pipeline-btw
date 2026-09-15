FROM docker.io/apache/airflow:3.3.1

COPY --chown=airflow requirements.txt /tmp/requirements.txt

# the image's python is a venv at /home/airflow/.local; plain install lands where airflow itself lives
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
