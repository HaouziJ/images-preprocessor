FROM python:3.6

WORKDIR /app

COPY . /app

ENV FLASK_APP=/app/flask_app

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["flask_app.py"]