import os
from flask import redirect, render_template, url_for, request, flash, Flask
from werkzeug.utils import secure_filename


def configure_routes(app: Flask):
	@app.get("/teste")
	def _teste():
		return "<h1>Teste</h1><h4>Funciona!!!</h4>"


	@app.get("/forms/transaction")
	def transacoes_get_form():
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
