FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /code
RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8080

