
# images-preprocessor


Images preprocessor engine


Description
===========

Objectifs:
- Recuperer les images accessibles par les urls contenues dans le fichier urls.txt.
- Developper une tache qui calculera la MD5 de l'image
- Developper une tache qui transformera l'image en niveau de gris avec le calcul suivant: (R + G + B) / 3
- Developper une tache qui recuperera les outputs des deux precedents workers. Il devra egalement inserer dans une base
de donnees MongoDB, les informations (md5, l'image en niveau de gris, la hauteur et la largeur de l'image, la date d'insertion).
- Developper une api en Flask pour visualiser les images stockees dans MongoDB via l'url http://localhost:5000/image/<MD5>
- Developper une api en Flask de monitoring via l'url http://localhost:5000/monitoring. Cette api devra retourner un
histogramme decrivant le nombre d'images traitees avec succes ou erreur par interval d'une minute. (Prevoir une collection dans MongoDB pour recuperer ces informations)


Requirements
============
This project is fully-based on docker container.
Docker has to be installed on your host machine.
See: https://docs.docker.com/install/

Please also check your internet connection, needed for image downloading.

Architecture
============
This project is based on 3 docker container:
- MongoDB database container
- Flask web app container
- Images preprocessor container including Airflow


Installation
============
### Build and run all container
> Go to the project home directory and run:

    docker-compose up
    
This command will create 3 containers:

![Alt text](images/docker_view.png)

Execution
=========
Airflow provides a web interface to run your DAG pipeline.
A Dag is a sequence of task, and each task is an operator running on airflow host.

1. Go to the interface on: http://localhost:8080/admin
2. Be sure the DAG "IMAGES-PREPROCESSOR" is visible and set to "ON"
3. Trigger the DAG clicking on the "play" button on the right side

![Alt text](images/home_view.png)

Once the DAG is finished, you can visualize results on the web UI: http://localhost:5000

On this page you have a:
- "Monitoring page" Menu which shows you how much images have been transformed by seconds
- The "MD5 list" menu linked to the list of image transformed as gray

![Alt text](images/menu_view.png)


Then if you scroll down you will see a sticker showing total error and success transformation. You can click
on the histogram to display the image.

Scrolling down more will show you the list of image transformed with their md5. You can click on it 
to diplay the image:

![Alt text](images/md5_view.png)

Parameters
==========
You can overwrite some application options directly on airflow Web UI:
1. Go to "Admin" menu and then "Variables"
2. Next you can overwrite the environment and log level variables

![Alt text](images/variables_view.png)

- The "ENV" variable can be modified to "prod" to load other property file. In this case it won't change anything because all properties are the same on both files.
- The "LOG_LEVEL" variable can be modified to "INFO" or "DEBUG" to display more logs or not.

Monitoring
==========
To monitor your task execution, airflow provide log application of each task.
1. Click on "Recent tasks" bubble of your choice and click on the task you want to monitor

![Alt text](images/tasks_view.png)


3. Click on "Log" to get all application logs of your task

![Alt text](images/log_view.png)

Note
====

This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
