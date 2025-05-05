import math
from dataclasses import dataclass
import numpy as np

@dataclass
class Tower:
    latitude: float
    longitude: float
    radius: float  # in meters
    def __init__(self, latitude, longitude, radius):
        """
        Initialize a tower with its latitude, longitude, and radius.
        :param latitude: Latitude of the tower's location.
        :param longitude: Longitude of the tower's location.
        :param radius: Radius of the tower's coverage in kilometers.
        """
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius * 1000  # Convert radius to meters

    @staticmethod
    def closest_tower(towers, point, radius):
        """
        Find the closest tower to a given point and create a Tower instance.
        :param towers: List of tuples [(longitude, latitude), ...] representing tower coordinates.
        :param point: Tuple (longitude, latitude) representing the reference point.
        :param radius: Radius to assign to the created Tower instance in kilometers.
        :return: Tower instance for the closest tower.
        """
        def haversine(lon1, lat1, lon2, lat2):
            # Calculate the great-circle distance between two points on the Earth
            R = 6371  # Earth radius in kilometers
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        closest = min(towers, key=lambda tower: haversine(point[0], point[1], tower[0], tower[1]))
        return Tower(latitude=closest[1], longitude=closest[0], radius=radius)

class Triangulation:
    def __init__(self, tower1: Tower, tower2: Tower, tower3: Tower):
        """
        Initialize with three Tower objects.
        :param tower1: Tower object for the first tower.
        :param tower2: Tower object for the second tower.
        :param tower3: Tower object for the third tower.
        """
        self.tower1 = tower1
        self.tower2 = tower2
        self.tower3 = tower3

    @staticmethod
    def latlon_to_xy(lat, lon, ref_lat, ref_lon):
        """
        Convert latitude and longitude to local x, y coordinates in meters relative to a reference point.
        """
        R = 6371000  # Earth radius in meters
        x = R * (math.radians(lon) - math.radians(ref_lon)) * math.cos(math.radians(ref_lat))
        y = R * (math.radians(lat) - math.radians(ref_lat))
        return (x, y)

    @staticmethod
    def calculate_position(tower1: Tower, tower2: Tower, tower3: Tower):
        """
        Calculate the position of the target based on distances to the three towers.
        :param tower1: Tower object for the first tower.
        :param tower2: Tower object for the second tower.
        :param tower3: Tower object for the third tower.
        :return: Tuple (longitude, latitude) representing the estimated position.
        """
        # Choose tower1 as reference point
        ref_lat = tower1.latitude
        ref_lon = tower1.longitude

        # Convert all tower coordinates to x, y
        x1, y1 = Triangulation.latlon_to_xy(tower1.latitude, tower1.longitude, ref_lat, ref_lon)
        x2, y2 = Triangulation.latlon_to_xy(tower2.latitude, tower2.longitude, ref_lat, ref_lon)
        x3, y3 = Triangulation.latlon_to_xy(tower3.latitude, tower3.longitude, ref_lat, ref_lon)
        r1 = tower1.radius
        r2 = tower2.radius
        r3 = tower3.radius

        # Solve using trilateration equations
        A = 2 * (x2 - x1)
        B = 2 * (y2 - y1)
        C = r1**2 - r2**2 - x1**2 - y1**2 + x2**2 + y2**2
        D = 2 * (x3 - x2)
        E = 2 * (y3 - y2)
        F = r2**2 - r3**2 - x2**2 - y2**2 + x3**2 + y3**2

        # Calculate x and y
        denominator = A * E - B * D
        if abs(denominator) < 1e-10:  # Avoid division by zero or near-zero values
            raise ValueError("The towers are collinear or distances are invalid.")

        x = (C * E - F * B) / denominator
        y = (A * F - C * D) / denominator

        # Convert back to latitude and longitude
        est_lon = ref_lon + (x / (6371000 * math.cos(math.radians(ref_lat)))) * (180 / math.pi)
        est_lat = ref_lat + (y / 6371000) * (180 / math.pi)

        return (est_lon, est_lat)

    @staticmethod
    def triangulate_position(tower1: Tower, tower2: Tower, tower3: Tower):
        """
        Calculate the centroid (approximation to the middle point) of the triangle formed by three towers.
        :param tower1: Tower object for the first tower.
        :param tower2: Tower object for the second tower.
        :param tower3: Tower object for the third tower.
        :return: Tuple (longitude, latitude) representing the centroid of the triangle.
        """
        # Calculate the centroid of the triangle
        centroid_lat = (tower1.latitude + tower2.latitude + tower3.latitude) / 3
        centroid_lon = (tower1.longitude + tower2.longitude + tower3.longitude) / 3

        return (centroid_lon, centroid_lat)
