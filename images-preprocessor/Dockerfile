FROM python:3.6

WORKDIR /app

COPY . /app

ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW_HOME=/root/airflow

EXPOSE 8080

RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN mkdir /app/logs
RUN mkdir -p /app/data/test
RUN mv images-preprocessor/data/urls.txt /app/data
RUN python -m pip install --upgrade pip
RUN python -m pip install apache-airflow
RUN mkdir -p /root/airflow/dags
RUN python -m pip install -r images-preprocessor/requirements.txt
RUN mv /app/airflow/engine_dag.py /root/airflow/dags
RUN mv images-preprocessor/entrypoint.sh /
RUN python -m pip install -e images-preprocessor/

ENTRYPOINT [ "/entrypoint.sh" ]