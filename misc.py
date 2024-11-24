from werkzeug.security import generate_password_hash, check_password_hash

class PassAction:

    @staticmethod
    def hash_passwords(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def verify_password(hashed_password: str, input_password: str) -> bool:
        return check_password_hash(hashed_password, input_password)
