from flask import (
    Blueprint,
    render_template,
    request
)

from werkzeug.utils import secure_filename

from models import Aquatory

from services.auth_service import login_required
from services.import_service import process_import


import_bp = Blueprint(
    "import",
    __name__
)


@import_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_page():

    stats = None

    aquatories = Aquatory.query.all()

    if request.method == "POST":

        uploaded_file = request.files.get("data_file")

        action = request.form.get(
            "action",
            "check"
        )

        file_format = request.form.get(
            "file_format",
            "CSV"
        )

        aquatory_id = request.form.get(
            "aquatory_id",
            type=int
        )

        stats = process_import(
            uploaded_file=uploaded_file,
            action=action,
            file_format=file_format,
            aquatory_id=aquatory_id,
            secure_filename_func=secure_filename
        )

    return render_template(
        "import.html",
        active_page="import",
        stats=stats,
        aquatories=aquatories
    )