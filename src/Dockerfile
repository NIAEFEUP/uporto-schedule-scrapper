FROM python:3.9 as base

RUN mkdir -p /scrapper

COPY . /scrapper/

WORKDIR /scrapper

RUN pip install -r requirements.txt

FROM base as prod

RUN apt update && apt install -y postgresql-client

CMD tail -f /dev/null
