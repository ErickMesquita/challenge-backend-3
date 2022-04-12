"""
Autor: Leonardo Giordani
Obtido de: https://www.thedigitalcatonline.com/blog/2020/07/05/flask-project-setup-tdd-docker-postgres-and-more-part-1/
"""

import os
import json
import signal
import subprocess

import click

docker_compose_file = "docker/development.yml"
docker_compose_cmdline = ["docker-compose", "-f", docker_compose_file]


# Garante que uma variável de ambiente existe e tem um valor
def setenv(variable, default):
	os.environ[variable] = os.getenv(variable, default)


setenv("APPLICATION_CONFIG", default="development")

# Lê a configuração do arquivo JSON
config_json_filename = os.getenv("APPLICATION_CONFIG") + ".json"
with open(os.path.join("config", config_json_filename)) as f:
	config = json.load(f)

# Convert the config into a usable Python dictionary
# config = dict((i["name"], i["value"]) for i in config)

for key, value in config.items():
	setenv(key, value)


@click.group()
def cli():
	pass


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("subcommand", nargs=-1, type=click.Path())
def flask(subcommand):
	subcommand_list = list(subcommand)

	if "--host" not in subcommand_list:
		subcommand_list.append("--host")
		subcommand_list.append("::1")

	cmdline = ["flask"] + subcommand_list

	try:
		p = subprocess.Popen(cmdline)
		p.wait()
	except KeyboardInterrupt:
		p.send_signal(signal.SIGINT)
		p.wait()


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("subcommand", nargs=-1, type=click.Path())
def compose(subcommand):
	cmdline = docker_compose_cmdline + list(subcommand)

	try:
		p = subprocess.Popen(cmdline)
		p.wait()
	except KeyboardInterrupt:
		p.send_signal(signal.SIGINT)
		p.wait()


@cli.command(context_settings={"ignore_unknown_options": True})
def env():
	print("Environment variables in use:")
	for key, value in os.environ.items():
		print(f"{key} -> {value}")


if __name__ == "__main__":
	cli()