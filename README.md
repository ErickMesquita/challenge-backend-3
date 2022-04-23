<h1 align="center">
	<p align="center">Desafio Back-End</p>
	<a href="https://www.alura.com.br/challenges/back-end-3"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/challenges-logo-2.svg" alt="Alura Challenges"></a>
</h1>
<div align="center" id="badges">
	<a href="https://docs.python.org/3.8/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/Python-3.8-brightgreen.svg" alt="Python 3.8"></a>
	<a href="https://docs.pytest.org/en/7.1.x/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/tested%20with-pytest-blue.svg" alt="Teste with pytest"></a>
	<a href="https://docs.docker.com/compose/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/Deploy%20with-Docker%20Compose-blue.svg" alt="Deploy with Docker Compose"></a>
	<img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow" alt="Status: Em desenvolvimento">
</div>
<h3>
	<p align="center">Aplicação web para analisar e investigar transações financeiras</p>
</h3>

Aprender a desenvolver uma aplicação web tradicional completa com upload de arquivos, controle de acesso e análise de dados. O projeto é dividido em containers Docker, para facilitar o deploy.

Os usuários podem fazer o upload de planilhas contendo dados de transações financeiras e elas serão analizadas pelo sistema.

## :zap: Funcionalidades

 - :page_with_curl: `Upload de arquivos`: Planilhas com dados sobre transações financeiras a serem analizadas
 - :floppy_disk: `Armazenamento em banco de dados`: Persistência em Banco de Dados SQL
 - :closed_lock_with_key: `Controle de Acesso`: CRUD de usuários com Login, Logout, Cadastro e Exclusão de contas de usuário
 - :microscope: `Análise de Transações`: Investigação em busca de fraudes ou transações suspeitas

## Requisitos

 - [Python 3.8+](https://docs.python.org/3.8/)
 - [Docker](https://www.docker.com/)
 - [Docker Compose](https://docs.docker.com/compose/)

## :hammer_and_wrench: Abrir e rodar o projeto

1. Clone este repositório
2. A variável de ambiente `APPLICATION_CONFIG` indica se o ambiente é de `development`(padrão), `testing` ou `production`
3. Na pasta raiz do projeto, use o comando `python manage.py compose up --build` para buildar as imagens e rodar o projeto

## :man_technologist: Tecnologias utilizadas

 - [Flask 2.1](https://flask.palletsprojects.com/en/2.1.x/)
 - [PostgreSQL 14.2](https://www.postgresql.org/)
 - [Flask-SQLAlchemy 2.5](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
 - [Flask-Bcrypt 1.0](https://flask-bcrypt.readthedocs.io/en/latest/)
 - [Flask-Migrate 3.1](https://flask-migrate.readthedocs.io/en/latest/index.html)
 - [Flask-Login 0.6](https://flask-login.readthedocs.io/en/latest/)
 - [Flask-WTForms 1.0](https://flask-wtf.readthedocs.io/en/1.0.x/)
 - [Pandas 1.4](https://pandas.pydata.org/)
 - [PyCharm](https://www.jetbrains.com/pycharm/0)
