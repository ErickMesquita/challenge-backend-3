import os

from application.wsgi import app
from flask import redirect, render_template, url_for, request, flash
from werkzeug.utils import secure_filename


@app.get("/teste")
def teste():
	return "<h1>Teste</h1><h4>Funciona!!!</h4>"


@app.get("/transacoes")
def transacoes_get():
	return render_template("importar_transacoes.html", titulo="Importar Transações")


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.post("/transacoes")
def transacoes_post():
	if 'file' not in request.files:
		flash('Nenhum arquivo enviado')
		return redirect(request.url)

	file = request.files["file"]

	if file.filename == "":
		flash('Nenhum arquivo selecionado')
		return redirect(request.url)

	if not allowed_file(file.filename):
		flash('Extensão inválida')
		return redirect(request.url)

	filename = secure_filename(file.filename)
	file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	file.save(file_path)
	print(f"Arquivo chegando - filesize = {os.path.getsize(file_path)} Bytes")
	flash(f"Arquivo chegando - filesize = {os.path.getsize(file_path)} Bytes")
	return redirect(url_for("transacoes_get"))
