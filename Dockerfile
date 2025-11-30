# Use a full Python base image
FROM python:3.11-bookworm

# Set working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy pyproject.toml and any potential lock file first for better caching
COPY pyproject.toml .
# If you use a uv.lock file, uncomment the following line:
COPY uv.lock .

# Install dependencies using 'uv'
ENV UV_HTTP_TIMEOUT=300
RUN uv pip install --no-cache-dir --system .

# Copy the entire project code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port (Cloud Run defaults to 8080)
EXPOSE 8080

# Command to run your application
# CMD ["python", "-m", "uvicorn", "personal_agent.serve:app", "--host", "0.0.0.0", "--port", "8080"]
CMD ["adk", "web", "--port", "8080"]