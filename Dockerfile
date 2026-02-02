# Dockerfile

# 1. Base Image
FROM python:3.12-slim

# 2. Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Create and set working directory
WORKDIR /app

# 4. Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy project code
COPY . .

# 6. Expose port
EXPOSE 8000

# 7. Run the application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
