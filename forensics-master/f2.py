from geopy.distance import distance
from geopy.point import Point

def generate_covering_points(center_lat, center_lon):
    center = Point(center_lat, center_lon)
    angles = [0, 120, 240]
    radius_km = 1.0
    return [distance(kilometers=radius_km).destination(center, angle) for angle in angles] + [center]

def generate_kml(points, output_file='points.kml'):
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>\n'''
    kml_footer = '</Document>\n</kml>'

    placemarks = ''
    for i, pt in enumerate(points, start=1):
        placemarks += f'''  <Placemark>
    <name>Point {i}</name>
    <Point><coordinates>{pt.longitude},{pt.latitude},0</coordinates></Point>
  </Placemark>\n'''

    with open(output_file, 'w') as f:
        f.write(kml_header + placemarks + kml_footer)
    print(f"KML file saved as: {output_file}")

# Example usage
def gp(center_coord = (-17.3854389, -66.1606556)):
    return generate_covering_points(*center_coord)


def generate_circles_kml(points, radius_km, num_points=100, output_file='circles.kml'):
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>\n'''
    kml_footer = '</Document>\n</kml>'
    placemarks = ''

    for i, center in enumerate(points, start=1):
        angle_step = 360 / num_points
        coordinates = []
        for j in range(num_points + 1):
            angle = j * angle_step
            point = distance(kilometers=radius_km).destination(center, angle)
            coordinates.append(f"{point.longitude},{point.latitude},0")
        
        placemarks += f'''  <Placemark>
    <name>Circle {i}</name>
    <Style>
      <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
      <PolyStyle><color>220000ff</color></PolyStyle>
    </Style>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>
            {' '.join(coordinates)}
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>\n'''

    with open(output_file, 'w') as f:
        f.write(kml_header + placemarks + kml_footer)

    print(f"KML with {len(points)} circles saved as: {output_file}")

# Example usage

generate_circles_kml(gp()[:-1], radius_km=1.0)  # 1 km radius = 2 km diameter
