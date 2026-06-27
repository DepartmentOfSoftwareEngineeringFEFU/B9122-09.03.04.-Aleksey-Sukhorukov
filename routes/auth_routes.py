from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from extensions import db
from models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(
            login=login_value
        ).first()

        if user and user.check_password(password):

            session["user_id"] = user.id

            flash(
                "Вы успешно вошли в систему.",
                "success"
            )


            return redirect(
                url_for("results.results_page")
            )


        flash(
            "Неверный логин или пароль.",
            "danger"
        )

    return render_template(
        "login.html"
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        login_value = request.form.get(
            "login",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        password2 = request.form.get(
            "password2",
            ""
        )

        if not login_value or not password:

            flash(
                "Логин и пароль не могут быть пустыми.",
                "warning"
            )

        elif password != password2:

            flash(
                "Пароль и подтверждение не совпадают.",
                "warning"
            )

        elif User.query.filter_by(
            login=login_value
        ).first():

            flash(
                "Пользователь с таким логином уже существует.",
                "warning"
            )

        else:

            user = User(
                login=login_value,
                role="analyst"
            )

            user.set_password(password)

            db.session.add(user)

            db.session.commit()

            flash(
                "Регистрация успешно завершена.",
                "success"
            )

            return redirect(
                url_for("auth.login")
            )

    return render_template(
        "register.html"
    )


@auth_bp.route("/logout")
def logout():

    session.pop(
        "user_id",
        None
    )

    flash(
        "Вы вышли из системы.",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )