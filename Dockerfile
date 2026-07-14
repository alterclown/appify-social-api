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

# Configure poetry to not create virtual environments inside the container
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application files
COPY . /app/

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]