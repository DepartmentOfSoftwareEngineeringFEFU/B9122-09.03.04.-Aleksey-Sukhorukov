from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from extensions import db
from services.simulation_service import run_simulation

from models import (
    Scenario,
    ScenarioVessel,
    SimRun,
    SimPoint,
    MetricValue,
    Aquatory,
    TrafficLevel,
    ModelConfig
)

from services.auth_service import login_required


simulation_bp = Blueprint(
    "simulation",
    __name__
)


def parse_datetime_local(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%dT%H:%M"
        )
    except ValueError:
        return None


@simulation_bp.route("/scenarios", methods=["GET", "POST"])
@login_required
def scenarios_page():

    edit_id = request.args.get(
        "edit_id",
        type=int
    )

    edit_scenario = None

    if edit_id:
        edit_scenario = Scenario.query.get(edit_id)

    if request.method == "POST":

        action = request.form.get("action")

        if action == "create":

            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()

            aquatory_id = request.form.get("aquatory_id", type=int)
            model_id = request.form.get("model_id", type=int)
            level_id = request.form.get("level_id", type=int)

            start_time = parse_datetime_local(
                request.form.get("start_time")
            )

            end_time = parse_datetime_local(
                request.form.get("end_time")
            )

            if not name:
                flash("Введите название сценария.", "warning")

            elif not aquatory_id or not model_id or not level_id:
                flash("Заполните обязательные поля сценария.", "warning")

            else:
                scenario = Scenario(
                    name=name,
                    description=description,
                    aquatory_id=aquatory_id,
                    model_id=model_id,
                    level_id=level_id,
                    start_time=start_time,
                    end_time=end_time
                )

                db.session.add(scenario)
                db.session.commit()

                flash("Сценарий создан.", "success")

                return redirect(
                    url_for("simulation.scenarios_page")
                )

        elif action == "update":

            scenario_id = request.form.get("scenario_id", type=int)
            scenario = Scenario.query.get(scenario_id)

            if not scenario:
                flash("Сценарий не найден.", "warning")

            else:
                scenario.name = request.form.get("name", "").strip()
                scenario.description = request.form.get("description", "").strip()
                scenario.aquatory_id = request.form.get("aquatory_id", type=int)
                scenario.model_id = request.form.get("model_id", type=int)
                scenario.level_id = request.form.get("level_id", type=int)
                scenario.start_time = parse_datetime_local(
                    request.form.get("start_time")
                )
                scenario.end_time = parse_datetime_local(
                    request.form.get("end_time")
                )

                db.session.commit()

                flash("Сценарий обновлён.", "success")

                return redirect(
                    url_for("simulation.scenarios_page")
                )


        elif action == "delete":

            scenario_id = request.form.get("scenario_id", type=int)

            scenario = Scenario.query.get(scenario_id)

            if scenario:

                # Удаляем все запуски моделирования

                for run in scenario.runs:
                    # Удаляем точки моделирования

                    SimPoint.query.filter_by(

                        run_id=run.id

                    ).delete()

                    # Удаляем рассчитанные показатели

                    MetricValue.query.filter_by(

                        run_id=run.id

                    ).delete()

                # Удаляем сами запуски

                SimRun.query.filter_by(

                    scenario_id=scenario.id

                ).delete()

                # Удаляем суда сценария

                ScenarioVessel.query.filter_by(

                    scenario_id=scenario.id

                ).delete()

                # Удаляем сценарий

                db.session.delete(scenario)

                db.session.commit()

                flash(

                    "Сценарий удалён.",

                    "info"

                )

            return redirect(

                url_for("simulation.scenarios_page")

            )

    scenarios = (
        Scenario.query
        .order_by(Scenario.created_at.desc())
        .all()
    )

    aquatories = Aquatory.query.all()
    traffic_levels = TrafficLevel.query.all()
    model_configs = ModelConfig.query.all()

    return render_template(
        "scenarios.html",
        active_page="scenarios",
        scenarios=scenarios,
        aquatories=aquatories,
        traffic_levels=traffic_levels,
        model_configs=model_configs,
        edit_scenario=edit_scenario
    )


#@simulation_bp.route("/simulation")
#@login_required
@simulation_bp.route("/simulation", methods=["GET", "POST"])
@login_required
def simulation_page():

    if request.method == "POST":

        scenario_id = request.form.get(
            "scenario_id",
            type=int
        )

        if not scenario_id:

            flash(
                "Выберите сценарий.",
                "warning"
            )

        else:

            run = run_simulation(scenario_id)

            flash(
                f"Моделирование завершено. Запуск № {run.id}.",
                "success"
            )

            return redirect(
                url_for("simulation.simulation_page")
            )

    scenarios = (
        Scenario.query
        .order_by(
            Scenario.created_at.desc()
        )
        .all()
    )

    runs = (
        SimRun.query
        .order_by(
            SimRun.start_time.desc()
        )
        .all()
    )

    return render_template(
        "simulation.html",
        active_page="simulation",
        scenarios=scenarios,
        runs=runs
    )