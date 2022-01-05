FROM pylakey/poetry_base:latest

WORKDIR /app
ENV PYTHONPATH=/app

# Install deps
RUN apt-get update -y && apt-get install --no-install-recommends -y \
    git \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/
RUN poetry install
COPY ./app /app/app

COPY start.sh /app
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]