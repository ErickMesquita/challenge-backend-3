from application.models import bcrypt
from flask_bcrypt import check_password_hash as bcrypt_check_password_hash
from hashlib import sha512
from secrets import randbelow


def generate_password() -> str:
	"""
	Generates a random 6-digits number and returns it as a string.
	"""
	return str(randbelow(1000000)).zfill(6)


def hash_password(password: str) -> str:
	"""
	Receives a password string, gets its SHA-512 hash, then encrypts it with bcrypt
	"""
	sha512hash = sha512(password.encode("utf-8")).digest()  # Bytes
	sha512hash_nilsafe = sha512hash.replace(b"\x00", b"\x45")  # This avoids bcrypt ValueError
	enc_password = bcrypt.generate_password_hash(sha512hash_nilsafe)  # Bytes
	enc_password_str = str(enc_password, encoding="utf8")
	return enc_password_str


def check_password_hash(user_password_hash: str, candidate_password: str) -> bool:
	candidate_sha512 = sha512(candidate_password.encode("utf-8")).digest()  # Bytes
	candidate_sha512_safe = candidate_sha512.replace(b"\x00", b"\x45")  # Bytes # Avoid bcrypt ValueError

	return bcrypt_check_password_hash(user_password_hash, candidate_sha512_safe)