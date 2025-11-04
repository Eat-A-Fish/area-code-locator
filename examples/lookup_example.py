#!/usr/bin/env python3
"""
Example usage of the Area Code Locator library.
"""

from area_code_locator import AreaCodeLocator

def main():
    # The area-codes.parquet file is included with the library,
    # so no setup is required!

    # Initialize the locator (uses included data by default)
    try:
        locator = AreaCodeLocator()
    except FileNotFoundError:
        print("Error: area-codes.parquet file not found.")
        print("The data file should be included with the library.")
        return

    # Example locations
    locations = [
        (40.7128, -74.0060, "New York City, NY"),
        (34.0522, -118.2437, "Los Angeles, CA"),
        (41.8781, -87.6298, "Chicago, IL"),
        (29.7604, -95.3698, "Houston, TX"),
        (33.4484, -112.0740, "Phoenix, AZ"),
    ]

    print("Area Code Lookup Examples:")
    print("=" * 40)

    for lat, lon, location in locations:
        try:
            area_codes = locator.lookup(lat, lon, return_all=True)
            print(f"{location}: {', '.join(area_codes)}")
        except Exception as e:
            print(f"{location}: Error - {e}")

if __name__ == "__main__":
    main()