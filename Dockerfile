FROM python:3.10-slim

WORKDIR /app

# Accept environment argument
ARG ENVIRONMENT=development

# Install system dependencies with proper cleanup
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dev dependencies if in development mode
RUN if [ "$ENVIRONMENT" = "development" ] ; then \
    pip install --no-cache-dir pytest pytest-cov black flake8 mypy ; \
    fi

# Install node dependencies
COPY package.json .
RUN npm install

# Copy project files
COPY . .

# Set up pre-commit hooks in development only
RUN if [ "$ENVIRONMENT" = "development" ] ; then pip install pre-commit ; fi

# Define environment variable
ENV ENVIRONMENT=$ENVIRONMENT

# Default command
CMD ["python", "src/main.py"] 