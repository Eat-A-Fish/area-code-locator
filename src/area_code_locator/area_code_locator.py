# area_code_locator.py
from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Tuple, Union, cast
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files  # backport for Py3.8 and earlier

import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform
from pyproj import Transformer


BBox = Tuple[float, float, float, float]


def bbox_of(geom: BaseGeometry) -> BBox:
    minx, miny, maxx, maxy = geom.bounds
    return float(minx), float(miny), float(maxx), float(maxy)


class AreaCodeLocator:
    def __init__(self, path: Optional[str] = None, projected_epsg: int = 5070):
        """
        Initialize the Area Code Locator.

        Args:
            path: Path to a Parquet file containing area code data. If None, uses the included data.
            projected_epsg: EPSG code for projected coordinate system (default: 5070 - NAD83/Conus Albers).
        """
        self._epsg_proj = int(projected_epsg)

        # Use included data if no path provided
        if path is None:
            # Use importlib.resources to access the packaged data file
            data_files = files("area_code_locator.data")
            p = data_files.joinpath("area-codes.parquet")
            # Convert Traversable to string for geopandas
            p = str(p)
        else:
            p = Path(path)

        # Load dataset
        gdf = gpd.read_parquet(p)

        # Ensure WGS84 for point-in-polygon
        if gdf.crs is None:
            gdf = gdf.set_crs(4326)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        # Detect code column
        gdf.columns = [c.lower() for c in gdf.columns]
        code_col: Optional[str] = next((c for c in ("area_code", "areacode", "npa", "code") if c in gdf.columns), None)
        if code_col is None:
            raise RuntimeError(f"No area-code column found. Columns: {list(gdf.columns)}")

        self.code_col: str = code_col
        self.gdf: gpd.GeoDataFrame = gdf
        self.gdf_proj: gpd.GeoDataFrame = gdf.to_crs(epsg=self._epsg_proj)

        # Spatial indexes (touch once so they are built)
        _ = self.gdf.sindex           # type: ignore[attr-defined]
        _ = self.gdf_proj.sindex      # type: ignore[attr-defined]

        # Pure Shapely transformers (no GeoSeries -> avoids Pylance confusion)
        self._to_proj = Transformer.from_crs(4326, self._epsg_proj, always_xy=True)
        self._to_proj_fn = self._to_proj.transform  # callable(x, y) -> (X, Y)

    def _covers_query(self, geom: BaseGeometry) -> List[int]:
        """Return candidate indices whose polygons cover the given geometry (point)."""
        try:
            idx = list(self.gdf.sindex.query(geom, predicate="covers"))  # type: ignore[attr-defined]
            return [int(i) for i in idx]
        except Exception:
            # Fallback: bbox candidates then precise covers filter
            bb = bbox_of(geom)
            try:
                idx_any = list(self.gdf.sindex.query(bb))  # type: ignore[attr-defined]
            except Exception:
                idx_any = list(range(len(self.gdf)))

            out: List[int] = []
            for i in idx_any:
                # Pylance-friendly: explicitly cast to a Shapely geometry
                g_i = self.gdf.geometry.iloc[int(i)]
                g_geom: BaseGeometry = cast(BaseGeometry, g_i)  # tell Pylance this is a geometry
                if g_geom.covers(geom):
                    out.append(int(i))
            return out

    def _intersects_query_proj(self, geom_proj: BaseGeometry) -> List[int]:
        """Return candidate indices (in projected CRS) that intersect the given geometry."""
        try:
            idx = list(self.gdf_proj.sindex.query(geom_proj, predicate="intersects"))  # type: ignore[attr-defined]
            return cast(List[int], idx)
        except Exception:
            bb = bbox_of(geom_proj)
            return cast(List[int], list(self.gdf_proj.sindex.query(bb)))  # type: ignore[attr-defined]

    def lookup(self, lat: float, lon: float, return_all: bool = True) -> Union[str, List[str]]:
        """
        Returns one or more area codes for (lat, lon).
        Order:
          1) exact covers (includes boundary points)
          2) 50 m buffer intersects (projected CRS)
          3) expanding window nearest (25/100/300 km)
        """
        pt: BaseGeometry = Point(float(lon), float(lat))

        # 1) Exact polygon match
        cand_idx = self._covers_query(pt)
        if cand_idx:
            matches = self.gdf.iloc[cand_idx]
            codes = [str(c) for c in matches[self.code_col].unique()]
            return codes if return_all else codes[0]

        # Projected point as pure Shapely geometry
        pt_proj: BaseGeometry = transform(self._to_proj_fn, pt)

        # 2) Border fudge: 50 m buffer (projected) and intersects
        ring50: BaseGeometry = pt_proj.buffer(50.0)
        cand2_idx = self._intersects_query_proj(ring50)
        if cand2_idx:
            proj_slice = self.gdf_proj.iloc[cand2_idx]
            mask = proj_slice.geometry.intersects(ring50)
            if bool(mask.any()):
                idxs = proj_slice[mask].index
                codes = [str(c) for c in self.gdf.loc[idxs, self.code_col].unique()]
                return codes if return_all else codes[0]

        # 3) Nearest via expanding search windows (meters)
        for meters in (25_000.0, 100_000.0, 300_000.0):
            ring: BaseGeometry = pt_proj.buffer(meters)
            bb = bbox_of(ring)
            try:
                cand_idx3 = list(self.gdf_proj.sindex.query(bb))  # type: ignore[attr-defined]
            except Exception:
                cand_idx3 = []
            if cand_idx3:
                proj_cand = self.gdf_proj.iloc[cand_idx3].copy()
                # Distance to the projected point (meters)
                proj_cand["__d__"] = proj_cand.geometry.distance(pt_proj)
                hit = cast(int, proj_cand["__d__"].idxmin())
                return [str(self.gdf.loc[hit, self.code_col])]

        # Ultra-fallback (should almost never happen)
        proj_all = self.gdf_proj.copy()
        proj_all["__d__"] = proj_all.geometry.distance(pt_proj)
        hit = cast(int, proj_all["__d__"].idxmin())
        return [str(self.gdf.loc[hit, self.code_col])]
