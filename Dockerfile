FROM python:3.9
LABEL author="Grupo 1 <atsantiagogarcia@gmail.com>"

# RUN apt-get update && apt-get upgrade

COPY ./ .
COPY ./src .
ENV GOOGLE_APPLICATION_CREDENTIALS ./alumnos-sandbox-50f796a33b0b.json


RUN pip3 install -r requirements.txt

CMD python3 scraper.py
