from flask import Flask, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from markupsafe import escape

from application.controller.user_utils import create_or_reactivate_user, get_users_list, load_user_from_id, \
	edit_user_account
from application.models.forms import SignUpForm


def configure_routes_users(app: Flask):

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
		return redirect(url_for("users_get"))

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
		flash(f"Conta de usuário {escape(user.username)} desativada com sucesso", category="success")
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
