from flask import (
    Blueprint,
    redirect,
    url_for
)

from services.auth_service import (
    login_required
)


main_bp = Blueprint(
    "main",
    __name__
)


@main_bp.route("/")
@login_required
def index():

    return redirect(
        url_for ("results.results_page")
    )