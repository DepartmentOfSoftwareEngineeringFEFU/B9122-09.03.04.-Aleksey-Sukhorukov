import os

from flask import Flask

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # импорт моделей
    from models import (
        User,
        Aquatory,
        Port,
        Vessel,
        AISSession,
        TrackPoint
    )

    # регистрация уже готовых Blueprint
    from routes.auth_routes import auth_bp
    from routes.main_routes import main_bp
    from routes.import_routes import import_bp
    from routes.retrospective_routes import retrospective_bp
    from routes.results_routes import results_bp
    from routes.admin_routes import admin_bp
    from routes.simulation_routes import simulation_bp
    from routes.clustering_routes import clustering_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(retrospective_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(clustering_bp)


    # создание БД
    from services.init_db import init_db

    with app.app_context():
        init_db()

    # current_user для шаблонов
    from services.auth_service import get_current_user

    @app.context_processor
    def inject_user():
        return {
            "current_user": get_current_user()
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)