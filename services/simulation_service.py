import random
from datetime import datetime, timedelta

from extensions import db
from uuid import uuid4

from models import (
    Scenario,
    SimRun,
    SimPoint,
    TrackPoint,
    Vessel
)
from services.clustering_service import TrajectoryClusterService
from services.geometry_service import (
    point_on_land,
    segment_crosses_land
)


def run_simulation(scenario_id: int):

    scenario = Scenario.query.get(scenario_id)

    if not scenario:
        raise ValueError("Сценарий не найден.")

    run = SimRun(
        scenario_id=scenario.id,
        status="Выполняется"
    )

    db.session.add(run)
    db.session.flush()

    # Берём последнюю сессию выбранной акватории
    session_record = (
        scenario.aquatory.sessions[-1]
        if scenario.aquatory.sessions
        else None
    )

    if session_record is None:
        raise ValueError("Для выбранной акватории нет импортированных данных.")

    cluster_data = (
        TrajectoryClusterService.cluster_trajectories(
            session_record.id
        )
    )

    cluster_tracks = cluster_data.get("cluster_tracks", {})

    if scenario.traffic_level.name == "Низкий":
        traffic_coeff = 0.5

    elif scenario.traffic_level.name == "Средний":
        traffic_coeff = 1.0

    else:
        traffic_coeff = 1.8

    model_type = scenario.model.model_type

    sim_vessel_counter = 1

    for cluster in cluster_tracks.values():

        cluster_size = len(cluster["vessels"])

        generated_vessels = max(
            1,
            round(cluster_size * traffic_coeff)
        )

        for vessel_index in range(generated_vessels):

            sim_vessel = Vessel(
                number=f"SIM_{uuid4().hex[:8]}",
                name=f"Смоделированное судно {sim_vessel_counter}",
                vessel_type="simulation"
            )

            db.session.add(sim_vessel)
            db.session.flush()

            sim_vessel_counter += 1

            time_shift = timedelta(
                minutes=random.randint(0, 20)
            )

            previous_lat = None
            previous_lon = None

            for point in cluster["track"]:

                point_time = datetime.fromisoformat(
                    point["timestamp"]
                )

                if (
                        scenario.start_time is not None
                        and point_time < scenario.start_time
                ):
                    continue

                if (
                        scenario.end_time is not None
                        and point_time > scenario.end_time
                ):
                    continue

                lat = (
                        point["lat"] +
                        random.uniform(-0.00008, 0.00008)
                )

                lon = (
                        point["lon"] +
                        random.uniform(-0.00008, 0.00008)
                )


                sog = cluster["avg_speed"]

                if sog <= 0:
                    sog = random.uniform(5, 10)

                if model_type == "statistical":
                    coeff = random.uniform(0.95, 1.05)
                    sog = round(sog * coeff, 2)

                    lat += random.uniform(-0.00005, 0.00005)
                    lon += random.uniform(-0.00005, 0.00005)

                    if point_on_land(lat, lon):
                        break

                    if (
                            previous_lat is not None
                            and
                            segment_crosses_land(
                                previous_lat,
                                previous_lon,
                                lat,
                                lon
                            )
                    ):
                        break

                sim_point = SimPoint(
                    run_id=run.id,
                    vessel_id=sim_vessel.id,
                    timestamp=(
                            point_time +
                            time_shift
                    ),
                    lat=lat,
                    lon=lon,
                    sog=sog,
                    cog=None
                )

                db.session.add(sim_point)

                previous_lat = lat
                previous_lon = lon

    run.status = "Завершено"
    run.end_time = datetime.utcnow()

    db.session.commit()

    return run