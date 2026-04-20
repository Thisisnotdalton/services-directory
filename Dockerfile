FROM python:3.12-slim-bullseye
ENV PORT=8000

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --locked --no-cache

# Run the application.
CMD ["sh", "-c", "uv run fastapi run --host 0.0.0.0 --port ${PORT:-8000}"]