import argparse
from . import lookup

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--all", dest="return_all", action="store_true")
    args = p.parse_args()
    print(lookup(args.lat, args.lon, return_all=args.return_all))