from flask import (
    Blueprint,
    render_template,
    request,
    flash
)

from extensions import db

from models import (
    AISSession,
    TrackPoint
)

from services.auth_service import login_required
from services.retrospective_service import get_session_stats


retrospective_bp = Blueprint(
    "retrospective",
    __name__
)


@retrospective_bp.route(
    "/retrospective",
    methods=["GET", "POST"]
)
@login_required
def retrospective_page():

    stats = None

    if request.method == "POST":

        action = request.form.get("action")

        #
        # Удаление сессии
        #
        if action == "delete":

            delete_id = request.form.get(
                "delete_id",
                type=int
            )

            if delete_id:

                session_record = AISSession.query.get(delete_id)

                if session_record:

                    TrackPoint.query.filter_by(
                        session_id=session_record.id
                    ).delete()

                    db.session.delete(session_record)

                    db.session.commit()

                    flash(
                        f"Сессия № {delete_id} удалена.",
                        "info"
                    )

        #
        # Расчёт статистики
        #
        elif action == "stats":

            session_id = request.form.get(
                "session_id",
                type=int
            )

            if session_id:

                stats = get_session_stats(
                    session_id
                )

                if stats is None:

                    flash(
                        "Выбранная сессия не найдена.",
                        "warning"
                    )

            else:

                flash(
                    "Не выбрана сессия.",
                    "warning"
                )

    sessions = (
        AISSession.query
        .order_by(
            AISSession.created_at.desc()
        )
        .all()
    )

    return render_template(

        "retrospective.html",

        active_page="retro",

        sessions=sessions,

        stats=stats

    )