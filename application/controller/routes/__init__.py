from urllib.parse import urlparse, urljoin

from flask import redirect, render_template, url_for, request, flash, Flask, abort
from flask_login import login_user, login_required, logout_user

from application.controller.routes.transactions import configure_routes_transactions
from application.controller.routes.users import configure_routes_users
from application.models.forms import LoginForm, SignUpForm
from application.controller.password_utils import check_password_hash
from application.controller.user_utils import user_from_db


def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def configure_routes(app: Flask):

	configure_routes_users(app)
	configure_routes_transactions(app)

	@app.route("/")
	def index():
		return redirect("login")

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
			return redirect(url_for("transactions_get"))

		next_url = request.args.get('next')

		if next_url == "/logout":
			return redirect(url_for("transactions_get"))
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
