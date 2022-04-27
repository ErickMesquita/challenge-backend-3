from flask_login import UserMixin
from application.models import db


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), nullable=False, unique=True)
	password = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False)
	login_id = db.Column(db.Integer, db.Identity(start=5000, increment=1, cycle=True), nullable=False, unique=True)
	active = db.Column(db.Boolean, db.ColumnDefault(True), nullable=False)

	__table_args__ = (db.CheckConstraint("login_id <> id",
										  name="id_and_login_id_are_different"),)

	def __repr__(self):
		return f"<User {self.username}>"

	def get_id(self):
		if self.login_id is not None:
			return str(self.login_id)
		query = db.select(User.login_id).filter_by(id=self.id)
		return db.session.scalars(query).first()

	def deactivate_account(self):
		self.active = False
		db.session.add(self)
		db.session.commit()
