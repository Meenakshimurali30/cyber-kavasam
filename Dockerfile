# ========================================================
# Dockerfile for Cyber Kavasam (சைபர் கவசம்)
# Production-grade, lightweight, secure, non-root user
# ========================================================

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    KAVASAM_MAX_LENGTH=2000 \
    KAVASAM_RATE_LIMIT=30

WORKDIR /app

# Install curl for HEALTHCHECK and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies first for layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and data
COPY app/ /app/app/
COPY data/ /app/data/

# Create models and data directories
RUN mkdir -p /app/models /app/data

# Build dataset and train ML model at build time
RUN python data/build_dataset.py && python -m app.train

# Create non-root user for security
RUN useradd -m -u 10001 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose HTTP port
EXPOSE 5000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production WSGI server
CMD ["waitress-serve", "--listen=0.0.0.0:5000", "--call", "app.server:create_app"]
