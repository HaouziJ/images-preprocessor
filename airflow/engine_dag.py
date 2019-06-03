from airflow.models import Variable
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime
import os

env = Variable.get("ENV", default_var=os.environ.get('ENV'))
log_level = Variable.get("LOG_LEVEL", default_var="DEBUG")

args = {
    'owner': 'Airflow'
}

dag = DAG(
    "IMAGES-PREPROCESSOR",
    start_date=datetime(year=2019, month=6, day=1, hour=6, minute=0, second=0),
    schedule_interval='0 6 * * *',
    catchup=False,
    max_active_runs=1,
    default_args=args
)

INIT_DIRECTORY_STRUCTURE = BashOperator(
    task_id='INIT_DIRECTORY_STRUCTURE',
    bash_command="init_directory_structure --env {}".format(env),
    dag=dag
)

COLLECT_INSERT_IMAGES = BashOperator(
    task_id='COLLECT_INSERT_IMAGES',
    bash_command="collect_insert_images --env {} --loglevel {}".format(env, log_level),
    dag=dag
)

COMPUTE_INSERT_MD5_AND_GRAY = BashOperator(
    task_id='INSERT_COMPUTE_MD5_AND_GRAY',
    bash_command="compute_insert_md5_and_gray --env {} --loglevel {}".format(env, log_level),
    dag=dag
)

INIT_DIRECTORY_STRUCTURE >> COLLECT_INSERT_IMAGES >> COMPUTE_INSERT_MD5_AND_GRAY
