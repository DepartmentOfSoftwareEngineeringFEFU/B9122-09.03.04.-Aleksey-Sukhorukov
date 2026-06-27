from datetime import datetime

from extensions import db


class TrafficLevel(db.Model):
    """
    Уровень интенсивности трафика.
    """

    __tablename__ = "traffic_level"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.String(255)
    )


class ModelConfig(db.Model):
    """
    Конфигурация модели движения.
    """

    __tablename__ = "model_config"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    model_type = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text
    )


class Scenario(db.Model):
    """
    Сценарий моделирования.
    """

    __tablename__ = "scenario"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    aquatory_id = db.Column(
        db.Integer,
        db.ForeignKey("aquatory.id"),
        nullable=False
    )

    model_id = db.Column(
        db.Integer,
        db.ForeignKey("model_config.id"),
        nullable=False
    )

    level_id = db.Column(
        db.Integer,
        db.ForeignKey("traffic_level.id"),
        nullable=False
    )

    start_time = db.Column(
        db.DateTime
    )

    end_time = db.Column(
        db.DateTime
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    aquatory = db.relationship(
        "Aquatory"
    )

    model = db.relationship(
        "ModelConfig"
    )

    traffic_level = db.relationship(
        "TrafficLevel"
    )


class ScenarioVessel(db.Model):
    """
    Судно, участвующее в сценарии.
    """

    __tablename__ = "scenario_vessel"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    scenario_id = db.Column(
        db.Integer,
        db.ForeignKey("scenario.id"),
        nullable=False
    )

    vessel_id = db.Column(
        db.Integer,
        db.ForeignKey("vessel.id"),
        nullable=False
    )

    scenario = db.relationship(
        "Scenario",
        backref="scenario_vessels"
    )

    vessel = db.relationship(
        "Vessel"
    )


class SimRun(db.Model):
    """
    Запуск моделирования.
    """

    __tablename__ = "sim_run"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    scenario_id = db.Column(
        db.Integer,
        db.ForeignKey("scenario.id"),
        nullable=False
    )

    start_time = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    end_time = db.Column(
        db.DateTime
    )

    status = db.Column(
        db.String(30),
        default="Создан"
    )

    scenario = db.relationship(
        "Scenario",
        backref="runs"
    )


class SimPoint(db.Model):
    """
    Точка смоделированной траектории.
    """

    __tablename__ = "sim_point"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    run_id = db.Column(
        db.Integer,
        db.ForeignKey("sim_run.id"),
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

    sog = db.Column(
        db.Float
    )

    cog = db.Column(
        db.Float
    )

    run = db.relationship(
        "SimRun",
        backref="points"
    )

    vessel = db.relationship(
        "Vessel"
    )


class MetricValue(db.Model):
    """
    Рассчитанные показатели моделирования.
    """

    __tablename__ = "metric_value"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    run_id = db.Column(
        db.Integer,
        db.ForeignKey("sim_run.id"),
        nullable=False
    )

    metric_type = db.Column(
        db.String(100),
        nullable=False
    )

    value = db.Column(
        db.Float,
        nullable=False
    )

    run = db.relationship(
        "SimRun",
        backref="metrics"
    )