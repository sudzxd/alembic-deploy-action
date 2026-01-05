FROM python:3.11-slim

LABEL maintainer="sudzxd"
LABEL description="GitHub Action for safe Alembic database migrations"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    alembic>=1.13.0 \
    psycopg2-binary \
    pymysql \
    sqlalchemy>=2.0.0

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /github/workspace

ENTRYPOINT ["/entrypoint.sh"]
