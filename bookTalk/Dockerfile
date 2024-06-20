FROM python:3.12

RUN apt-get update \
    && apt-get install -y default-mysql-client

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8000

ENV NAME World

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
