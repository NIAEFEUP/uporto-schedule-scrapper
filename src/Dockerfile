FROM python:3.9 as base

RUN mkdir -p /scrapper

ADD requirements.txt /scrapper/

WORKDIR /scrapper

RUN pip install -r requirements.txt

FROM base as prod

CMD tail -f /dev/null
