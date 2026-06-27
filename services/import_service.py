import csv
import os
from datetime import datetime

from flask import current_app, flash

from extensions import db

from models import (
    AISSession,
    Vessel,
    TrackPoint
)

from services.auth_service import get_current_user


def parse_timestamp(ts):

    ts = ts.strip()

    if not ts:
        return None

    ts = ts.replace("Z", "")

    formats = (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S"
    )

    for fmt in formats:

        try:
            return datetime.strptime(ts, fmt)

        except ValueError:
            pass

    return None


def process_import(
        uploaded_file,
        action,
        file_format,
        aquatory_id,
        secure_filename_func
):
    """
    Выполняет проверку либо импорт CSV.

    Возвращает словарь statistics
    либо None при ошибке.
    """

    if not uploaded_file or uploaded_file.filename == "":

        flash(
            "Не выбран файл для импорта.",
            "warning"
        )

        return None

    filename = secure_filename_func(
        uploaded_file.filename
    )

    #
    # временный или постоянный файл
    #

    if action == "check":

        stored_name = None

        path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            "_tmp_" + filename
        )

    else:

        stored_name = (
            datetime.utcnow().strftime(
                "%Y%m%d_%H%M%S_"
            )
            + filename
        )

        path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            stored_name
        )

    uploaded_file.save(path)

    total = 0
    valid = 0
    invalid = 0

    min_time = None
    max_time = None

    try:

        with open(
                path,
                newline="",
                encoding="utf-8"
        ) as f:

            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError(
                    "В файле отсутствует заголовок."
                )

            required = [
                "mmsi",
                "timestamp",
                "lat",
                "lon"
            ]

            for col in required:

                if col not in reader.fieldnames:
                    raise ValueError(
                        f"Отсутствует столбец '{col}'."
                    )

            #
            # Только проверка
            #

            if action == "check":

                for row in reader:

                    total += 1

                    ts = parse_timestamp(
                        row["timestamp"]
                    )

                    if ts:

                        valid += 1

                        if (
                                min_time is None
                                or
                                ts < min_time
                        ):
                            min_time = ts

                        if (
                                max_time is None
                                or
                                ts > max_time
                        ):
                            max_time = ts

                    else:

                        invalid += 1

            #
            # Импорт
            #

            else:

                current_user = get_current_user()

                session_record = AISSession(

                    user_id=current_user.id,

                    aquatory_id=aquatory_id,

                    original_filename=filename,

                    stored_filename=stored_name,

                    file_format=file_format

                )

                db.session.add(
                    session_record
                )

                db.session.flush()

                for row in reader:

                    total += 1

                    ts = parse_timestamp(
                        row["timestamp"]
                    )

                    if ts:

                        valid += 1

                        if (
                                min_time is None
                                or
                                ts < min_time
                        ):
                            min_time = ts

                        if (
                                max_time is None
                                or
                                ts > max_time
                        ):
                            max_time = ts

                    else:

                        invalid += 1

                    number = row["mmsi"].strip()

                    vessel = Vessel.query.filter_by(
                        number=number
                    ).first()

                    if vessel is None:

                        vessel = Vessel(
                            number=number
                        )

                        db.session.add(vessel)

                        db.session.flush()

                    try:

                        lat = float(
                            row["lat"]
                        )

                        lon = float(
                            row["lon"]
                        )

                    except ValueError:

                        invalid += 1
                        continue

                    sog = None

                    if (
                            "sog" in row
                            and
                            row["sog"].strip()
                    ):

                        try:
                            sog = float(
                                row["sog"]
                            )
                        except ValueError:
                            pass

                    cog = None

                    if (
                            "cog" in row
                            and
                            row["cog"].strip()
                    ):

                        try:
                            cog = float(
                                row["cog"]
                            )
                        except ValueError:
                            pass

                    point = TrackPoint(

                        session_id=session_record.id,

                        vessel_id=vessel.id,

                        timestamp=ts or datetime.utcnow(),

                        lat=lat,

                        lon=lon,

                        sog=sog,

                        cog=cog

                    )

                    db.session.add(point)

                session_record.total_records = total
                session_record.time_start = min_time
                session_record.time_end = max_time

                db.session.commit()

                flash(
                    f"Импорт выполнен. Создана сессия № {session_record.id}.",
                    "success"
                )

    except Exception as e:

        flash(
            f"Ошибка при чтении файла: {e}",
            "danger"
        )

        return None

    finally:

        if (
                action == "check"
                and
                os.path.exists(path)
        ):
            os.remove(path)

    return {

        "total": total,

        "valid": valid,

        "invalid": invalid,

        "period": (
            f"{min_time} — {max_time}"
            if min_time and max_time
            else None
        )

    }