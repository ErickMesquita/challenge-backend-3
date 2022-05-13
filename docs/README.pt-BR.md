<h1 align="center">
	<p align="center">Desafio Back-End 3ª Edição</p>
	<a href="https://www.alura.com.br/challenges/back-end-3"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/logo/challenges-logo-2-darkbg.svg" alt="Alura Challenges"></a>
</h1>
<div align="center" id="badges">
	<a href="https://docs.python.org/3.8/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/badges/Python-3.8-brightgreen.svg" alt="Python 3.8"></a>
	<a href="https://docs.pytest.org/en/7.1.x/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/badges/tested%20with-pytest-blue.svg" alt="Teste with pytest"></a>
	<a href="https://docs.docker.com/compose/"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/badges/Deploy%20with-Docker%20Compose-blue.svg" alt="Deploy with Docker Compose"></a>
	<img src="https://img.shields.io/badge/Status-Aprovado-brightgreen" alt="Status: Aprovado">
</div>

*Read this in other languages: [English](https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/README.en-US.md)*

<h3>
	<p align="center">Aplicação web para analisar e investigar transações financeiras</p>
</h3>

O objetivo é aprender desenvolvimento web na prática, com uma aplicação web completa com upload de arquivos, controle de acesso e análise de dados. O projeto é dividido em containers Docker, para facilitar o deploy.

Os usuários podem fazer o upload de planilhas contendo dados de transações financeiras e elas serão analizadas pelo sistema.

Este projeto foi apresentado para a banca de professores da Alura e foi aprovado em 10/05/2022

## :zap: Funcionalidades

 - :closed_lock_with_key: `Controle de Acesso`: CRUD de usuários com Login, Logout, Cadastro e Exclusão de contas de usuário
 - :page_with_curl: `Upload de arquivos`: Arquivos CSV e XML com dados sobre transações financeiras a serem analizadas
 - :floppy_disk: `Armazenamento em banco de dados`: Persistência em Banco de Dados SQL
 - :microscope: `Análise de Transações`: Investigação em busca de fraudes ou transações suspeitas

### :closed_lock_with_key: Login

<img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/gif/Login-admin.gif" alt="GIF showing user login" width=550>


### :closed_lock_with_key: Signup

<img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/gif/Signup.gif" alt="GIF showing new user account creation" width=550>


## <img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/logo/challenges-logo.svg" width="24px" class="emoji"> Requisitos

 - [Python 3.8+](https://docs.python.org/3.8/)
 - [Docker](https://www.docker.com/)
 - [Docker Compose](https://docs.docker.com/compose/)

## :hammer_and_wrench: Abrir e rodar o projeto

Acesse o site http://challenge-backend3.freedynamicdns.net:5000/login e veja o serviço rodando!

ou

1. Clone este repositório
2. Na pasta raiz do projeto, use o comando `python manage.py compose up --build` para buildar as imagens e rodar o projeto

Opcionalmente, pode-se adicionar a variável de ambiente `APPLICATION_CONFIG` para selecionar o modo de operação:
```
APPLICATION_CONFIG=testing python manage.py compose up
```

## <img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/logo/challenges-logo.svg" width="24px" class="emoji"> Modos de Operação

 - `testing`: Inicia um contêiner com o banco de dados sem persistência. A aplicação deve ser executada diretamente no host, sem conteineização. Este modo é especialmente útil para executar os testes PyTest 
 - `development`: Tanto o banco de dados quanto a aplicação rodam em contêineres. Os dados do banco de dados são armazenados em um volume no host. Os códigos da aplicação são trazidos de volume no host, para que a cada mudança no código, o servidor seja automaticamente reiniciado com a versão mais recente
 - `production`: Servidor Gunicorn com segurança adicional. Desativa o debugger do Flask 

## :hammer_and_wrench: Configuração

Todas as configurações do projeto ficam juntas, para facilitar a sua alteração e o deploy.

As variáveis de ambiente utilizadas na aplicação e nos contêineres Docker estão salvas em formato JSON, na pasta `config`.

As configurações específicas do Flask estão no arquivo `application/config.py`

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

## :man_teacher:: Aprendizados

Este foi meu primeiro projeto desenvolvendo uma aplicação Flask completa, do começo ao fim. Passei muito mais tempo lendo documentação de pacotes e plug-ins do Flask do que efetivamente escrevendo código.

Aprendi que é muito mais fácil utilizar um plug-in do que tentar resolver um grande problema "na mão". Existem muitos plug-ins Flask disponíveis para resolver a maior parte dos problemas que podem surgir.

No meio do projeto, fui forçado a alterar o banco de dados de `MySQL` para `PostgreSQL` porque o primeiro não é compatível com a arquitetura do computador da produção. Aprendi a sempre verificar com antecedência a compatibilidade das imagens docker e dos pacotes Python com todas as máquinas envolvidas.

Aprendi a utilizar `SQLAlchemy` para modelar e manipular o banco de dados, incluindo relações e restrições. Também precisei fazer várias migrações durante o projeto, e para isso tive que aprender a utilizar o pacote `Alembic`

<p align="center"><img src="https://github.com/ErickMesquita/challenge-backend-3/blob/master/docs/img/Badge_Alura_Challenge_back_First_v3.png" width=500></p>
