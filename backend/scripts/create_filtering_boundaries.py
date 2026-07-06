#!/usr/bin/env python3
"""Create district-sized GeoJSON from OSM extracts for participant filtering.

Combines French arrondissements (admin_level7) from Franche-Comte and Rhone-Alpes
with Swiss districts (admin_level6) and districtless cantons (admin_level4).
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

LAYER_NAME = "gis_osm_adminareas_a_free"

DISTRICTLESS_CANTONS: list[str] = [
    "Uri",
    "Obwalden",
    "Nidwalden",
    "Glarus",
    "Zug",
    "Basel-Stadt",
    "Genève",
    "Appenzell Innerrhoden",
    "Appenzell Ausserrhoden",
    "Luzern",
    "Neuchâtel",
]


def read_osm_extract(path: Path, layer: str = LAYER_NAME) -> gpd.GeoDataFrame:
    """Read an OSM administrative areas layer from a GeoPackage."""
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return gpd.read_file(path, layer=layer)


def get_france_arrondissements(france_paths: list[Path], crs: str) -> gpd.GeoDataFrame:
    """Extract admin_level7 (arrondissements) from French OSM extracts."""
    frames: list[gpd.GeoDataFrame] = []
    for path in france_paths:
        gdf = read_osm_extract(path)
        arrondissements = gdf[gdf.fclass == "admin_level7"].to_crs(crs)
        print(f"  {path.name}: {len(arrondissements)} arrondissements")
        frames.append(arrondissements)
    return pd.concat(frames, ignore_index=True)


def get_switzerland_areas(ch_path: Path, crs: str) -> gpd.GeoDataFrame:
    """Extract Swiss districts and districtless cantons from the OSM extract."""
    gdf = read_osm_extract(ch_path)

    districts = gdf[gdf.fclass == "admin_level6"].to_crs(crs)
    print(f"  {ch_path.name}: {len(districts)} districts")

    cantons = gdf[(gdf.fclass == "admin_level4") &
                  (gdf.name.isin(DISTRICTLESS_CANTONS))].to_crs(crs)
    print(f"  {ch_path.name}: {len(cantons)} districtless cantons")

    return pd.concat([cantons, districts], ignore_index=True)


def main() -> None:
    """Build the unified administrative boundaries GeoJSON."""
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    france_paths = [
        data_dir / "france" / "franche-comte" / "franche-comte.gpkg",
        data_dir / "france" / "rhone-alpes" / "rhone-alpes.gpkg",
    ]

    ch_path = data_dir / "switzerland" / "switzerland" / "switzerland.gpkg"

    crs = "EPSG:4326"  # WGS84

    print("Loading French arrondissements...")
    france = get_france_arrondissements(france_paths, crs)

    print("Loading Swiss areas...")
    switzerland = get_switzerland_areas(ch_path, crs)

    output = pd.concat([france, switzerland], ignore_index=True)
    output_path = data_dir / "filtering_boundaries.geojson"

    print(f"\nTotal features: {len(output)}")
    print(f"Writing to {output_path}...")
    output.to_file(output_path, driver="GeoJSON")
    print("Done.")


if __name__ == "__main__":
    main()
