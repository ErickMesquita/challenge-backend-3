from flask import Flask, flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user

from application.controller.transactions_utils import get_extension_strategy
from application.controller.transactions_utils.analysis import get_transactions_from_month, get_sus_transactions, \
	get_sus_accounts, get_sus_branches
from application.models.forms import TransactionUploadForm
from application.controller import transactions_utils as t_utils


def configure_routes_transactions(app: Flask):

	@app.get("/transactions")
	@login_required
	def transactions_get():
		form = TransactionUploadForm()
		return render_template("form_transactions.html", title="Importar Transações",
							   form=form, transactions_files_list=t_utils.get_transactions_files_list())

	@app.get("/transactions/<int:transactions_file_id>")
	@login_required
	def transactions_file_get(transactions_file_id):
		transactions_file = t_utils.transactions_file_from_id(transactions_file_id)
		if not transactions_file:
			flash("Upload não encontrado", category="warning")
			return redirect(url_for("transactions_get"), 303)

		return render_template("show_transactions_details.html", transactions_file=transactions_file)

	@app.post("/transactions")
	@login_required
	def transactions_post():
		form = TransactionUploadForm()

		if not form.validate_on_submit():
			return redirect(url_for("transactions_get"), 303)

		file = form.file.data

		upload_folder_path = app.config['UPLOAD_FOLDER']
		file_path, error = t_utils.save_uploaded_file(file, upload_folder_path, current_user.id)
		if error:
			flash(error, category="warning")
			return redirect(url_for("transactions_get"), 303)

		strategy = get_extension_strategy(file_path)

		df, error = strategy.read_file(file_path)

		df, date, error = t_utils.clean_uploaded_transactions(df)

		if error:
			flash(error, category="warning")
			return redirect(url_for("transactions_get"), 303)

		success, error = t_utils.push_transactions_to_db(df, date, current_user, file_path)

		if error:
			flash(error, category="warning")
			return redirect(url_for("transactions_get"), 303)

		flash(f"Upload das transações do dia {date} bem sucedido", category="success")
		return redirect(url_for("transactions_get"), 302)

	@app.get("/transactions/analysis")
	@login_required
	def transactions_analysis_get():
		if not ("year" in request.args.keys() and "month" in request.args.keys()):
			return render_template("show_transactions_analysis.html", date_selected=False)

		month = int(request.args.get("month"))
		year = int(request.args.get("year"))
		transactions = get_transactions_from_month(month, year)

		sus_transactions = get_sus_transactions(transactions)
		sus_accounts = get_sus_accounts(transactions)
		sus_branches = get_sus_branches(transactions)

		return render_template("show_transactions_analysis.html", date_selected=True,
							   sus_transactions=sus_transactions,
							   sus_accounts=sus_accounts,
							   sus_branches=sus_branches)
