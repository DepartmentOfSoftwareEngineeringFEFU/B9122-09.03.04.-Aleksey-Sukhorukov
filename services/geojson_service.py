import json

from pathlib import Path

from shapely.geometry import shape


class GeoJSONService:

    _geojson_cache = None

    _polygon_cache = None

    @staticmethod
    def load_geojson():

        if GeoJSONService._geojson_cache is not None:
            return GeoJSONService._geojson_cache

        base_dir = Path(__file__).resolve().parent.parent

        geojson_path = (
            base_dir /
            "data" /
            "mainland.geojson"
        )

        with open(
            geojson_path,
            "r",
            encoding="utf-8"
        ) as f:

            GeoJSONService._geojson_cache = json.load(f)

        return GeoJSONService._geojson_cache

    @staticmethod
    def get_land_polygons():

        if GeoJSONService._polygon_cache is not None:
            return GeoJSONService._polygon_cache

        geojson_data = (
            GeoJSONService.load_geojson()
        )

        polygons = []

        for feature in geojson_data["features"]:

            geometry = feature.get("geometry")

            if geometry:
                polygons.append(
                    shape(geometry)
                )

        GeoJSONService._polygon_cache = polygons

        return polygons

