from collections import defaultdict

from models import TrackPoint

from datetime import timedelta


def build_density_grid(
    session_id,
    window="all",
    cell_size=0.05
):
    points = TrackPoint.query.filter_by(session_id=session_id).all()

    if not points:
        return []

    points.sort(key=lambda p: p.timestamp)

    if window != "all":
        hours = int(window)

        start_time = points[0].timestamp
        end_time = start_time + timedelta(hours=hours)

        points = [
            p for p in points
            if p.timestamp <= end_time
        ]

    grid = defaultdict(int)

    for point in points:
        cell_lat = round(point.lat / cell_size) * cell_size
        cell_lon = round(point.lon / cell_size) * cell_size

        grid[(cell_lat, cell_lon)] += 1

    result = []

    for (lat, lon), count in grid.items():
        result.append({
            "lat": lat,
            "lon": lon,
            "count": count
        })

    return result