
from collections import defaultdict
from math import radians, cos, sin, sqrt, atan2
from sklearn.preprocessing import StandardScaler

import numpy as np
from sklearn.cluster import DBSCAN

from models.ais import TrackPoint
from models import Vessel


class TrajectoryClusterService:

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1))
            * cos(radians(lat2))
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    @staticmethod
    def build_trajectory_features(session_id):

        points = (
            TrackPoint.query
            .filter_by(session_id=session_id)
            .order_by(
                TrackPoint.vessel_id,
                TrackPoint.timestamp
            )
            .all()
        )

        vessel_tracks = defaultdict(list)

        for point in points:
            vessel_tracks[point.vessel_id].append(point)

        features = []
        vessel_ids = []

        for vessel_id, track in vessel_tracks.items():

            if len(track) < 2:
                continue

            start = track[0]
            end = track[-1]

            total_distance = 0

            for i in range(len(track) - 1):

                p1 = track[i]
                p2 = track[i + 1]

                total_distance += (
                    TrajectoryClusterService.haversine(
                        p1.lat,
                        p1.lon,
                        p2.lat,
                        p2.lon
                    )
                )

            speeds = [
                p.sog
                for p in track
                if p.sog is not None
            ]

            avg_speed = np.mean(speeds) if speeds else 0

            courses = [
                p.cog
                for p in track
                if p.cog is not None
            ]

            avg_course = np.mean(courses) if courses else 0

            point_count = len(track)

            feature_vector = [
                start.lat,
                start.lon,
                end.lat,
                end.lon,
                avg_speed,
                avg_course,
                total_distance,
                point_count
            ]

            features.append(feature_vector)
            vessel_ids.append(vessel_id)

            print("Количество судов:", len(vessel_tracks))
            print("Количество признаков:", len(features))
            print("Vessel IDs:", vessel_ids)

        return np.array(features), vessel_ids

    @staticmethod
    def build_cluster_tracks(session_id, labels, vessel_ids):
        cluster_tracks = {}

        for vessel_id, cluster_id in zip(vessel_ids, labels):
            if cluster_id == -1:
                continue

            cluster_id = int(cluster_id)

            if cluster_id in cluster_tracks:
                cluster_tracks[cluster_id]["vessels"].append(vessel_id)
                continue

            points = (
                TrackPoint.query
                .filter_by(
                    session_id=session_id,
                    vessel_id=vessel_id
                )
                .order_by(TrackPoint.timestamp)
                .all()
            )

            if not points:
                continue

            avg_speed = np.mean(
                [p.sog for p in points if p.sog is not None]
            )

            total_distance = 0

            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]

                total_distance += (
                    TrajectoryClusterService.haversine(
                        p1.lat,
                        p1.lon,
                        p2.lat,
                        p2.lon
                    )
                )

            cluster_tracks[int(cluster_id)] = {
                "vessels": [vessel_id],
                "track": [
                    {
                        "lat": p.lat,
                        "lon": p.lon,
                        "timestamp": p.timestamp.isoformat()
                    }
                    for p in points
                ],
                "avg_speed": float(avg_speed) if not np.isnan(avg_speed) else 0,
                "length": float(total_distance)
            }

        return cluster_tracks

    @staticmethod
    def cluster_trajectories(
        session_id,
        eps=2.5,
        min_samples=2
    ):

        features, vessel_ids = (
            TrajectoryClusterService
            .build_trajectory_features(session_id)
        )

        if len(features) == 0:
            return []

        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        model = DBSCAN(
            eps=eps,
            min_samples=min_samples
        )

        labels = model.fit_predict(features_scaled)

        cluster_tracks = (
            TrajectoryClusterService.build_cluster_tracks(
                session_id,
                labels,
                vessel_ids
            )
        )

        cluster_count = len(set(labels)) - (1 if -1 in labels else 0)
        anomaly_count = list(labels).count(-1)

        results = []

        for vessel_id, cluster_id in zip(vessel_ids, labels):
            vessel = Vessel.query.get(vessel_id)

            results.append({
                "vessel_id": int(vessel_id),
                "vessel_number": vessel.number if vessel else None,
                "cluster": int(cluster_id),
                "is_anomaly": bool(cluster_id == -1)
            })

        return {
            "clusters": results,
            "cluster_tracks": cluster_tracks,
            "cluster_count": int(cluster_count),
            "anomaly_count": int(anomaly_count)
        }

