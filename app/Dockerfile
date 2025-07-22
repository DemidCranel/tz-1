FROM python:3.12
WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements-linux.txt
RUN apt update
RUN apt install nano
