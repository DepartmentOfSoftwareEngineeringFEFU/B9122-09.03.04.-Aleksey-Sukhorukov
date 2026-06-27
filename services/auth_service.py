from functools import wraps

from flask import (
    session,
    flash,
    redirect,
    url_for
)

from models import User


def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return User.query.get(user_id)


def login_required(view):

    @wraps(view)
    def wrapper(*args, **kwargs):

        if not session.get("user_id"):
            flash(
                "Необходимо войти в систему.",
                "warning"
            )
            return redirect(url_for("auth.login"))
        user = User.query.get(session.get("user_id"))

        if user is None:
            session.clear()
            return redirect(url_for("auth.login"))

        if not user.is_active:
            session.clear()
            flash(
                "Учётная запись заблокирована.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapper