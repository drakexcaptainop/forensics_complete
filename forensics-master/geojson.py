import json
import math
import folium

class GeoJSONBuilder:
    """
    A class to build and manipulate GeoJSON FeatureCollections.
    """

    def __init__(self, geojson_dict):
        """
        Initialize the GeoJSONBuilder with a GeoJSON FeatureCollection.

        Parameters:
            geojson_dict (dict): A GeoJSON FeatureCollection.
        """
        if geojson_dict.get("type") != "FeatureCollection":
            raise ValueError("Input must be a GeoJSON FeatureCollection")
        self.geojson = geojson_dict

    def add_line_to_geojson(self, coordinates, properties=None):
        """
        Adds a LineString feature to the GeoJSON FeatureCollection.

        Parameters:
            coordinates (list of [lon, lat]): List of coordinates forming the line.
            properties (dict): Optional properties for the line feature.

        Returns:
            dict: Updated GeoJSON dictionary.
        """
        line_feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            },
            "properties": properties or {}
        }

        self.geojson["features"].append(line_feature)
        return self.geojson

    def add_circle_to_geojson(self, center, radius, properties=None, alpha=1.0, color=None, tooltip=None):
        """
        Adds a circle (as a Polygon) feature to the GeoJSON FeatureCollection.

        Parameters:
            center (list of [lon, lat]): The center of the circle [longitude, latitude].
            radius (float): The radius of the circle in kilometers.
            properties (dict): Optional properties for the circle feature.
            alpha (float): Transparency level for the circle fill (0.0 to 1.0).
            color (str): Optional color for the circle fill.
            tooltip (str): Optional tooltip text for the circle feature.
        """
        # Convert radius from kilometers to degrees (approximation)
        radius_in_degrees = radius / 111.32  # 1 degree ≈ 111.32 km

        num_segments = 64  # Number of segments to approximate the circle
        circle_coords = []
        for i in range(num_segments + 1):
            angle = 2 * math.pi * i / num_segments
            dx = radius_in_degrees * math.cos(angle)
            dy = radius_in_degrees * math.sin(angle)
            circle_coords.append([center[0] + dx, center[1] + dy])

        # Add alpha, color, and tooltip to properties
        if properties is None:
            properties = {}
        properties["fill-opacity"] = alpha
        if color:
            properties["fill"] = color
        if tooltip:
            properties["tooltip"] = tooltip  # Use 'name' for geojson.io compatibility

        circle_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [circle_coords]
            },
            "properties": properties
        }

        self.geojson["features"].append(circle_feature)
        return self.geojson

    def save_to_file(self, path):
        """
        Saves the GeoJSON dictionary to a file.

        Parameters:
            path (str): The file path where the GeoJSON will be saved.
        """
        with open(path, 'w') as file:
            json.dump(self.geojson, file, indent=2)
    
    @staticmethod
    def get_base_geojson():
        return GeoJSONBuilder(  GeoJSONBuilder.get_dict_template()) 
    
    @staticmethod
    def get_dict_template():
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    @staticmethod
    def extract_coordinates(geojson_file_path):
        """
        Extracts coordinates from a GeoJSON file.

        Parameters:
            geojson_file_path (str): The file path to a GeoJSON file.

        Returns:
            list of tuple: A list of (lat, lon) tuples extracted from the GeoJSON.
        """
        with open(geojson_file_path, 'r') as file:
            geojson_data = json.load(file)

        coordinates = []

        for feature in geojson_data.get("features", []):
            geometry = feature.get("geometry", {})
            if geometry.get("type") == "Point":
                # Extract coordinates for Point
                lon, lat = geometry.get("coordinates", [None, None])
                coordinates.append((lat, lon))
            elif geometry.get("type") in ["LineString", "Polygon"]:
                # Extract coordinates for LineString or Polygon
                for coord in geometry.get("coordinates", []):
                    if isinstance(coord[0], list):  # For Polygon
                        coordinates.extend([(lat, lon) for lon, lat in coord])
                    else:  # For LineString
                        lon, lat = coord
                        coordinates.append((lat, lon))

        return coordinates
    
    def add_marker(self, location, properties=None, tooltip=None):
        """
        Adds a Point feature to the GeoJSON FeatureCollection.

        Parameters:
            location (list of [lon, lat]): The location of the marker [longitude, latitude].
            properties (dict): Optional properties for the marker feature.
            tooltip (str): Optional tooltip text for the marker feature.
        """
        if properties is None:
            properties = {}
        if tooltip:
            properties["tooltip"] = tooltip

        point_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": location
            },
            "properties": properties
        }
        self.geojson["features"].append(point_feature)

    def add_circle(self, location, radius, properties=None, tooltip=None):
        """
        Adds a circle (as a Polygon) feature to the GeoJSON FeatureCollection.

        Parameters:
            location (list of [lon, lat]): The center of the circle [longitude, latitude].
            radius (float): The radius of the circle in kilometers.
            properties (dict): Optional properties for the circle feature.
            tooltip (str): Optional tooltip text for the circle feature.
        """
        self.add_circle_to_geojson(center=location, radius=radius, properties=properties, tooltip=tooltip)

    def add_polyline(self, locations, properties=None):
        """
        Adds a LineString feature to the GeoJSON FeatureCollection.

        Parameters:
            locations (list of [lon, lat]): List of coordinates forming the polyline.
            properties (dict): Optional properties for the polyline feature.
        """
        self.add_line_to_geojson(coordinates=locations, properties=properties)

    def add_lines_from_coordinates(self, coordinates, properties=None):
        """
        Adds LineString features connecting consecutive coordinates in the array.

        Parameters:
            coordinates (list of [lon, lat]): List of coordinates to connect with lines.
            properties (dict): Optional properties for the lines.
        """
        for i in range(len(coordinates) - 1):
            self.add_polyline(
                locations=[coordinates[i], coordinates[i + 1]],
                properties=properties
            )

    def addv_heatmap(self, points, properties=None):
        """
        Adds a heatmap-like representation by adding Point features for each point.

        Parameters:
            points (list of [lon, lat]): List of points to include in the heatmap.
            properties (dict): Optional properties for the points.
        """
        for point in points:
            self.add_marker(location=point, properties=properties)
    
    def add_tooltip_or_label(self, feature_index, tooltip=None, label=None):
        """
        Adds tooltip or label text to a specific feature in the GeoJSON FeatureCollection.

        Parameters:
            feature_index (int): The index of the feature in the FeatureCollection.
            tooltip (str): Optional tooltip text to add to the feature's properties.
            label (str): Optional label text to add to the feature's properties.
        """
        if feature_index < 0 or feature_index >= len(self.geojson["features"]):
            raise IndexError("Feature index out of range")

        feature = self.geojson["features"][feature_index]
        if tooltip:
            feature["properties"]["tooltip"] = tooltip  # Use 'name' for geojson.io compatibility
        if label:
            feature["properties"]["label"] = label

    def add_direct_feature(self, feature):
        """
        Appends a feature directly to the GeoJSON FeatureCollection.

        Parameters:
            feature (dict): A GeoJSON feature to append.
        """
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            raise ValueError("Input must be a valid GeoJSON Feature")
        self.geojson["features"].append(feature)

class GeoJSONToFolium:
    """
    A class to transform a GeoJSON string into an interactive HTML map using folium.
    """

    def __init__(self, geojson_str):
        """
        Initialize the GeoJSONToFolium with a GeoJSON string.

        Parameters:
            geojson_str (str): A GeoJSON string.
        """
        self.geojson_data = json.loads(geojson_str)

    @staticmethod
    def from_file(file_path):
        """
        Creates an instance of GeoJSONToFolium from a GeoJSON file.

        Parameters:
            file_path (str): The file path to the GeoJSON file.

        Returns:
            GeoJSONToFolium: An instance of GeoJSONToFolium initialized with the file's content.
        """
        with open(file_path, 'r') as file:
            geojson_str = file.read()
        return GeoJSONToFolium(geojson_str)

    def generate_map(self, center=None, zoom_start=10):
        """
        Generates a folium map with the GeoJSON data.

        Parameters:
            center (list of [lat, lon]): The center of the map. If None, the center is calculated dynamically.
            zoom_start (int): Initial zoom level for the map.

        Returns:
            folium.Map: A folium map object.
        """
        if center is None:
            # Calculate the center dynamically based on the bounding box of all features
            all_coords = []
            for feature in self.geojson_data.get("features", []):
                geometry = feature.get("geometry", {})
                coords = geometry.get("coordinates", [])
                if geometry.get("type") == "Point":
                    all_coords.append(coords)
                elif geometry.get("type") == "LineString":
                    all_coords.extend(coords)
                elif geometry.get("type") == "Polygon":
                    for ring in coords:
                        all_coords.extend(ring)

            if not all_coords:
                raise ValueError("No coordinates found in the GeoJSON data to calculate the center.")

            # Calculate the bounding box and center
            lons, lats = zip(*all_coords)
            center = [sum(lats) / len(lats), sum(lons) / len(lons)]

        # Create a folium map
        folium_map = folium.Map(location=center, zoom_start=zoom_start)

        # Add GeoJSON data to the map with custom styling
        def style_function(feature):
            properties = feature.get("properties", {})
            return {
                "color": properties.get("color", "blue"),
                "fillColor": properties.get("fill", "blue"),
                "fillOpacity": properties.get("fill-opacity", 0.6),
            }

        # Add GeoJSON data with tooltips
        geojson_layer = folium.GeoJson(
            self.geojson_data,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=["tooltip"],  # Ensure "tooltip" is included in properties
                aliases=["Tooltip:"],
                localize=True,
                labels=False,  # Avoid errors if tooltip is missing
                sticky=False
            )
        )
        geojson_layer.add_to(folium_map)
        return folium_map

    def save_to_html(self, output_path, center=None, zoom_start=10):
        """
        Saves the folium map as an HTML file.

        Parameters:
            output_path (str): The file path to save the HTML file.
            center (list of [lat, lon]): The center of the map. If None, the first feature's coordinates are used.
            zoom_start (int): Initial zoom level for the map.
        """
        folium_map = self.generate_map(center=center, zoom_start=zoom_start)
        folium_map.save(output_path)

