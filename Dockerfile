FROM python:3.11-slim-bookworm

# Install system dependencies required for audio processing
RUN apt-get update && apt-get install -y \
    libsndfile1 git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock* /app/
COPY install.py /app/

# Install Python dependencies
RUN uv sync --locked

# Pre-download the T-one model during build
RUN uv run python install.py

# Copy application code
COPY . /app

# Expose the default port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "python", "main.py"]
