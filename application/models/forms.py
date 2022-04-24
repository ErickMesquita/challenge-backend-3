from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, NoneOf, Email


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


class LoginForm(FlaskForm):
	username_or_email = StringField(
		label="Nome de Usuário ou Email",
		validators=[InputRequired(message="Digite seu nome de usuário ou email"), Length(1, 80)]
	)
	password = PasswordField(label="Senha", validators=[InputRequired(message="Digite sua senha"), Length(min=6, max=6, message="A senha deve ter 6 caracteres")])
