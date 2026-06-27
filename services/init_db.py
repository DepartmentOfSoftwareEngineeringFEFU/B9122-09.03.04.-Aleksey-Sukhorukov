from models import (
    User,
    Aquatory,
    Port,
    TrafficLevel,
    ModelConfig
)

from extensions import db


def init_db():

    db.create_all()

    if not User.query.filter_by(
        login="admin"
    ).first():

        admin = User(
            login="admin",
            role="admin"
        )

        admin.set_password("admin")

        db.session.add(admin)

    if not Aquatory.query.first():

        aq = Aquatory(
            name="Акватория Владивосток",
            geometry=None,
            area=2500,
            zone_type="прибрежная",
            speed_limit=7.0,
            ports_count=1,
            min_lat=42.8,
            max_lat=43.5,
            min_lon=131.7,
            max_lon=132.3
        )

        db.session.add(aq)

        db.session.flush()

        db.session.add(

            Port(
                aquatory_id=aq.id,
                name="Порт Владивосток",
                lat=43.105,
                lon=131.90
            )

        )


    if TrafficLevel.query.count() == 0:
        db.session.add_all([

            TrafficLevel(
                name="Низкий",
                description="До 5 одновременно находящихся судов в акватории"
            ),

            TrafficLevel(
                name="Средний",
                description="От 6 до 15 одновременно находящихся судов"
            ),

            TrafficLevel(
                name="Высокий",
                description="Более 15 одновременно находящихся судов"
            )

        ])

        if ModelConfig.query.count() == 0:
            db.session.add_all([

                ModelConfig(

                    name="Статистическая",

                    model_type="statistical",

                    description=(
                        "Построение движения на основе "
                        "ретроспективных данных АИС "
                        "с небольшими вариациями скорости."
                    )

                ),

                ModelConfig(

                    name="Повторение ретроспективной траектории",

                    model_type="replay",

                    description=(
                        "Использование существующей "
                        "ретроспективной траектории "
                        "без изменения маршрута."
                    )

                )

            ])

    db.session.commit()