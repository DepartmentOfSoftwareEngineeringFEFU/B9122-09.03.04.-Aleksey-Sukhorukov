from datetime import datetime

from extensions import db


class AISSession(db.Model):
    __tablename__ = "ais_session"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    aquatory_id = db.Column(
        db.Integer,
        db.ForeignKey("aquatory.id")
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False
    )

    file_format = db.Column(
        db.String(16),
        nullable=False
    )

    total_records = db.Column(
        db.Integer,
        default=0
    )

    time_start = db.Column(db.DateTime)

    time_end = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="ais_sessions"
    )

    aquatory = db.relationship(
        "Aquatory",
        backref="sessions"
    )


class TrackPoint(db.Model):
    __tablename__ = "track_point"

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("ais_session.id"),
        nullable=False
    )

    vessel_id = db.Column(
        db.Integer,
        db.ForeignKey("vessel.id"),
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
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

    sog = db.Column(db.Float)

    cog = db.Column(db.Float)

    session = db.relationship(
        "AISSession",
        backref="track_points"
    )

    vessel = db.relationship(
        "Vessel",
        backref="track_points"
    )