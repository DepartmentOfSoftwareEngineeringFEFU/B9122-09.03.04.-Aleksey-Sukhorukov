
from flask import Blueprint, jsonify

from services.auth_service import login_required
from services.clustering_service import (
    TrajectoryClusterService
)

clustering_bp = Blueprint(
    "clustering",
    __name__
)


@clustering_bp.route(
    "/api/clusters/<int:session_id>"
)
@login_required
def get_clusters(session_id):

    result = TrajectoryClusterService.cluster_trajectories(session_id)

    return jsonify(result)

