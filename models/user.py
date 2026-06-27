from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(
        db.String(64),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(128),
        nullable=False
    )

    role = db.Column(
        db.String(16),
        nullable=False,
        default="analyst"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )