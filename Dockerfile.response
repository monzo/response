FROM python:3.7

RUN apt-get update && apt-get install -y \
    netcat

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]