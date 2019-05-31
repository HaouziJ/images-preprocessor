FROM python:3.6

WORKDIR /app

COPY . /app

RUN mkdir /app/data

RUN mv /app/images-preprocessor/data/urls.txt /app/data

RUN mkdir /app/logs

RUN python -m pip install --upgrade pip

RUN python -m pip install -r requirements.txt

RUN python -m pip install -e images-preprocessor

ENTRYPOINT [ "/bin/bash" ]