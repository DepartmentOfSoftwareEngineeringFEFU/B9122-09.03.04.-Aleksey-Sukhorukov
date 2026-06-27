from sqlalchemy import func

from extensions import db

from models import (
    AISSession,
    TrackPoint
)


def get_session_stats(session_id):

    session_rec = AISSession.query.get(session_id)

    if not session_rec:
        return None

    base_q = TrackPoint.query.filter_by(
        session_id=session_id
    )

    points_count = base_q.count()

    vessels_count = (
        db.session.query(
            func.count(
                func.distinct(
                    TrackPoint.vessel_id
                )
            )
        )
        .filter(
            TrackPoint.session_id == session_id
        )
        .scalar()
    ) or 0

    speed_min = speed_max = speed_avg = None

    speed_stats = (
        db.session.query(
            func.min(TrackPoint.sog),
            func.max(TrackPoint.sog),
            func.avg(TrackPoint.sog)
        )
        .filter(
            TrackPoint.session_id == session_id,
            TrackPoint.sog.isnot(None)
        )
        .one()
    )

    speed_min, speed_max, speed_avg = speed_stats

    duration_hours = None

    if (
        session_rec.time_start
        and
        session_rec.time_end
    ):

        duration = (
            session_rec.time_end
            -
            session_rec.time_start
        ).total_seconds()

        if duration > 0:
            duration_hours = duration / 3600

    traffic_intensity = None

    if (
        session_rec.aquatory
        and
        session_rec.aquatory.area
        and
        session_rec.aquatory.area > 0
    ):

        traffic_intensity = (
            vessels_count
            /
            session_rec.aquatory.area
        )

    return {
        "session": session_rec,
        "points": points_count,
        "vessels": vessels_count,
        "speed_min": speed_min,
        "speed_max": speed_max,
        "speed_avg": speed_avg,
        "duration_hours": duration_hours,
        "traffic_intensity": traffic_intensity,
    }