import os
from base64 import b64decode, b64encode
from urllib.parse import urlparse, urljoin

from flask import redirect, render_template, url_for, request, flash, Flask, session, abort
from flask_login import login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from application.controller import transactions_utils as t_utils
from application.controller import user_utils as u_utils
from application.controller.forms import LoginForm, SignUpForm
from hashlib import sha512


def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def configure_routes(app: Flask):
	@app.get("/teste")
	def _teste():
		return "<h1>Teste</h1><h4>Funciona!!!</h4>"

	@app.get("/forms/transaction")
	@login_required
	def transactions_get_form():
		return render_template("form_transactions.html", title="Importar Transações")

	def allowed_file(filename):
		return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

	@app.post("/transaction")
	def transactions_post():
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

		df, error = t_utils.clean_uploaded_transactions_csv(file_path)

		if error:
			flash(error)
			return redirect(url_for("transacoes_get_form"), 303)

		t_utils.push_transactions_to_db(df)

		return redirect(url_for("transacoes_get_form"), 302)

	@app.get("/transactions")
	@login_required
	def transactions_get():
		return "Transactions get"

	@app.route("/login", methods=["GET", "POST"])
	def login():
		form = LoginForm()
		if not form.validate_on_submit():
			return render_template("form_login.html", title="Login", form=form)

		user = u_utils.user_from_db(username_or_email=form.username_or_email.data)

		if user is None or not user.active:
			return login_invalid("Nome de usuário ou email inválido", "danger")

		if not u_utils.check_password_hash(user.password, form.password.data):
			return login_invalid("Senha inválida", "danger")

		login_user(user)
		flash(f"Usuário {user.username} logado com sucesso!", "success")

		if "next" not in request.args:
			return redirect(url_for("transactions_get_form"))

		next_url = request.args.get('next')

		if not is_safe_url(next_url):
			return abort(400)
		return redirect(next_url)

	def login_invalid(message: str, category: str = None):
		flash(message, category)
		return redirect(url_for("login", next=request.args.get("next")))

	@app.get("/logout")
	def logout():
		logout_user()
		flash(f"Usuário saiu com sucesso!")
		return redirect(url_for("_teste"))

	@app.get("/forms/signup")
	def signup_form_get():
		form = SignUpForm()
		return render_template("form_signup.html", title="Sign Up", form=form)

	@app.post("/users")
	def users_post():
		form = SignUpForm()
		if not form.validate_on_submit():
			return redirect(url_for("signup_form_get"))

		username = form.username.data
		email = form.email.data

		success, message = u_utils.create_new_user(username, email)

		if not success:
			flash(message, "danger")
		else:
			flash(f"Senha: {message}")

		return redirect(url_for("login"))




