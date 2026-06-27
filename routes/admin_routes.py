from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask import send_from_directory
import shutil
from datetime import datetime
from pathlib import Path

from extensions import db

from models import User

from services.auth_service import (
    login_required,
    get_current_user
)



admin_bp = Blueprint(
    "admin",
    __name__
)


@admin_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin_page():

    current_user = get_current_user()

    if current_user.role != "admin":
        flash(
            "Доступ запрещён.",
            "danger"
        )
        return redirect(
            url_for("main.index")
        )

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":

            login = request.form.get(
                "login",
                ""
            ).strip()

            password = request.form.get(
                "password",
                ""
            )

            role = request.form.get(
                "role",
                "analyst"
            )

            if not login or not password:

                flash(
                    "Введите логин и пароль.",
                    "warning"
                )

            elif User.query.filter_by(
                login=login
            ).first():

                flash(
                    "Пользователь уже существует.",
                    "warning"
                )

            else:

                user = User(
                    login=login,
                    role=role
                )

                user.set_password(password)

                db.session.add(user)
                db.session.commit()

                flash(
                    "Пользователь создан.",
                    "success"
                )

            return redirect(
                url_for("admin.admin_page")
            )

        if action == "backup":

            base_dir = Path(__file__).resolve().parent.parent

            db_path = base_dir / "ismds.db"

            backup_dir = base_dir / "backups"

            backup_dir.mkdir(exist_ok=True)

            backup_name = (
                "backup_" +
                datetime.now().strftime("%Y%m%d_%H%M%S") +
                ".db"
            )

            shutil.copy2(
                db_path,
                backup_dir / backup_name
            )

            flash(
                f"Создана резервная копия {backup_name}.",
                "success"
            )

            return redirect(
                url_for("admin.admin_page")
            )


        user_id = request.form.get(
            "user_id",
            type=int
        )

        user = User.query.get(user_id)

        if action == "delete":

            if user is None:

                flash(
                    "Пользователь не найден.",
                    "warning"
                )

            elif user.id == current_user.id:

                flash(
                    "Нельзя удалить самого себя.",
                    "warning"
                )

            elif (
                user.role == "admin"
                and
                User.query.filter_by(
                    role="admin"
                ).count() == 1
            ):

                flash(
                    "Нельзя удалить последнего администратора.",
                    "warning"
                )

            else:

                db.session.delete(user)
                db.session.commit()

                flash(
                    "Пользователь удалён.",
                    "success"
                )

            return redirect(
                url_for("admin.admin_page")
            )

        if user:

            if action == "toggle":

                if user.id == current_user.id:
                    flash(
                        "Нельзя заблокировать самого себя.",
                        "warning"
                    )
                else:
                    user.is_active = not user.is_active
                    db.session.commit()

            elif action == "role":

                if user.role == "admin":
                    user.role = "analyst"
                else:
                    user.role = "admin"

                db.session.commit()

        return redirect(
            url_for("admin.admin_page")
        )

    users = (
        User.query
        .order_by(User.id)
        .all()
    )

    base_dir = Path(__file__).resolve().parent.parent

    backup_dir = base_dir / "backups"

    backups = []

    if backup_dir.exists():

        backups = sorted(
            backup_dir.glob("*.db"),
            reverse=True
        )

    return render_template(
        "admin.html",
        active_page="admin",
        users=users,
        backups=backups
    )

@admin_bp.route("/admin/backup/<filename>")
@login_required
def download_backup(filename):

    current_user = get_current_user()

    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    base_dir = Path(__file__).resolve().parent.parent

    backup_dir = base_dir / "backups"

    return send_from_directory(
        backup_dir,
        filename,
        as_attachment=True
    )