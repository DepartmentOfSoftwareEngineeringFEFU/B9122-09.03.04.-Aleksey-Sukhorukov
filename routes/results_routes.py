from flask import (
    Blueprint,
    render_template,
    jsonify,
    request
)

from sqlalchemy import func

from extensions import db


from models import (
    AISSession,
    TrackPoint,
    Vessel,
    SimRun,
    SimPoint
)

from services.auth_service import login_required
from services.validation_service import validate_session_geometry
from services.geometry_service import (
    session_has_land_points,
    session_has_land_segments
)
from services.traffic_service import build_density_grid
from services.geojson_service import GeoJSONService
from services.geometry_service import point_on_land




results_bp = Blueprint(
    "results",
    __name__
)


@results_bp.route("/results")
@login_required
def results_page():
    sessions = (
        AISSession.query
        .order_by(AISSession.created_at.desc())
        .all()
    )

    runs = (
        SimRun.query
        .order_by(SimRun.start_time.desc())
        .all()
    )

    return render_template(
        "results.html",
        active_page="results",
        sessions=sessions,
        runs=runs
    )


@results_bp.route("/api/session/<int:session_id>/tracks")
@login_required
def api_session_tracks(session_id):

    session_rec = AISSession.query.get(session_id)

    if not session_rec:
        return jsonify(
            error="Сессия не найдена."
        ), 404

    ok, warning = validate_session_geometry(session_rec)

    if not ok:
        return jsonify(error=warning)

    if session_has_land_points(session_id):

        return jsonify(
            error=(
                "Обнаружены точки траекторий, "
                "расположенные на суше. "
                "Отображение невозможно."
            )
        )

    if session_has_land_segments(session_id):

        return jsonify(
            error=(
                "Обнаружены участки траекторий, "
                "пересекающие сушу. "
                "Отображение невозможно."
            )
        )

    points = (

        db.session.query(
            TrackPoint,
            Vessel.number
        )

        .join(
            Vessel,
            TrackPoint.vessel_id == Vessel.id
        )

        .filter(
            TrackPoint.session_id == session_id
        )

        .order_by(
            TrackPoint.vessel_id,
            TrackPoint.timestamp
        )

        .all()

    )

    tracks = {}

    for tp, number in points:

        tracks.setdefault(
            number,
            []
        ).append({

            "lat": tp.lat,

            "lon": tp.lon

        })

    return jsonify(
        tracks=tracks,
        warning=warning
    )

@results_bp.route("/api/run/<int:run_id>/tracks")
@login_required
def api_run_tracks(run_id):

    run = SimRun.query.get(run_id)

    if not run:
        return jsonify(error="Запуск моделирования не найден."), 404

    points = (
        db.session.query(SimPoint, Vessel.number)
        .join(Vessel, SimPoint.vessel_id == Vessel.id)
        .filter(SimPoint.run_id == run_id)
        .order_by(
            SimPoint.vessel_id,
            SimPoint.timestamp
        )
        .all()
    )

    tracks = {}

    for point, number in points:
        tracks.setdefault(number, []).append({
            "lat": point.lat,
            "lon": point.lon
        })

    return jsonify(tracks=tracks)

@results_bp.route("/api/session/<int:session_id>/traffic")
@login_required
def api_session_traffic(session_id):
    session_rec = AISSession.query.get(session_id)

    if not session_rec:
        return jsonify(
            error="Сессия не найдена."
        ), 404

    window = request.args.get(
        "window",
        "all"
    )

    grid = build_density_grid(
        session_id,
        window
    )

    return jsonify(
        grid=grid
    )

@results_bp.route("/api/geometry")
@login_required
def api_geometry():
    return jsonify(
        GeoJSONService.load_geojson()
    )

@results_bp.route("/debug/land")
@login_required
def debug_land():

    return jsonify({
        "port": point_on_land(43.105, 131.90),
        "artem": point_on_land(43.35, 132.15),
        "sea": point_on_land(43.03, 131.97)
    })



