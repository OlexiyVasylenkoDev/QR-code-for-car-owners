FROM python:3.10

RUN apt update
RUN python --version

RUN mkdir /qr-code

WORKDIR /qr-code

COPY /src ./src
COPY /requirements.txt ./requirements.txt
COPY /db.json ./db.json

RUN python -m pip install --upgrade pip && pip install -r ./requirements.txt

CMD ["python", "src/manage.py", "runserver", "${WSGI_PORT}"]
