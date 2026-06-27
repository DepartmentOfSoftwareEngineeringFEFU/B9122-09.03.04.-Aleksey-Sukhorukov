from extensions import db


class Vessel(db.Model):
    __tablename__ = "vessel"

    id = db.Column(db.Integer, primary_key=True)

    number = db.Column(
        db.String(64),
        unique=True,
        nullable=False
    )

    name = db.Column(db.String(128))

    vessel_type = db.Column(db.String(32))