FROM python:3.7-slim
RUN mkdir /app
WORKDIR /app
COPY .. ./
WORKDIR /backend
RUN pip install -r requirements.txt --no-cache-dir
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]