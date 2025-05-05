from geojson import GeoJSONBuilder
from folium_builder import FoliumBuilder, Icon
import geopy_utils as gu

builder = GeoJSONBuilder.get_base_geojson()


line_coords = gu.read_coordinates_from_csv("longlat_output.csv") # Example: NY path
folium_builder = FoliumBuilder(center=line_coords[0])


for long, lat in line_coords:
    builder.add_circle_to_geojson((lat, long), radius=1, alpha=0.1)


builder.save_to_file("test.json")