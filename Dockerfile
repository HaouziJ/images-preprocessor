FROM python:3.6

WORKDIR /app

COPY . /app

COPY ./images-preprocessor/data/urls.txt /app/data

RUN mkdir -p /app/logs

RUN mkdir -p /app/data

RUN python -m pip install -r requirements.txt

RUN python -m pip install -e images-preprocessor

ENTRYPOINT [ "/bin/bash" ]