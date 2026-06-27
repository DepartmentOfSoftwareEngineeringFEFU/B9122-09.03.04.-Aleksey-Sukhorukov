from math import (
    radians,
    sin,
    cos,
    asin,
    sqrt
)

from sqlalchemy import func

from models import (
    TrackPoint,
    AISSession
)


def haversine_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        +
        cos(radians(lat1))
        *
        cos(radians(lat2))
        *
        sin(dlon / 2) ** 2
    )

    c = 2 * asin(sqrt(a))

    return R * c


def validate_session_geometry(
    session_rec: AISSession
):

    aq = session_rec.aquatory

    if not aq:
        return True, None

    if None in (
        aq.min_lat,
        aq.max_lat,
        aq.min_lon,
        aq.max_lon
    ):
        return True, None

    bad_points = (
        TrackPoint.query
        .filter(
            TrackPoint.session_id == session_rec.id
        )
        .filter(
            (
                TrackPoint.lat < aq.min_lat
            )
            |
            (
                TrackPoint.lat > aq.max_lat
            )
            |
            (
                TrackPoint.lon < aq.min_lon
            )
            |
            (
                TrackPoint.lon > aq.max_lon
            )
        )
        .count()
    )

    if bad_points:

        return (
            False,
            f"Найдено {bad_points} точек вне акватории."
        )

    if not aq.ports:
        return True, None

    first_points = (
        TrackPoint.query
        .with_entities(
            TrackPoint.vessel_id,
            func.min(
                TrackPoint.timestamp
            )
        )
        .filter(
            TrackPoint.session_id == session_rec.id
        )
        .group_by(
            TrackPoint.vessel_id
        )
        .all()
    )

    MAX_DIST = 2.0

    bad_starts = 0

    for vessel_id, t0 in first_points:

        point = (
            TrackPoint.query
            .filter_by(
                session_id=session_rec.id,
                vessel_id=vessel_id,
                timestamp=t0
            )
            .first()
        )

        if not point:
            continue

        nearest = min(
            haversine_km(
                point.lat,
                point.lon,
                port.lat,
                port.lon
            )
            for port in aq.ports
        )

        if nearest > MAX_DIST:
            bad_starts += 1

    warning = None

    if bad_starts > 0:
        warning = (
            f"Для {bad_starts} судов начальная точка "
            f"находится вне района порта."
        )

    return True, warning