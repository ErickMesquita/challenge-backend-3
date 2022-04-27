import os
from urllib.parse import urlparse, urljoin

from flask import redirect, render_template, url_for, request, flash, Flask, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from application.controller import transactions_utils as t_utils
from application.models.forms import LoginForm, SignUpForm
from application.models.user import User
from application.controller.password_utils import check_password_hash
from application.controller.user_utils import get_users_list, user_from_db, edit_user_account, \
	create_or_reactivate_user, load_user_from_id
from markupsafe import escape


def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def configure_routes(app: Flask):

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
			return redirect(url_for("transactions_get_form"), 303)

		file = request.files["file"]

		if file.filename == "":
			flash('Nenhum arquivo selecionado')
			return redirect(url_for("transactions_get_form"), 303)

		if not allowed_file(file.filename):
			flash('Extensão inválida')
			return redirect(url_for("transactions_get_form"), 303)

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
			return redirect(url_for("transactions_get_form"), 303)

		t_utils.push_transactions_to_db(df)

		return redirect(url_for("transactions_get_form"), 302)

	@app.get("/transactions")
	@login_required
	def transactions_get():
		return "Transactions get"

	@app.route("/login", methods=["GET", "POST"])
	def login():
		form = LoginForm()
		if not form.validate_on_submit():
			return render_template("form_login.html", title="Login", form=form)

		user = user_from_db(username_or_email=form.username_or_email.data)

		if user is None or not user.active:
			return login_invalid("Nome de usuário ou email inválido", "danger")

		if not check_password_hash(user.password, form.password.data):
			return login_invalid("Senha inválida", "danger")

		login_user(user)
		flash(f"Usuário {user.username} logado com sucesso!", "success")

		if "next" not in request.args:
			return redirect(url_for("transactions_get_form"))

		next_url = request.args.get('next')

		if next_url == "/logout":
			return redirect(url_for("transactions_get_form"))
		if not is_safe_url(next_url):
			return abort(400)
		return redirect(next_url)

	def login_invalid(message: str, category: str = None):
		flash(message, category)
		return redirect(url_for("login", next=request.args.get("next")))

	@app.get("/logout")
	@login_required
	def logout():
		logout_user()
		flash(f"Usuário saiu com sucesso!", category="info")
		return redirect(url_for("login"))

	@app.get("/forms/signup")
	@login_required
	def signup_form_get():
		form = SignUpForm()
		return render_template("form_edit_user.html", title="Cadastrar Usuário", form=form, button_text="Cadastrar")

	@app.post("/users")
	@login_required
	def users_post():
		form = SignUpForm()
		if not form.validate_on_submit():
			for field in form.errors.keys():
				for error in form.errors.get(field):
					flash(f"{field} error: {error}", "danger")
			return redirect(url_for("signup_form_get"))

		username = form.username.data
		email = form.email.data

		password, error = create_or_reactivate_user(username, email)

		if error:
			flash(error, "danger")
			return redirect(url_for("signup_form_get"))

		flash(f"Senha: {password}", "success")
		return redirect(url_for("login"))

	@app.get("/users")
	@login_required
	def users_get():
		return render_template("show_users.html", title="Usuários Cadastrados", users_list=get_users_list())

	@app.get("/users/<int:user_id>")
	@login_required
	def users_edit_form_get(user_id: int):
		if user_id == 1:
			return redirect(url_for("users_get"))

		form = SignUpForm()
		user = load_user_from_id(user_id=user_id)
		if not user:
			return redirect(url_for("users_get"))

		return render_template("form_edit_user.html", title="Editar Usuário", form=form, user=user, button_text="Salvar")

	@app.delete("/users/<int:user_id>")
	@login_required
	def users_delete(user_id: int):
		if user_id == 1 or user_id == current_user.id:
			flash("Não é possível excluir a si mesmo", category="warning")
			return redirect(url_for("users_edit_form_get", user_id=user_id))

		user = load_user_from_id(user_id=user_id)
		if not user:
			flash("Usuário não encontrado", category="warning")
			return redirect(url_for("users_get"))

		user.deactivate_account()
		flash(f"Usuário {escape(user.username)} excluído com sucesso", category="success")
		return "", 205

	@app.route("/users/<int:user_id>", methods=["PUT", "PATCH", "POST"])
	@login_required
	def users_put(user_id: int):
		if user_id == 1:
			return redirect(url_for("users_get"))

		user = load_user_from_id(user_id=user_id)

		if not user:
			flash("Usuário não encontrado", category="warning")
			return redirect(url_for("users_get"))

		form = SignUpForm()
		if not form.validate_on_submit():
			for field in form.errors.keys():
				for error in form.errors.get(field):
					flash(f"{field} error: {error}", "danger")
			return redirect(url_for("users_edit_form_get", user_id=user_id))

		new_username = form.username.data
		new_email = form.email.data

		success_message, error = edit_user_account(user, new_username, new_email)

		if error:
			flash(error, "danger")
			return redirect(url_for("users_get"))

		flash(success_message, "success")
		return redirect(url_for("users_get"))
