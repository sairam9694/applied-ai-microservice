FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .
COPY ./wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

COPY ./app /code/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
