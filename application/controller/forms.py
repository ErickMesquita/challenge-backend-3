from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, NoneOf, ValidationError, Email

from application.models import User, db


class SignUpForm(FlaskForm):
	username = StringField(
		label="Nome de usuário",
		validators=[
			InputRequired(),
			NoneOf(values="Admin")
		]
	)
	email = EmailField(
		label="Email",
		validators=[
			InputRequired(),
			Email(message="Email inválido")
		]
	)

	@staticmethod
	def validate_email(email):
		query = db.select(User).where(User.email == email)
		if db.session.scalars(query).first():
			raise ValidationError("Email already registered!")

	@staticmethod
	def validate_username(username):
		query = db.select(User).where(User.username == username)
		if db.session.scalars(query).first():
			raise ValidationError("Username already taken!")


class LoginForm(FlaskForm):
	username_or_email = StringField(
		label="Nome de Usuário ou Email",
		validators=[InputRequired(), Length(1, 80)]
	)
	password = PasswordField(label="Senha", validators=[InputRequired(), Length(min=6, max=6)])

