from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, NoneOf, ValidationError, Email

from application.models import User, db


class SignUpForm(FlaskForm):
	username = StringField(
		label="Nome de usuário",
		validators=[
			InputRequired(message="Digite um nome de usuário"),
			NoneOf(values="Admin")
		]
	)
	email = EmailField(
		label="Email",
		validators=[
			InputRequired(message="Digite um email"),
			Email(message="Email inválido")
		]
	)

"""
	@staticmethod
	def validate_email(form, field):
		query = db.select(User).where(User.email == field.data)
		if db.session.scalars(query).first():
			raise ValidationError("Email already registered!")

	@staticmethod
	def validate_username(form, field):
		query = db.select(User).where(User.username == field.data)
		if db.session.scalars(query).first():
			raise ValidationError("Username already taken!")
"""

class LoginForm(FlaskForm):
	username_or_email = StringField(
		label="Nome de Usuário ou Email",
		validators=[InputRequired(message="Digite seu nome de usuário ou email"), Length(1, 80)]
	)
	password = PasswordField(label="Senha", validators=[InputRequired(message="Digite sua senha"), Length(min=6, max=6, message="A senha deve ter 6 caracteres")])

