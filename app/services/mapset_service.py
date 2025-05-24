import json
import math
import os
from typing import Any, Dict, List, Optional, Tuple

import httpx
import numpy as np
from colour import Color
from fastapi import HTTPException, status
from shapely.geometry import Point, shape
from sqlalchemy import or_
from uuid6 import UUID

from app.core.exceptions import UnprocessableEntity
from app.models import MapsetModel
from app.models.organization_model import OrganizationModel
from app.repositories import (
    MapsetHistoryRepository,
    MapsetRepository,
    SourceUsageRepository,
)
from app.schemas.user_schema import UserSchema

from . import BaseService


class MapsetService(BaseService[MapsetModel]):
    def __init__(
        self,
        repository: MapsetRepository,
        history_repository: MapsetHistoryRepository,
        source_usage_repository: SourceUsageRepository,
    ):
        super().__init__(MapsetModel, repository)
        self.repository = repository
        self.history_repository = history_repository
        self.source_usage_repository = source_usage_repository

    async def find_all(
        self,
        user: UserSchema,
        filters: str | List[str],
        sort: str | List[str],
        search: str = "",
        group_by: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[MapsetModel] | int]:
        list_model_filters = []
        list_sort = []

        if isinstance(filters, str):
            filters = [filters]

        filters.append("is_deleted=false")

        for filter_item in filters:
            if isinstance(filter_item, list):
                or_filter = []
                for values in filter_item:
                    try:
                        col, value = values.split("=")
                    except ValueError:
                        raise UnprocessableEntity(
                            f"Invalid filter {filter_item} must be 'name=value' or '[[name=value],[name=value]]'"
                        )

                    if not hasattr(self.model_class, col):
                        raise UnprocessableEntity(f"Invalid filter column: {col}")

                    if col == "id":
                        try:
                            value = UUID(value)
                        except:
                            raise UnprocessableEntity(f"Invalid filter value {value}, please provide UUID")

                    if isinstance(value, str) and value.lower() in {"true", "false", "t", "f"}:
                        value = value.lower() in {"true", "t"}

                    or_filter.append(getattr(self.model_class, col) == value)
                list_model_filters.append(or_(*or_filter))
                continue

            try:
                col, value = filter_item.split("=")
            except ValueError:
                raise UnprocessableEntity(
                    f"Invalid filter {filter_item} must be 'name=value' or '[[name=value],[name=value]]'"
                )

            if not hasattr(self.model_class, col):
                raise UnprocessableEntity(f"Invalid filter column: {col}")

            if col == "id":
                try:
                    value = UUID(value)
                except:
                    raise UnprocessableEntity(f"Invalid filter value {value}, please provide UUID")

            if isinstance(value, str) and value.lower() in {"true", "false", "t", "f"}:
                value = value.lower() in {"true", "t"}
                list_model_filters.append(getattr(self.model_class, col).is_(value))
            else:
                list_model_filters.append(getattr(self.model_class, col) == value)

        if isinstance(sort, str):
            sort = [sort]

        for sort_item in sort:
            try:
                col, order = sort_item.split(":")
            except ValueError:
                raise UnprocessableEntity(f"Invalid sort {sort_item}. Must be 'name:asc' or 'name:desc'")

            if not hasattr(self.model_class, col):
                raise UnprocessableEntity(f"Invalid sort column: {col}")

            if order.lower() == "asc":
                list_sort.append(getattr(self.model_class, col).asc())
            elif order.lower() == "desc":
                list_sort.append(getattr(self.model_class, col).desc())
            else:
                raise UnprocessableEntity(f"Invalid sort order '{order}' for {col}")

        return await self.repository.find_all(user, list_model_filters, list_sort, search, group_by, limit, offset)

    async def find_all_group_by_organization(
        self,
        user: Optional[UserSchema] = None,
        filters: Optional[list[str]] = None,
        sort: Optional[list[str]] = None,
        search: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Dict], int]:
        """
        Find organizations with filtered mapsets.
        Only returns the mapsets that match the filter for each organization.
        """
        mapset_filters = []
        organization_filters = []
        list_sort = []

        filters = filters or []

        if isinstance(filters, str):
            filters = [filters]

        filters.append("is_deleted=false")

        for filter_str in filters:
            if isinstance(filter_str, list):
                mapset_or_conditions = []
                org_or_conditions = []

                for value_str in filter_str:
                    col, value = value_str.split("=")
                    if hasattr(MapsetModel, col):
                        if value.lower() in {"true", "false", "t", "f"}:
                            value = value.lower() in {"true", "t"}
                        mapset_or_conditions.append(getattr(MapsetModel, col) == value)
                    elif hasattr(OrganizationModel, col):
                        if value.lower() in {"true", "false", "t", "f"}:
                            value = value.lower() in {"true", "t"}
                        org_or_conditions.append(getattr(OrganizationModel, col) == value)
                    else:
                        raise UnprocessableEntity(f"Invalid filter column: {col}")

                if mapset_or_conditions:
                    mapset_filters.append(or_(*mapset_or_conditions))
                if org_or_conditions:
                    organization_filters.append(or_(*org_or_conditions))
                continue

            try:
                col, value = filter_str.split("=")

                # Konversi nilai boolean jika perlu
                if value.lower() in {"true", "false", "t", "f"}:
                    value = value.lower() in {"true", "t"}

                # Tambahkan filter ke daftar yang sesuai
                if hasattr(MapsetModel, col):
                    mapset_filters.append(getattr(MapsetModel, col) == value)
                elif hasattr(OrganizationModel, col):
                    organization_filters.append(getattr(OrganizationModel, col) == value)
                else:
                    raise UnprocessableEntity(f"Invalid filter column: {col}")
            except ValueError:
                raise UnprocessableEntity(f"Invalid filter format: {filter_str}")

        if isinstance(sort, str):
            sort = [sort]

        for sort_str in sort or []:
            try:
                col, order = sort_str.split(":")

                if hasattr(OrganizationModel, col):
                    sort_col = getattr(OrganizationModel, col)
                elif hasattr(MapsetModel, col):
                    # Untuk sort berdasarkan atribut mapset, kita perlu subquery
                    # Ini tidak diimplementasi di sini untuk menjaga kesederhanaan
                    # Namun Anda bisa mengembangkannya jika diperlukan
                    # continue
                    sort_col = getattr(MapsetModel, col)
                else:
                    raise UnprocessableEntity(f"Invalid sort column: {col}")

                if order.lower() == "asc":
                    list_sort.append(sort_col.asc())
                elif order.lower() == "desc":
                    list_sort.append(sort_col.desc())
                else:
                    raise UnprocessableEntity(f"Invalid sort order: {order}")
            except ValueError:
                raise UnprocessableEntity(f"Invalid sort format: {sort_str}")

        if not list_sort:
            list_sort = [OrganizationModel.name.asc()]

        return await self.repository.find_all_group_by_organization(
            user=user,
            mapset_filters=mapset_filters,
            organization_filters=organization_filters,
            sort=list_sort,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def create(self, user: UserSchema, data: Dict[str, Any]) -> MapsetModel:
        data["created_by"] = user.id
        data["updated_by"] = user.id

        track_note = data.pop("notes", None)
        source_id = data.pop("source_id", None)

        mapset = await super().create(data)

        if source_id:
            list_source_usage = []
            if isinstance(source_id, str) or isinstance(source_id, UUID):
                source_id = [source_id]

            for id in source_id:
                list_source_usage.append({"mapset_id": mapset.id, "source_id": id})

            await self.source_usage_repository.bulk_create(list_source_usage)

        await self.history_repository.create(
            {
                "mapset_id": mapset.id,
                "validation_type": mapset.status_validation,
                "notes": track_note,
                "user_id": user.id,
            }
        )

        return mapset

    async def update(self, id: UUID, user: UserSchema, data: Dict[str, Any]) -> MapsetModel:
        data["updated_by"] = user.id
        track_note = data.pop("notes", None)
        source_id = data.pop("source_id", None)

        mapset = await super().update(id, data)

        if source_id:
            list_source_usage = []
            if isinstance(source_id, str) or isinstance(source_id, UUID):
                source_id = [source_id]

            for id in source_id:
                list_source_usage.append({"mapset_id": mapset.id, "source_id": id})

            await self.source_usage_repository.bulk_update(mapset.id, list_source_usage)

        await self.history_repository.create(
            {
                "mapset_id": mapset.id,
                "validation_type": mapset.status_validation,
                "notes": track_note,
                "user_id": user.id,
            }
        )

        return mapset

    async def bulk_update_activation(self, mapset_ids: List[UUID], is_active: bool) -> None:
        await self.repository.bulk_update_activation(mapset_ids, is_active)

    async def calculate_choropleth(
        self, geojson_data: Dict, boundary_name: str = "jatim.json", coordinate_field: str = "coordinates"
    ) -> List[Dict]:
        """
        Menghitung data choropleth berdasarkan jumlah titik dalam poligon.

        Args:
            geojson_data: GeoJSON data yang berisi titik-titik
            boundary_name: Nama file boundary GeoJSON di dalam folder assets
            coordinate_field: Nama field yang berisi koordinat di dalam geometri

        Returns:
            List[Dict]: Data choropleth untuk setiap poligon dengan jumlah titik
        """
        if not geojson_data or not isinstance(geojson_data, dict) or "features" not in geojson_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid GeoJSON data format")

        features = geojson_data.get("features", [])

        boundary_geojson = self._load_boundary_geojson(boundary_name)
        polygon_features = boundary_geojson.get("features", [])

        choropleth_data = []

        for polygon in polygon_features:
            value = 0
            polygon_shape = shape(polygon["geometry"])

            for feature in features:
                if feature.get("geometry", {}).get("type") == "Point" and coordinate_field in feature.get(
                    "geometry", {}
                ):
                    coords = feature["geometry"]["coordinates"]
                    if len(coords) >= 2:
                        point = Point(coords[0], coords[1])

                        if polygon_shape.contains(point):
                            value += 1

            choropleth_data.append({**polygon["properties"], "value": value})

        return choropleth_data

    async def generate_colorscale(
        self, geojson_source: str, color_range: List[str] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate color scale untuk data choropleth.

        Args:
            geojson_source: geojson_source url menuju data choropleth
            color_range: Rentang warna yang akan digunakan

        Returns:
            Tuple[List[Dict], List[Dict]]:
                - Data choropleth dengan warna
                - Color scale untuk legenda
        """

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(geojson_source)
            geojson_data = response.json()

        choropleth_data = await self.calculate_choropleth(geojson_data)
        if not color_range:
            color_range = ["#ddffed", "#006430"]

        arr_tobe_percentile = []
        for row in choropleth_data:
            arr_tobe_percentile.append(row["value"])

        arr_tobe_percentile.sort()
        arr_tobe_percentile = list(filter(lambda num: num != 0, arr_tobe_percentile))

        count = 5
        is_duplicate = False
        arr_percentile = []

        if len(arr_tobe_percentile) > 1:
            while count >= 1:
                diff = 100 / count
                arr_percentile = []

                for j in range(count + 1):
                    perc = math.ceil(np.percentile(arr_tobe_percentile, j * diff))
                    arr_percentile.append(perc)

                is_duplicate = self._check_if_duplicates(arr_percentile)
                if is_duplicate:
                    count = count - 1
                    arr_tobe_percentile = arr_percentile.copy()
                else:
                    break
        elif len(arr_tobe_percentile) == 1:
            arr_percentile = arr_tobe_percentile
        else:
            pass

        if len(arr_percentile) > 1:
            colors = list(Color(color_range[0]).range_to(Color(color_range[1]), len(arr_percentile) - 1))

            rangelist = []
            rangelist.append({"from": 0, "to": 0, "color": "#FFFFFFFF", "total_cluster": 0})

            for i in range(len(arr_percentile) - 1):
                if i == 0:
                    rangelist.append(
                        {
                            "from": arr_percentile[i],
                            "to": arr_percentile[i + 1],
                            "color": colors[i].hex,
                            "total_cluster": 0,
                        }
                    )
                else:
                    rangelist.append(
                        {
                            "from": arr_percentile[i] + 1,
                            "to": arr_percentile[i + 1],
                            "color": colors[i].hex,
                            "total_cluster": 0,
                        }
                    )
        elif len(arr_percentile) == 1:
            colors = list(Color(color_range[0]).range_to(Color(color_range[1]), 1))

            rangelist = []
            rangelist.append({"from": 0, "to": 0, "color": "#FFFFFFFF", "total_cluster": 0})
            rangelist.append(
                {"from": arr_percentile[0], "to": arr_percentile[0], "color": colors[0].hex, "total_cluster": 0}
            )
        else:
            rangelist = []
            rangelist.append({"from": 0, "to": 0, "color": "#FFFFFFFF", "total_cluster": 0})

        result = []
        for item in choropleth_data:
            temp = item.copy()

            for range_item in rangelist:
                if temp["value"] >= range_item["from"] and temp["value"] <= range_item["to"]:
                    temp["color"] = range_item["color"]
                    range_item["total_cluster"] += 1

            result.append(temp)

        return result, rangelist

    def _load_boundary_geojson(self, boundary_filename: str) -> Dict:
        try:
            boundary_path = os.path.join("assets", boundary_filename)

            if not os.path.exists(boundary_path):
                raise FileNotFoundError(f"File boundary tidak ditemukan: {boundary_path}")

            with open(boundary_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gagal membaca file boundary: {str(e)}"
            )
