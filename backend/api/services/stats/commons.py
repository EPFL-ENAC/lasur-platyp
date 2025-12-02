import pandas as pd
import h3


MODES = [
    'walking',
    'bike',
    'ebike',
    'pub',
    'moto',
    'carpool',
    'car',
    'train'
]

RECOS = [
    'train',
    'tpu',
    'vae',
    'velo',
    'marche',
    'inter',
    'elec',
    'covoit'
]

MODES_PRO_V1 = [
    'local_walking',
    'local_car',
    'local_pub',
    'local_bike',
    'local_moto',
    'local_train',
    'region_car',
    'region_pub',
    'region_train',
    'region_moto',
    'region_plane',
    'europe_car',
    'europe_train',
    'europe_plane',
    'inter_car',
    'inter_train',
    'inter_plane'
]

MODES_PRO = [
    'walking',
    'bike',
    'pub',
    'moto',
    'car',
    'train',
    'boat',
    'plane',
]

RECOS_PRO = [
    'train',
    'ebike',
    'bike',
    'walking',
    'elec',
    'plane',
    'boat',
    'elec_moto',
    'pub'
]


class BaseStatsService:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _get_records_v1(self) -> pd.DataFrame:
        """Get records with data.version as NaN"""
        if 'data.version' not in self.df.columns:
            return self.df.copy()
        df_v1 = self.df[self.df['data.version'].isna()].copy()
        return df_v1

    def _get_records_v2(self) -> pd.DataFrame:
        """Get records with data.version starting with '2.'"""
        if 'data.version' not in self.df.columns:
            return pd.DataFrame()
        df_v2 = self.df[self.df['data.version'].notna(
        ) & self.df['data.version'].str.startswith('2.')].copy()
        return df_v2

    def _calculate_distance(self, origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> float:
        """Calculate the distance between origin and destination locations."""
        try:
            from math import radians, cos, sin, acos
            distance_km = 6371 * acos(
                cos(radians(origin_lat)) *
                cos(radians(dest_lat)) *
                cos(radians(dest_lon) - radians(origin_lon)) +
                sin(radians(origin_lat)) *
                sin(radians(dest_lat))
            )
            return distance_km * 1.3  # factor for real distance
        except Exception:
            return 0

    def _calculate_distance_to_h3(self, lat: float, lon: float, h3_index: str, mode: str) -> float:
        """Calculate the distance between workplace and destination with a transport mode."""
        try:
            if pd.isna(h3_index):
                return 0
            # Hypothèse sur l'allongement des distances : en moyenne, 1.22 (network based vs real measured distances : https://journals.sagepub.com/doi/abs/10.3141/1804-28)
            # On pourrait améliorer ca en cherchant la meme chose pour l'avion (études sur les détours/distances faites lorsqu'on doit attendre au dessus d'un aéroport plein...)
            # Pareil pour le bateau (pour l'instant on applique 1.22 à tous)
            avg_dist_coeff = {'train': 1.22, 'car': 1.22, 'bike': 1.22,
                              'walk': 1.22, 'moto': 1.22, 'pub': 1.22, 'boat': 1.22, 'plane': 1.22}
            if h3.latlng_to_cell(lat, lon, h3.get_resolution(h3_index)) == h3_index:
                # Si meme hexagone (apres mise à la resolution choisie par l'utilisateur), on prend une distance moyenne de la taille d'une arrête de l'hexagone.
                return h3.average_hexagon_edge_length(h3.get_resolution(h3_index))
            else:
                # Si pas meme hexagone, on convertit le centre du h3 sélectionné en h3 plus petit pour calculer des distances plus précises
                return h3.great_circle_distance(h3.cell_to_latlng(h3.cell_to_center_child(h3_index, 9)),
                                                (lat, lon)) * avg_dist_coeff[mode]
        except Exception:
            return 0

    def _calculate_distance_home_to_work(self, row):
        """Calculate distance from home to workplace for a record."""
        origin_lat = float(row['data.origin.lat'])
        origin_lon = float(row['data.origin.lon'])
        work_lat = float(row['data.workplace.lat'])
        work_lon = float(row['data.workplace.lon'])
        return self._calculate_distance(origin_lat, origin_lon, work_lat, work_lon)
