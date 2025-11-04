import threading
from functools import lru_cache
from typing import List, Union, Optional

from .area_code_locator import AreaCodeLocator

__version__ = "0.2.0"
__all__ = ["AreaCodeLocator", "lookup", "batch_lookup"]

# Thread-safe lazy singleton for the locator
_locator_instance: Optional[AreaCodeLocator] = None
_locator_lock = threading.Lock()


def _get_locator() -> AreaCodeLocator:
    """Get or create the singleton AreaCodeLocator instance."""
    global _locator_instance
    if _locator_instance is None:
        with _locator_lock:
            if _locator_instance is None:
                _locator_instance = AreaCodeLocator()
    return _locator_instance


def lookup(lat: float, lon: float, return_all: bool = True) -> Union[str, List[str]]:
    """
    Look up area code(s) for a given latitude and longitude.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        return_all: If True, return all overlapping area codes. If False, return only the first.

    Returns:
        Area code(s) as string or list of strings
    """
    return _lookup_cached(lat, lon, return_all)


@lru_cache(maxsize=100_000)
def _lookup_cached(lat: float, lon: float, return_all: bool) -> Union[str, List[str]]:
    """Cached wrapper for the locator lookup."""
    return _get_locator().lookup(lat=lat, lon=lon, return_all=return_all)


def batch_lookup(points: List[tuple[float, float]], return_all: bool = True) -> List[Union[str, List[str]]]:
    """
    Look up area codes for multiple latitude/longitude points.

    Args:
        points: List of (lat, lon) tuples
        return_all: If True, return all overlapping area codes for each point.
                   If False, return only the first area code for each point.

    Returns:
        List of area code results, one per input point
    """
    locator = _get_locator()
    return [locator.lookup(lat, lon, return_all) for lat, lon in points]