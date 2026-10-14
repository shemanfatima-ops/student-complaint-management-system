from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, name, email, password_hash, user_id=None):
        self.id = user_id
        self.name = name
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)