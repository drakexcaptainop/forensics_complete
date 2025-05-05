from enum import Enum
import folium
from folium.plugins import HeatMap

class Icon(Enum):
    """
    Enum for predefined marker icons.
    """
    TOWER = "tower"
    HOME = "home"
    STAR = "star"
    FLAG = "flag"
    TELECOM_TOWER = "telecom-tower"  # Added telecom tower icon
    PERSON = "person"  # Added person icon

class FoliumBuilder:
    """
    A class to build and manipulate Folium maps.
    """

    def __init__(self, center, zoom_start=13):
        """
        Initialize the FoliumBuilder with a map centered at a specific location.

        Parameters:
            center (list of [lat, lon]): The center of the map [latitude, longitude].
            zoom_start (int): Initial zoom level of the map.
        """
        self.map = folium.Map(location=center, zoom_start=zoom_start)

    def add_marker(self, location, popup=None, tooltip=None, icon=None):
        """
        Adds a marker to the map.

        Parameters:
            location (list of [lat, lon]): The location of the marker [latitude, longitude].
            popup (str): Optional popup text for the marker.
            tooltip (str): Optional tooltip text for the marker.
            icon (Icon): Optional icon for the marker (from the Icon enum).
        """
        marker_icon = folium.Icon(icon=icon.value) if icon else None
        folium.Marker(location=location, popup=popup, tooltip=tooltip, icon=marker_icon).add_to(self.map)

    def add_circle(self, location, radius, color="blue", fill=True, fill_color="blue", fill_opacity=0.5):
        """
        Adds a circle to the map.

        Parameters:
            location (list of [lat, lon]): The center of the circle [latitude, longitude].
            radius (float): The radius of the circle in kilometers.
            color (str): Border color of the circle.
            fill (bool): Whether to fill the circle.
            fill_color (str): Fill color of the circle.
            fill_opacity (float): Fill opacity of the circle.
        """
        radius_in_meters = radius * 1000  # Convert radius from kilometers to meters
        folium.Circle(
            location=location,
            radius=radius_in_meters,
            color=color,
            fill=fill,
            fill_color=fill_color,
            fill_opacity=fill_opacity
        ).add_to(self.map)

    def add_polyline(self, locations, color="blue", weight=2, opacity=1.0):
        """
        Adds a polyline to the map.

        Parameters:
            locations (list of [lat, lon]): List of coordinates forming the polyline.
            color (str): Color of the polyline.
            weight (int): Width of the polyline.
            opacity (float): Opacity of the polyline.
        """
        folium.PolyLine(
            locations=locations,
            color=color,
            weight=weight,
            opacity=opacity
        ).add_to(self.map)

    def add_lines_from_coordinates(self, coordinates, color="blue", weight=2, opacity=1.0, marker=False, icon=None):
        """
        Adds lines connecting consecutive coordinates in the array.

        Parameters:
            coordinates (list of [lat, lon]): List of coordinates to connect with lines.
            color (str): Color of the lines.
            weight (int): Width of the lines.
            opacity (float): Opacity of the lines.
            marker (bool): If True, adds a marker to each coordinate.
        """
        for i in range(len(coordinates) - 1):
            self.add_polyline(
                locations=[coordinates[i], coordinates[i + 1]],
                color=color,
                weight=weight,
                opacity=opacity
            )
            if marker:
                self.add_marker(location=coordinates[i], icon=icon)  # Add marker to each coordinate
        if marker:
            self.add_marker(location=coordinates[-1], icon=icon)  # Add marker to the last coordinate

    def add_heatmap(self, points, radius=10, blur=15, max_zoom=1):
        """
        Adds a heat map to the map using a series of points.

        Parameters:
            points (list of [lat, lon]): List of points to include in the heat map.
            radius (int): Radius of each point in the heat map.
            blur (int): Amount of blur for the heat map.
            max_zoom (int): Maximum zoom level for the heat map.
        """
        HeatMap(points, radius=radius, blur=blur, max_zoom=max_zoom).add_to(self.map)

    def save_to_file(self, path):
        """
        Saves the map to an HTML file.

        Parameters:
            path (str): The file path where the map will be saved.
        """
        self.map.save(path)


