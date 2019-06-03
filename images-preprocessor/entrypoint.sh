#!/usr/bin/env bash
echo "Running test for images-preprocessor application..."
pytest
CR_PYTEST=${?}
echo "[DONE] Test for images-preprocessor application are done with code return ${CR_PYTEST}"

if [[ ${CR_PYTEST} -eq 0 ]]
then
    echo "Launching airflow web server and scheduler..."
    airflow initdb
    airflow scheduler &
    airflow webserver
fi