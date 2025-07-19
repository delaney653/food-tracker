#build stage
FROM python:3.11 AS first_s
WORKDIR /app

#install dependencies 
COPY requirements.txt ./
RUN pip install --prefix=/src -r requirements.txt

#runtime stage
FROM python:3.11-slim

COPY --from=first_s /src /usr/local
COPY src/ ./src
EXPOSE 3306

CMD ["python", "app.py"]