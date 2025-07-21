# build stage
FROM python:3.11 AS first_s
WORKDIR /app

# install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# runtime stage
FROM python:3.11-slim

COPY --from=first_s /usr/local /usr/local
COPY src/ ./src

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

EXPOSE 3306
CMD ["python", "app.py"]
