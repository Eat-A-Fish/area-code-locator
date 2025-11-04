# NANP Area Code Locator

[![PyPI version](https://img.shields.io/pypi/v/area-code-locator.svg)](https://pypi.org/project/area-code-locator/)
[![Python versions](https://img.shields.io/pypi/pyversions/area-code-locator.svg)](https://pypi.org/project/area-code-locator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Reverse-geocode latitude/longitude to **NANP** telephone **area codes**. Works offline; ships a compact Parquet of polygons.

---

## ✨ Features
- 🔎 **Reverse-geocode** `(lat, lon)` → area code(s)
- ⚡ **Fast local lookups** (vectorized GeoPandas + spatial index)
- 🪪 **NANP coverage** (US, Canada, participating Caribbean)
- 🧳 **Zero setup** — packaged Parquet data included (~29 MB)
- 🧭 **CRS handled automatically** (WGS84 in / projected out as needed)
- 🧵 **Simple API & CLI** (`lookup()` and `area-code-lookup`)

---

## 📦 Install

```bash
pip install area-code-locator

# From source:
git clone https://github.com/Eat-A-Fish/area-code-locator.git
cd area-code-locator
pip install -e .
```

---

## 🚀 Quickstart

```python
from area_code_locator import lookup, batch_lookup

# Single point (returns all matching/overlay codes by default)
codes = lookup(40.7128, -74.0060)      # NYC
print(codes)                           # -> ['212', '646', '917', ...]

# First/primary only
code = lookup(34.0522, -118.2437, return_all=False)  # LA
print(code)                              # -> '213'

# Batch
points = [(40.7128, -74.0060), (41.8781, -87.6298)]
print(batch_lookup(points))              # -> [['212', ...], ['312', ...]]
```

---

## 🖥️ CLI

```bash
area-code-lookup --lat 40.7128 --lon -74.0060
# -> 917

area-code-lookup --lat 40.7128 --lon -74.0060 --all
# -> ["212", "646", "917", ...]
```

---

## 🧪 API

```python
lookup(lat: float, lon: float, return_all: bool = True) -> Union[str, List[str]]
batch_lookup(points: List[Tuple[float, float]], return_all: bool = True) -> List[Union[str, List[str]]]
```

- `return_all=True` → all matching/overlay area codes
- `return_all=False` → first/primary area code

### Advanced

```python
from area_code_locator import AreaCodeLocator

loc = AreaCodeLocator()                       # uses bundled data
loc_custom = AreaCodeLocator("path/to/area-codes.parquet")
loc.lookup(40.7128, -74.0060, return_all=True)
```

---

## 🗺️ Data

The package includes a preprocessed Parquet file of area-code polygons, so no setup is required.

### Using your own data:
- Parquet with a polygon geometry column
- An area-code column named one of: `area_code`, `areacode`, `npa`, or `code`
- CRS: EPSG:4326 (WGS84)

---

## 🛠️ Development

```bash
pip install -e ".[dev]"
pytest
```

---

## 🙏 Acknowledgments

Area-code boundaries derived from public NANP datasets (e.g., projects compiling NANP polygons). Thanks to the open geospatial community for GeoPandas/Shapely/PyProj.

---

## 📄 License

MIT © Area Code Locator Contributors