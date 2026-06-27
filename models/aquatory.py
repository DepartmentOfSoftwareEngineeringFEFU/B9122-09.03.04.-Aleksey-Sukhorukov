from extensions import db


class Aquatory(db.Model):
    __tablename__ = "aquatory"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    geometry = db.Column(db.Text)

    area = db.Column(db.Float)

    zone_type = db.Column(db.String(20))

    speed_limit = db.Column(db.Float)

    ports_count = db.Column(db.Integer)

    min_lat = db.Column(db.Float)
    max_lat = db.Column(db.Float)

    min_lon = db.Column(db.Float)
    max_lon = db.Column(db.Float)


class Port(db.Model):
    __tablename__ = "port"

    id = db.Column(db.Integer, primary_key=True)

    aquatory_id = db.Column(
        db.Integer,
        db.ForeignKey("aquatory.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    lat = db.Column(
        db.Float,
        nullable=False
    )

    lon = db.Column(
        db.Float,
        nullable=False
    )

    aquatory = db.relationship(
        "Aquatory",
        backref="ports"
    )