import os
from flask import redirect, render_template, url_for, request, flash, Flask
from werkzeug.utils import secure_filename
from application.controller.transaction_analysis import clean_uploaded_transactions_csv



def configure_routes(app: Flask):
	@app.get("/teste")
	def _teste():
		return "<h1>Teste</h1><h4>Funciona!!!</h4>"


	@app.get("/forms/transaction")
	def transacoes_get_form():
		return render_template("form_transactions.html", titulo="Importar Transações")


	def allowed_file(filename):
		return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


	@app.post("/transaction")
	def transacoes_post():
		if 'file' not in request.files:
			flash('Nenhum arquivo enviado')
			return redirect(url_for("transacoes_get_form"), 303)

		file = request.files["file"]

		if file.filename == "":
			flash('Nenhum arquivo selecionado')
			return redirect(url_for("transacoes_get_form"), 303)

		if not allowed_file(file.filename):
			flash('Extensão inválida')
			return redirect(url_for("transacoes_get_form"), 303)

		filename = secure_filename(file.filename)
		file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		print(file_path)
		file.save(file_path)
		print(f"Arquivo chegando - filename = {file.filename} - filesize = {os.path.getsize(file_path)} Bytes")
		print(f'Conteúdo: {open(file_path, "r", encoding="UTF-8").read()}')
		flash(f"Arquivo chegando - filename = {file.filename} - filesize = {os.path.getsize(file_path)} Bytes")

		df, error = clean_uploaded_transactions_csv(file_path)

		if error:
			flash(error)
			return redirect(url_for("transacoes_get_form"), 303)

		return redirect(url_for("transacoes_get_form"), 302)
