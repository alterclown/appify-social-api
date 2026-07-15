FROM python:3.12-slim-bookworm

# Force apt to ignore release file expiration checks entirely
RUN apt-get update -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false || true

# Install dependencies using the same bypass flags
RUN apt-get install -y -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false \
    netcat-openbsd postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency configuration files
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry for containers and retry transient package-download failures.
RUN poetry config virtualenvs.create false && \
    poetry config requests.max-retries 5 && \
    attempts=0; \
    until poetry install --no-root --no-interaction --no-ansi; do \
        attempts=$((attempts + 1)); \
        if [ "$attempts" -ge 3 ]; then exit 1; fi; \
        echo "Dependency installation failed; retrying ($attempts/3)..."; \
        sleep 5; \
    done

# Copy the rest of the application files
COPY . /app/

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
