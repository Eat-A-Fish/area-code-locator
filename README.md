# Area Code Locator

A Python library for locating area codes (NPAs) from latitude and longitude coordinates using geospatial data.

## Features

- Fast area code lookup from geographic coordinates
- Supports Parquet format for efficient data storage
- Handles boundary cases with buffer searches
- Uses spatial indexing for performance
- Automatic coordinate system handling

## Installation

Install from source:

```bash
git clone https://github.com/yourusername/area-code-locator.git
cd area-code-locator
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- GeoPandas
- Shapely
- PyProj
- PyArrow (for Parquet file support)

## Data Setup

The library comes with pre-processed area code boundary data, so **no setup is required**! The `area-codes.parquet` file (29MB) is included in the repository and contains comprehensive North American area code boundaries.

### Data Source

The area code data is derived from the [nanp-boundaries](https://github.com/1ec5/nanp-boundaries) project by Elijah Verdoorn, which provides authoritative GeoJSON boundaries for North American Numbering Plan (NANP) area codes.

### Using Custom Data

If you prefer to use your own area code data source:

1. Obtain a Parquet file containing area code polygons
2. Ensure it has:
   - A geometry column with polygon data
   - An area code column (named `area_code`, `areacode`, `npa`, or `code`)
   - Coordinate Reference System (CRS) set to EPSG:4326 (WGS84)
3. Replace the `area-codes.parquet` file or specify a different path

## Usage

```python
from area_code_locator import AreaCodeLocator

# Use included data (recommended)
locator = AreaCodeLocator()

# Lookup area code for a location
area_code = locator.lookup(40.7128, -74.0060)  # New York City
print(area_code)  # ['212']

# Get all matching area codes
all_codes = locator.lookup(34.0522, -118.2437, return_all=True)  # Los Angeles
print(all_codes)  # ['213', '310', ...]

# Or use custom data
locator_custom = AreaCodeLocator("path/to/your/area-codes.parquet")
```

## API Reference

### AreaCodeLocator

#### `__init__(path: Optional[str] = None, projected_epsg: int = 5070)`

Initialize the locator with area code data.

- `path`: Path to a Parquet file containing area code polygons. If None, uses the included data.
- `projected_epsg`: EPSG code for projected coordinate system (default: 5070 - NAD83/Conus Albers)

#### `lookup(lat: float, lon: float, return_all: bool = True) -> Union[str, List[str]]`

Find area codes for the given latitude and longitude.

- `lat`: Latitude in decimal degrees
- `lon`: Longitude in decimal degrees
- `return_all`: If True, return all matching codes; if False, return only the first match

Returns a list of area codes or a single area code string.

## Algorithm

The lookup uses a hierarchical approach:

1. **Exact match**: Check if the point is exactly within any area code polygon
2. **Buffer search**: If no exact match, search within a 50-meter buffer around the point
3. **Expanding search**: If still no match, search in expanding circles (25km, 100km, 300km) and return the nearest area code

## Development

For development, install with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## Acknowledgments

This project uses area code boundary data derived from [nanp-boundaries](https://github.com/1ec5/nanp-boundaries) by Elijah Verdoorn, which provides comprehensive GeoJSON boundaries for North American Numbering Plan (NANP) area codes.

## License

MIT License