FROM mcr.microsoft.com/playwright/python:v1.58.0-noble
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
COPY services/api/pyproject.toml ./
RUN pip install -U pip && pip install -e .
COPY services/api/app ./app
ENV OUTPUT_DIR=/tmp/demomotion-generated
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
