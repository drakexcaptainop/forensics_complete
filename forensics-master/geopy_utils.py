import folium
from folium.plugins import HeatMap
import pandas as pd
from geopy.distance import geodesic
from matplotlib import cm
from matplotlib.colors import to_hex
import jmespath
import json

def generate_heatmap(data_points, map_center, zoom_start=10, output_file="heatmap.html", add_pins=True, alternate_points=None):
    """
    Generates a heatmap based on longitude and latitude points and optionally adds pins.

    Args:
        data_points (list of tuples): List of (latitude, longitude) points.
        map_center (tuple): The (latitude, longitude) center of the map.
        zoom_start (int): Initial zoom level for the map.
        output_file (str): File name to save the heatmap.
        add_pins (bool): Whether to add pins for each point on the map.
        alternate_points (list of tuples): Another set of points to find the closest pin locations.

    Returns:
        None
    """
    # Create a map centered at the specified location
    heatmap_map = folium.Map(location=map_center, zoom_start=zoom_start)

    # Function to calculate radius in pixels for a 2 km diameter
    def calculate_radius(zoom_level):
        # Approximation: 1 pixel = 156543.03392 meters at zoom level 0
        meters_per_pixel = 156543.03392 / (2 ** zoom_level)
        radius_in_meters = 2000 / 2  # 2 km diameter, so 1 km radius
        return int(radius_in_meters / meters_per_pixel)

    # Calculate radius based on the zoom level
    radius = calculate_radius(zoom_start)

    # Add the heatmap layer
    points = []
    # Optionally add pins for each point
    if add_pins:
        previous_point = None
        color_map = cm.get_cmap('viridis', len(data_points))  # Use a colormap with as many colors as data points
        for t, (lat, lon) in enumerate(data_points):
            if alternate_points:
                # Find the closest point in alternate_points
                closest_point = min(alternate_points, key=lambda p: geodesic((lat, lon), p).meters)
                points.append(closest_point)
                folium.Marker(location=closest_point).add_to(heatmap_map)
                # Draw a line from the previous point to the current point with a gradient color
                if previous_point:
                    line_color = to_hex(color_map(t))  # Get the color for the current index
                    folium.PolyLine([previous_point, closest_point], color=line_color, weight=2.5).add_to(heatmap_map)
                previous_point = closest_point
            else:
                folium.Marker(location=(lat, lon)).add_to(heatmap_map)
    HeatMap(points, max_zoom=18, radius=radius, blur=10, min_opacity=0.8).add_to(heatmap_map)
    # Save the map to an HTML file
    heatmap_map.save(output_file)
    print(f"Heatmap saved to {output_file}")

def read_coordinates_from_csv(file_path, lat_column="Latitude", lon_column="Longitude"):
    """
    Reads a CSV file and extracts latitude and longitude columns.

    Args:
        file_path (str): Path to the CSV file.
        lat_column (str): Name of the latitude column in the CSV.
        lon_column (str): Name of the longitude column in the CSV.

    Returns:
        list of tuples: List of (latitude, longitude) points.
    """
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Extract latitude and longitude columns and format as a list of tuples
    data_points = list(zip(df[lon_column], df[lat_column]))

    return data_points


def read_geojson(file_path):
    """
    Reads a GeoJSON file and returns the data.

    Args:
        file_path (str): Path to the GeoJSON file.

    Returns:
        dict: Parsed GeoJSON data.
    """
    with open(file_path, 'r') as f:
        geojson_data = f.read()
    return json.loads(geojson_data)

def extract_coordinates_by_marker_color(json_data, marker_color):
    """
    Extracts coordinates from a JSON array of components based on the specified marker color.

    Args:
        json_data (str or dict): JSON data as a string or dictionary.
        marker_color (str): The marker color to filter coordinates by.

    Returns:
        list of tuples: List of (longitude, latitude) coordinates.
    """
    # Parse json_data if it's a string
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    
    # JMESPath query to filter by marker-color and extract coordinates
    query = f'features[?properties.markerColor==`{marker_color}`].geometry.coordinates'
    coordinates = jmespath.search(query, json_data)
    return [tuple(coord) for coord in coordinates]

