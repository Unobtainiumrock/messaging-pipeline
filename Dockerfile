FROM nikolaik/python-nodejs:python3.11-nodejs18

WORKDIR /app

# Accept environment argument
ARG ENVIRONMENT=development

# Install UV
RUN pip install uv

# Configure Git to trust the mounted directory
RUN git config --global --add safe.directory /app

# Copy necessary files for dependency installation
COPY pyproject.toml .
COPY package.json .

# Install dependencies using UV with --system flag
RUN uv pip install --system -e ".[dev]"

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
ENV PYTHONPATH=/app

# Default command
CMD ["python", "src/main.py"]
