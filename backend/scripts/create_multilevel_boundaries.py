#!/usr/bin/env python3
"""
Create unified GeoPackages for local, regional, and national boundaries.
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd

def extract_municipalities(
    nuts_df: gpd.GeoDataFrame, 
    lau_df: gpd.GeoDataFrame, 
    country_code: str, 
    region_name: str) -> gpd.GeoDataFrame:
    """Extract municipalities (LAU) that intersect with a given NUTS region."""
    region = nuts_df[(nuts_df["CNTR_CODE"] == country_code) & (nuts_df["NAME_LATN"] == region_name)]
    region_geometry = region.geometry.iloc[0]
    municipalities = lau_df[(lau_df.intersects(region_geometry)) & (lau_df["CNTR_CODE"] == country_code)]
    return municipalities

def get_data_path() -> Path:
    """Get the path to the data directory."""
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    return data_dir

def extract_local_boundaries(
    nuts_df: gpd.GeoDataFrame,
    lau_df: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Extract local boundaries (municipalities) for all countries."""
    fr_municipalities = extract_local_french_boundaries(nuts_df, lau_df)
    ch_municipalities = extract_local_swiss_boundaries(lau_df)
    de_municipalities = extract_local_german_boundaries(nuts_df, lau_df)
    it_municipalities = extract_local_italian_boundaries(nuts_df, lau_df)

    municipalities = pd.concat([fr_municipalities, ch_municipalities, de_municipalities, it_municipalities], ignore_index=True)
        
    municipalities = municipalities[["CNTR_CODE", "LAU_NAME", "geometry"]]
    municipalities = municipalities.rename(columns={"CNTR_CODE": "country", "LAU_NAME": "name"})

    return municipalities


def extract_local_french_boundaries(
    nuts_df: gpd.GeoDataFrame,
    lau_df: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    fr_ara_municipalities = extract_municipalities(nuts_df, lau_df, "FR", "Auvergne-Rhône-Alpes")
    fr_bfc_municipalities = extract_municipalities(nuts_df, lau_df, "FR", "Bourgogne-Franche-Comté")
    fr_ge_municipalities = extract_municipalities(nuts_df, lau_df, "FR", "Grand Est")

    fr_municipalities = pd.concat([fr_ara_municipalities, fr_bfc_municipalities, fr_ge_municipalities], ignore_index=True)

    return fr_municipalities


def extract_local_swiss_boundaries(
    lau_df: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    return lau_df[(lau_df["CNTR_CODE"] == "CH") & (lau_df["POP_2024"] > 0)]


def extract_local_german_boundaries(
    nuts_df: gpd.GeoDataFrame,
    lau_df: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    bw_municipalities = extract_municipalities(nuts_df, lau_df, "DE", "Baden-Württemberg")

    return bw_municipalities

def extract_local_italian_boundaries(
    nuts_df: gpd.GeoDataFrame,
    lau_df: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    it_va_municipalities = extract_municipalities(nuts_df, lau_df, "IT", "Valle d’Aosta/Vallée d’Aoste")
    it_pi_municipalities = extract_municipalities(nuts_df, lau_df, "IT", "Piemonte")

    return pd.concat([it_va_municipalities, it_pi_municipalities], ignore_index=True)

def extract_regional_boundaries(
    nuts_df: gpd.GeoDataFrame,
    nuts_2021_df: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    # Configure exclusions here
    EXCLUDED_NUTS3_IDS = {"FRY10", "FRY20", "FRY30", "FRY40", "FRY50"}  # FR overseas departments
    EXCLUDED_NUTS2_IDS = {"ES70", "PT20", "PT30"}  # Canarias, Açores, Madeira

    # Optional extra exclusions by display name
    EXCLUDED_NUTS3_NAMES = {"Guadeloupe", "Guyane", "La Réunion", "Mayotte", "Martinique"}
    EXCLUDED_NUTS2_NAMES = {"Canarias", "Açores", "Madeira"}

    nuts_clean = nuts_df.assign(NAME_LATN_CLEAN=nuts_df["NAME_LATN"].fillna("").str.strip())

    nuts3 = nuts_clean[(nuts_clean["LEVL_CODE"] == 3) & (nuts_clean["CNTR_CODE"].isin(["FR", "CH"]))]
    nuts3 = nuts3[
        (~nuts3["NUTS_ID"].isin(EXCLUDED_NUTS3_IDS))
        & (~nuts3["NAME_LATN_CLEAN"].isin(EXCLUDED_NUTS3_NAMES))
    ]

    nuts2 = nuts_clean[(nuts_clean["LEVL_CODE"] == 2) & (~nuts_clean["CNTR_CODE"].isin(["FR", "CH"]))]
    nuts2 = nuts2[
        (~nuts2["NUTS_ID"].isin(EXCLUDED_NUTS2_IDS))
        & (~nuts2["NAME_LATN_CLEAN"].isin(EXCLUDED_NUTS2_NAMES))
    ]

    regions = pd.concat([nuts3, nuts2], ignore_index=True).drop(columns=["NAME_LATN_CLEAN"], errors="ignore")

    uk_nuts = nuts_2021_df[(nuts_2021_df["CNTR_CODE"] == "UK") & (nuts_2021_df["LEVL_CODE"] == 2)]
    regions = pd.concat([regions, uk_nuts], ignore_index=True)

    regions = regions[["CNTR_CODE", "NAME_LATN", "geometry"]]
    # rename columns to "country, name, geometry"
    regions = regions.rename(columns={"CNTR_CODE": "country", "NAME_LATN": "name"})

    return regions

def extract_national_boundaries(gbd_df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    nations = gbd_df[["shapeType", "shapeName", "geometry"]]
    # rename columns to "type, name, geometry"
    nations = nations.rename(columns={"shapeType": "type", "shapeName": "name"})

    return nations


def main() -> None:
    data_dir = get_data_path()
    nuts_df = gpd.read_file(data_dir / "NUTS_RG_01M_2024_3035.gpkg")
    nuts_2021_df = gpd.read_file(data_dir / "NUTS_RG_01M_2021_3035.gpkg")
    lau_df = gpd.read_file(data_dir / "LAU_RG_01M_2024_3035.gpkg")
    gbd_df = gpd.read_file(data_dir / "geoBoundariesCGAZ_ADM0.gpkg")

    print("Extracting local boundaries...")
    local_boundaries = extract_local_boundaries(nuts_df, lau_df)
    local_boundaries.to_file(data_dir / "local_boundaries.geojson", driver="GeoJSON")
    
    print("Extracting regional boundaries...")
    regional_boundaries = extract_regional_boundaries(nuts_df, nuts_2021_df)
    regional_boundaries.to_file(data_dir / "regional_boundaries.geojson", driver="GeoJSON")

    print("Extracting national boundaries...")
    national_boundaries = extract_national_boundaries(gbd_df)
    national_boundaries.to_file(data_dir / "national_boundaries.geojson", driver="GeoJSON")

if __name__ == "__main__":
    main()
