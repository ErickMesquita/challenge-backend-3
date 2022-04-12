"""
Autor: Leonardo Giordani
Obtido de: https://www.thedigitalcatonline.com/blog/2020/07/05/flask-project-setup-tdd-docker-postgres-and-more-part-1/
"""

import os
import json
import signal
import subprocess
import time

import click


# Garante que uma variável de ambiente existe e tem um valor
def setenv(variable, default):
	os.environ[variable] = os.getenv(variable, default)


setenv("APPLICATION_CONFIG", default="development")


# Lê a configuração do arquivo JSON
def configure_app(config: str):
	config_json_filename = config + ".json"
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

	if subcommand_list and subcommand_list[0] == "run" and "--host" not in subcommand_list:
		subcommand_list.append("--host")
		subcommand_list.append("::")

	cmdline = ["flask"] + subcommand_list

	try:
		p = subprocess.Popen(cmdline)
		p.wait()
	except KeyboardInterrupt:
		p.send_signal(signal.SIGINT)
		p.wait()


def docker_compose_cmdline(config: str):
	configure_app(config)
	docker_compose_file = os.path.join("docker", f"{config}.yml")

	if not os.path.isfile(docker_compose_file):
		docker_compose_file2 = os.path.join("docker", f"{config}.yaml")
		if not os.path.isfile(docker_compose_file2):
			raise ValueError(f"The file {docker_compose_file} does not exist")

	return [
		"docker-compose",
		"-p",
		config,
		"-f",
		docker_compose_file,
	]


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("subcommand", nargs=-1, type=click.Path())
def compose(subcommand):
	cmdline = docker_compose_cmdline(os.getenv("APPLICATION_CONFIG")) + list(subcommand)

	try:
		p = subprocess.Popen(cmdline)
		p.wait()
	except KeyboardInterrupt:
		p.send_signal(signal.SIGINT)
		p.wait()


@cli.command()
@click.argument("filenames", nargs=-1)
def test(filenames):
	os.environ["APPLICATION_CONFIG"] = "testing"
	configure_app(os.getenv("APPLICATION_CONFIG"))

	cmdline = docker_compose_cmdline(os.getenv("APPLICATION_CONFIG")) + ["up", "-d"]
	subprocess.call(cmdline)

	cmdline = docker_compose_cmdline(os.getenv("APPLICATION_CONFIG")) + ["logs", "db"]
	logs = subprocess.check_output(cmdline)
	while "ready to accept connections" not in logs.decode("utf-8"):
		time.sleep(0.1)
		logs = subprocess.check_output(cmdline)

	cmdline = ["pytest", "-svv", "--cov=application", "--cov-report=term-missing"]
	cmdline.extend(filenames)
	subprocess.call(cmdline)

	cmdline = docker_compose_cmdline(os.getenv("APPLICATION_CONFIG")) + ["down"]
	subprocess.call(cmdline)


@cli.command(context_settings={"ignore_unknown_options": True})
def env():
	print("Environment variables in use:")
	for key, value in os.environ.items():
		print(f"{key} -> {value}")


if __name__ == "__main__":
	cli()
