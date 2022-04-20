from application.models import db, User, login_manager


def user_from_db(username_or_email=None, **kwargs):
	if username_or_email is None:
		query = db.select(User).filter_by(**kwargs)
	else:
		query = db.select(User).\
			where(
				db.or_(User.username == username_or_email,
					   User.email == username_or_email)
			)

	return db.session.scalars(query).first()


@login_manager.user_loader
def load_user(user_id):
	query = db.select(User).where(User.id == user_id)
	return db.session.scalars(query).first()
