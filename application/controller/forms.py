from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Length, Regexp, NoneOf, EqualTo, ValidationError, Email

from application.models import User, db


class SignUpForm(FlaskForm):
	username = StringField(
		label="Nome de usuário",
		validators=[
			InputRequired(),
			NoneOf(values="Admin")
		]
	)
	password = PasswordField(
		label="Senha",
		validators=[
			InputRequired(),
			Length(8, 512, message="A senha deve ter mais do que 8 caracteres")
		]
	)
	c_password = PasswordField(
		label="Digite a senha novamente",
		validators=[
			InputRequired(),
			Length(8, 512),
			EqualTo("password", message="As senhas devem ser iguais")
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

