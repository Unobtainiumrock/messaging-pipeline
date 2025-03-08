FROM python:3.10-slim

WORKDIR /app

# Accept environment argument
ARG ENVIRONMENT=development

# Install UV
RUN pip install uv

# Install system dependencies with proper cleanup
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy necessary files for dependency installation
COPY pyproject.toml .
COPY package.json .

# Install Python dependencies using UV (handles both production and dev)
RUN if [ "$ENVIRONMENT" = "production" ]; then \
        uv pip install --system . ; \
    else \
        uv pip install --system -e ".[dev]" && \
        uv pip install --system pytype==2023.10.17 ; \
    fi

# Install node dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Set up pre-commit hooks in development only
RUN if [ "$ENVIRONMENT" = "development" ] ; then \
        pre-commit install || echo "Pre-commit installation skipped" ; \
    fi

# Define environment variable
ENV ENVIRONMENT=$ENVIRONMENT

# Default command
CMD ["python", "src/main.py"]
