FROM python:3.14-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_KEY="non-secret-key-for-building-purposes"

RUN python3 manage.py collectstatic --noinput

EXPOSE 8000
CMD ["sh","./runserver"]
