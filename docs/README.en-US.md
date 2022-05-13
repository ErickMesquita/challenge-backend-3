<h1 align="center">
	<p align="center">Challenge Back-End 3ª Edition</p>
	<a href="https://www.alura.com.br/challenges/back-end-3"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/logo/challenges-logo-2-darkbg.svg" alt="Alura Challenges"></a>
</h1>
<div align="center" id="badges">
	<a href="https://docs.python.org/3.8/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/badges/Python-3.8-brightgreen.svg" alt="Python 3.8"></a>
	<a href="https://docs.pytest.org/en/7.1.x/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/badges/tested%20with-pytest-blue.svg" alt="Teste with pytest"></a>
	<a href="https://docs.docker.com/compose/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/badges/Deploy%20with-Docker%20Compose-blue.svg" alt="Deploy with Docker Compose"></a>
	<img src="https://img.shields.io/badge/Status-Approved-brightgreen" alt="Status: Approved">
</div>

*Read this in other languages: [Brazilian Portuguese](https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/README.pt-BR.md)*

<h3>
	<p align="center">Web application to analyse and investigate financial transactions</p>
</h3>

The goal is to learn web development in practice, with a complete web application that supports file upload, access control and data analysis. This project is split in Docker containers, to facilitate deployment.

Users are able to upload spreadsheets with financial transactions data to be analysed.

This project was submited to Alura Teachers' Board and approved in May 10 2022

## <img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/logo/challenges-logo.svg" alt="Alura Challenges" width="24px" class="emoji"> Requirements

 - [Python 3.8+](https://docs.python.org/3.8/)
 - [Docker](https://www.docker.com/)
 - [Docker Compose](https://docs.docker.com/compose/)

## :zap: Features

 - :closed_lock_with_key: `Access Control`: Users CRUD with Login, Logout, Registration and Deletion of accounts
 - :page_with_curl: `File upload`: CSV and XML files with financial transactions data to be analysed
 - :floppy_disk: `Database Storage`: SQL Database Persistence
 - :microscope: `Transactions Analysis`: Investigation for fraudulent or suspicious transactions

### :closed_lock_with_key: Login

Only logged in users can access the system, upload files and generate analyses.

<p align="center"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/gif/Login-admin.gif" alt="GIF showing user login" width=550></p>


### :closed_lock_with_key: Signup

New users can only be registered by existing users. One of the project requirements is that a 6-digit numeric password is generated. The password is stored encrypted in the database with SHA512 and [bcrypt](https://flask-bcrypt.readthedocs.io/en/latest/)

<p align="center"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/gif/Signup.gif" alt="GIF showing new user account creation" width=550></p>

## :hammer_and_wrench: Open and run the project

Go to http://challenge-backend3.freedynamicdns.net:5000/login and see the service running!

or

1. Clone this repository
2. At the project's root folder, use the command `python manage.py compose up --build` to build the images and run the project

Optionally, you can add the environment variable `APPLICATION_CONFIG` to select the operating mode:
```
APPLICATION_CONFIG=testing python manage.py compose up
```

## <img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/logo/challenges-logo.svg" width="24px" class="emoji"> Modes of Operation

 - `testing`: Starts a database container without persistence. The flask application must run directly on the host, without containerization. This mode is especially useful for running pytest tests
 - `development`: Both the database and the application run in containers. Database data is stored on a volume on the host. The application code is brought in a volume from the host, so that with every change in the code, the server is automatically updated with the latest version.
 - `production`: Usage mode with additional security, which disables the Flask debugger. Gunicorn server is used for better production performance.

## :hammer_and_wrench: Configuration

All project settings are together, to facilitate their change and deployment.

The environment variables used in the application and in the Docker containers are saved in JSON format, in the `config` folder.

Flask specific settings are in the `application/config.py` file

## :man_technologist: Technologies used

- [Docker](https://www.docker.com/)
 - [Flask 2.1](https://flask.palletsprojects.com/en/2.1.x/)
 - [Flask-Bcrypt 1.0](https://flask-bcrypt.readthedocs.io/en/latest/)
 - [Flask-Login 0.6](https://flask-login.readthedocs.io/en/latest/)
 - [Flask-Migrate 3.1](https://flask-migrate.readthedocs.io/en/latest/index.html)
 - [Flask-SQLAlchemy 2.5](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
 - [Flask-WTForms 1.0](https://flask-wtf.readthedocs.io/en/1.0.x/)
 - [Pandas 1.4](https://pandas.pydata.org/)
 - [PostgreSQL 14.2](https://www.postgresql.org/)
 - [PyCharm](https://www.jetbrains.com/pycharm/0)

## :man_teacher:: Learning

This was my first project developing a complete Flask application from start to finish. I spent a lot more time reading documentation for Flask packages and plugins than actually writing code.

I learned that it is much easier to use a plug-in than trying to solve a big problem "by hand". There are many Flask plugins available to solve most problems that may arise.

Halfway through the project, I was forced to change the database from `MySQL` to `PostgreSQL` because the former is not compatible with the production computer architecture. I learned to always check in advance the compatibility of docker images and Python packages with all machines involved.

I learned to use `SQLAlchemy` to model and manipulate the database, including relationships and constraints. I also had to do several migrations during the project, and for that I had to learn how to use the `Alembic` package.

<p align="center"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/Badge_Alura_Challenge_back_First_v3.png" width=500></p>
