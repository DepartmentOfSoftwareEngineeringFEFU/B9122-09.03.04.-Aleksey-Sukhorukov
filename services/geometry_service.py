from shapely.geometry import Point, LineString
from models import TrackPoint


from services.geojson_service import (
    GeoJSONService
)


def point_on_land(lat, lon):

    point = Point(
        lon,
        lat
    )

    polygons = (
        GeoJSONService
        .get_land_polygons()
    )

    for polygon in polygons:

        if polygon.intersects(point):
            return True

    return False

def session_has_land_points(session_id):

    points = (
        TrackPoint.query
        .filter_by(session_id=session_id)
        .all()
    )

    for point in points:

        if point_on_land(
            point.lat,
            point.lon
        ):
            return True

    return False

def segment_crosses_land(
    lat1,
    lon1,
    lat2,
    lon2
):

    segment = LineString([
        (lon1, lat1),
        (lon2, lat2)
    ])

    polygons = (
        GeoJSONService
        .get_land_polygons()
    )

    for polygon in polygons:

        if polygon.intersects(segment):
            return True

    return False

from models import TrackPoint


def session_has_land_segments(session_id):

    points = (
        TrackPoint.query
        .filter_by(session_id=session_id)
        .order_by(
            TrackPoint.vessel_id,
            TrackPoint.timestamp
        )
        .all()
    )

    previous = {}

    for point in points:

        vessel_id = point.vessel_id

        if vessel_id in previous:

            prev = previous[vessel_id]

            if segment_crosses_land(
                prev.lat,
                prev.lon,
                point.lat,
                point.lon
            ):
                return True

        previous[vessel_id] = point

    return False