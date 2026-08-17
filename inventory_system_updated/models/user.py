import hashlib

from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(self, userID, username, password):
        self.userID = userID
        self.username = username
        self.password = password

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def verify_password(self, plain_password):
        if self.password == hashlib.sha256(plain_password.encode()).hexdigest():
            return True
        return check_password_hash(self.password, plain_password)
