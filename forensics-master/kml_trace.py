import csv
from geopy.distance import distance
from geopy.point import Point

def read_bts(filename):
    bts_data = {}
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bts_data[row['BTS_ID']] = {
                'name': row['TowerName'],
                'lat': float(row['Latitude']),
                'lon': float(row['Longitude'])
            }
    return bts_data

def read_cdr(filename):
    cdr_data = []
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cdr_data.append({
                "source": row["Source"],
                "destination": row["Destination"],
                "datetime": row["DateTime"],
                "type": row["Type"],
                "bts": row["BTS_ID"]
            })
    return cdr_data

def generate_bts_circle(lat, lon, radius_km=1.0, points=60):
    center = Point(lat, lon)
    return ' '.join(
        f"{distance(kilometers=radius_km).destination(center, i * (360 / points)).longitude},"
        f"{distance(kilometers=radius_km).destination(center, i * (360 / points)).latitude},0"
        for i in range(points + 1)
    )

def create_kml(bts_data, cdr_movements, output_file="forensic_case.kml"):
    kml = ['''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document>''']

    # BTS Circles and Markers
    for bts_id, data in bts_data.items():
        lat, lon = data['lat'], data['lon']
        name = data['name']
        circle = generate_bts_circle(lat, lon)
        kml.append(f'''
<Placemark>
  <name>{name} ({bts_id})</name>
  <Style>
    <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
    <PolyStyle><color>220000ff</color></PolyStyle>
  </Style>
  <Polygon>
    <outerBoundaryIs>
      <LinearRing><coordinates>{circle}</coordinates></LinearRing>
    </outerBoundaryIs>
  </Polygon>
</Placemark>
<Placemark>
  <name>{name} (Tower)</name>
  <Point><coordinates>{lon},{lat},0</coordinates></Point>
</Placemark>''')

    # Communication points and optional device route
    last_position = {}
    for record in cdr_movements:
        bts_id = record["bts"]
        if bts_id not in bts_data:
            continue
        bts_info = bts_data[bts_id]
        lat, lon = bts_info['lat'], bts_info['lon']
        src = record["source"]
        label = f'{record["type"].upper()} from {record["source"]} to {record["destination"]} @ {record["datetime"]}'
        kml.append(f'''
<Placemark>
  <name>{label}</name>
  <Style><LineStyle><color>ff00ff00</color><width>2</width></LineStyle></Style>
  <Point><coordinates>{lon},{lat},0</coordinates></Point>
</Placemark>''')
        if src in last_position:
            prev_lat, prev_lon = last_position[src]
            kml.append(f'''
<Placemark>
  <name>Route {src}</name>
  <LineString>
    <coordinates>
      {prev_lon},{prev_lat},0
      {lon},{lat},0
    </coordinates>
  </LineString>
</Placemark>''')
        last_position[src] = (lat, lon)

    kml.append('</Document></kml>')
    with open(output_file, 'w') as f:
        f.write('\n'.join(kml))
    print(f"KML saved to {output_file}")

# Example usage
bts_data = read_bts("bts.csv")
cdr_data = read_cdr("cdr.csv")
create_kml(bts_data, cdr_data)
