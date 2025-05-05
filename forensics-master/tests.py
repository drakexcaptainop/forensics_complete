import geojson 
import geopy_utils as gu
import triangulation as T
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime


p = (gu.read_geojson('r.j'))
coords = (gu.extract_coordinates_by_marker_color(p, "#000000"))
towers = gu.read_coordinates_from_csv('longlat_output.csv')
builder = geojson.GeoJSONBuilder.get_base_geojson()
call_coords = geojson.GeoJSONBuilder.extract_coordinates('calls.json')


def make_frames(coords, times, labels):
    """
    Create a matplotlib animation that plots coordinates based on times, draws lines between points, and adds labels.
    :param coords: List of coordinates to plot.
    :param times: List of corresponding datetime objects for the coordinates.
    :param labels: List of labels for each coordinate.
    """
    # Convert datetime objects to relative time in seconds
    start_time = min(times)
    relative_times = [(t - start_time).total_seconds() for t in times]

    fig, ax = plt.subplots()
    x_data, y_data = [], []
    scatter = ax.scatter([], [], c='blue')
    line, = ax.plot([], [], c='red')
    annotations = []  # Store annotation objects

    def init():
        padding = 0.01  # Add padding to the axis limits
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        ax.set_xlim(min(x_coords) - padding, max(x_coords) + padding)
        ax.set_ylim(min(y_coords) - padding, max(y_coords) + padding)
        return scatter, line

    def update(frame):
        x_data.append(coords[frame][0])
        y_data.append(coords[frame][1])
        scatter.set_offsets(list(zip(x_data, y_data)))
        if frame > 0:  # Only add lines between consecutive points
            line.set_data(x_data[:frame + 1], y_data[:frame + 1])  # Ensure no line wraps back to the first point

        # Add label for the current point
        annotation = ax.annotate(labels[frame], (coords[frame][0], coords[frame][1]), fontsize=8, color='black')
        annotations.append(annotation)

        return scatter, line, *annotations

    ani = FuncAnimation(fig, update, frames=len(relative_times), 
                        init_func=init, blit=True,
                       )
    plt.show()
def process_calls(towers, call_coords, method='triangle',save_path='output.geojson', builder=None,
                  fill_color="#0000ff", line_color="#0000ff", alpha=0.1, 
                  route_circle_color="#0000ff", route_circle_alpha=0.1, tooltips=None,
                   add_true=False, date_times=None):
    """
    Process call coordinates to find closest towers, perform triangulation, and update the GeoJSON builder.
    :param p: GeoJSON data.
    :param coords: Coordinates extracted from GeoJSON.
    :param towers: List of tower coordinates.
    :param builder: GeoJSON builder instance.
    :param call_coords: List of call coordinates.
    """
    if builder is None:
        builder = geojson.GeoJSONBuilder.get_base_geojson()
    n = 3
    t1 = T.Tower.closest_tower(towers, call_coords[0][::-1], radius=1)
    t2 = T.Tower.closest_tower(towers, call_coords[-1][::-1], radius=1)

    builder.add_circle_to_geojson((t1.longitude, t1.latitude), radius=.1, alpha=0.1, color=fill_color)
    builder.add_circle_to_geojson((t2.longitude, t2.latitude), radius=.1, alpha=0.1, color=fill_color)

    prev = t1.longitude, t1.latitude
    for i in range(0, len(call_coords) - n + 1):
        c1 = T.Tower.closest_tower(towers, call_coords[i][::-1], radius=1)
        c2 = T.Tower.closest_tower(towers, call_coords[i + 1][::-1], radius=1)
        c3 = T.Tower.closest_tower(towers, call_coords[i + 2][::-1], radius=1)

        # Generate random colors
        color_c1 = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        color_c2 = color_c1
        color_c3 = color_c2

        if add_true:
            builder.add_marker(call_coords[i][::-1])
            builder.add_marker(call_coords[i + 1][::-1])
            builder.add_marker(call_coords[i + 2][::-1])
        
        if tooltips:
            builder.add_circle_to_geojson((c1.longitude, c1.latitude), radius=1, alpha=alpha, color=fill_color, tooltip=tooltips[i])
            builder.add_circle_to_geojson((c2.longitude, c2.latitude), radius=1, alpha=alpha, color=fill_color, tooltip=tooltips[i + 1])
            builder.add_circle_to_geojson((c3.longitude, c3.latitude), radius=1, alpha=alpha, color=fill_color, tooltip=tooltips[i + 2])

        else:
            builder.add_circle_to_geojson((c1.longitude, c1.latitude), radius=1, alpha=alpha, color=fill_color)
            builder.add_circle_to_geojson((c2.longitude, c2.latitude), radius=1, alpha=alpha, color=fill_color)
            builder.add_circle_to_geojson((c3.longitude, c3.latitude), radius=1, alpha=alpha, color=fill_color)

        try:
            if method == 'triangle':
                # Perform triangulation
                lon, lat = T.Triangulation.triangulate_position(c1, c2, c3)
            elif method == 'intersection':
                # Perform intersection
                lon, lat = T.Triangulation.calculate_position(c1, c2, c3)
            builder.add_circle_to_geojson((lon, lat), radius=.1, alpha=route_circle_alpha, color=route_circle_color, tooltip=tooltips[i] if tooltips else None) 
        except Exception as e:
            builder.add_circle_to_geojson((c1.longitude, c1.latitude), radius=0.1, alpha=route_circle_alpha, color=route_circle_color, tooltip=tooltips[i] if tooltips else None)

        builder.add_line_to_geojson([prev, (lon, lat)])
        prev = (lon, lat)
        if add_true:
            builder.add_marker(call_coords[i][::-1])

    for i in range(len(call_coords) - n + 1, len(call_coords)):
        pass

    builder.add_line_to_geojson([prev, (t2.longitude, t2.latitude)])
    if save_path is not None:
        builder.save_to_file(save_path)
    # Example usage
    return builder 



# Example usage

def test_make_frames():
    """
    Test the make_frames function by providing sample coordinates and times as datetime objects.
    """
    sample_coords = [(1, 1), (2, 2), (3, 3), (4, 4)]
    sample_times = [
        datetime(2023, 10, 1, 12, 0, 0),
        datetime(2023, 10, 1, 12, 0, 10),
        datetime(2023, 10, 1, 12, 0, 20),
        datetime(2023, 10, 1, 12, 0, 30)
    ]
    try:
        make_frames(sample_coords, sample_times)
        print("test_make_frames: Passed")
    except Exception as e:
        print(f"test_make_frames: Failed with error: {e}")


#test_make_frames()

def get_radio_base_info_from_coordinates(radios_csv_path, coordinates, output_csv_path='output_data.csv', epsilon=0.01): 
    """
    Retrieve radio base information based on coordinates and write the data to a CSV file.
    :param radios_csv_path: Path to the CSV file containing radio base data.
    :param coordinates: List of (longitude, latitude) tuples.
    :param output_csv_path: Path to save the output CSV file.
    :param epsilon: Allowed difference for matching coordinates.
    :return: List of matching data rows.
    """
    import pandas as pd
    import numpy as np

    radios = pd.read_csv(radios_csv_path)

    # Clean and convert 'Longitud' and 'Latitud' columns
    def clean_and_convert(value):
        try:
            value = value.replace(',', '.').strip()
            if value in ['..', '--'] or '\n' in value:
                return np.nan
            return float(value)
        except:
            return np.nan

    radios['Longitud'] = radios['Longitud'].apply(clean_and_convert)
    radios['Latitud'] = radios['Latitud'].apply(clean_and_convert)

    # Drop rows with invalid coordinates
    radios = radios.dropna(subset=['Longitud', 'Latitud'])
    
    data = [] 
    for lat, lon in coordinates: 
        matching_rows = radios.loc[
            (radios['Longitud'].between(lon - epsilon, lon + epsilon)) & 
            (radios['Latitud'].between(lat - epsilon, lat + epsilon))
        ]
        if not matching_rows.empty:
            data.append(matching_rows)

    # Write matching data to a CSV file
    if data:
        result = pd.concat(data, ignore_index=True)
        result.to_csv(output_csv_path, index=False)
        print(f"Data successfully written to {output_csv_path}")
    else:
        print("No matching data found.")
    
    return data


#print(get_radio_base_info_from_coordinates('/Users/jorgebarahona/Downloads/output (1).csv', geojson.GeoJSONBuilder.extract_coordinates('sospechoso1.json')))

def read_person_csv(csv_path, filter=False, source_filter=None):
    """
    Read a CSV file with fields 'Date-Time', 'Source', 'Destination', 'Event Type' 
    and filter data by the 'Source' column to match the provided argument.
    
    :param csv_path: Path to the CSV file.
    :param source_filter: Value to filter the 'Source' column.
    :return: Filtered DataFrame.
    """
    import pandas as pd

    try:
        # Read the CSV file
        data = pd.read_csv(csv_path)

        required_columns = ['Date-Time', 'Source', 'Destination', 'Event Type']
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"CSV file must contain the following columns: {required_columns}")
        if filter:

        # Filter data by 'Source'
            filtered_data = data[data['Source'] == source_filter]
        else:
            filtered_data = data

        return filtered_data
    except Exception as e:
        print(f"Error reading or processing the CSV file: {e}")
        return None

# Example usage:
# filtered_data = read_person_csv('person_data.csv', 'John Doe')
# print(filtered_data)

def read_person_xlxs(xlxs_path, source_filter):
    """
    Read an Excel file with fields 'Date-Time', 'Source', 'Destination', 'Event Type' 
    and filter data by the 'Source' column to match the provided argument.
    
    :param xlxs_path: Path to the Excel file.
    :param source_filter: Value to filter the 'Source' column.
    :return: Filtered DataFrame.
    """
    import pandas as pd

    try:
        # Read the Excel file
        data = pd.read_excel(xlxs_path)

        # Ensure required columns exist
        required_columns = ['Date-Time', 'Source', 'Destination', 'Event Type']
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"Excel file must contain the following columns: {required_columns}")

        # Filter data by 'Source'
        filtered_data = data[data['Source'] == source_filter]

        return filtered_data
    except Exception as e:
        print(f"Error reading or processing the Excel file: {e}")
        return None

# Example usage:

def make_frames_multiple(*args, labels_list=None, interval=200, legend_labels=None, save_path=None, dpi=1300):
    """
    Create a matplotlib animation that plots multiple sets of coordinates and times in the same frame.
    :param args: Tuples of (coords, times, color) for each dataset.
    :param labels_list: List of lists of labels for each dataset.
    :param interval: Time in milliseconds between updates.
    :param legend_labels: List of labels for the legend corresponding to each dataset.
    :param save_path: Path to save the animation file (e.g., 'animation.mp4').
    """
    if labels_list is None:
        labels_list = [None] * len(args)
    if legend_labels is None:
        legend_labels = [f"Dataset {i+1}" for i in range(len(args))]

    fig, ax = plt.subplots()
    scatter_list = []
    line_list = []
    annotations_list = [[] for _ in args]  # Store annotation objects for each dataset

    # Initialize scatter and line objects for each dataset
    for _, _, color in args:
        scatter = ax.scatter([], [], c=color, label=legend_labels[len(scatter_list)])
        line, = ax.plot([], [], c=color)
        scatter_list.append(scatter)
        line_list.append(line)

    def init():
        padding = 0.01  # Add padding to the axis limits
        all_x_coords = [c[1] for coords, _, _ in args for c in coords]
        all_y_coords = [c[0] for coords, _, _ in args for c in coords]
        ax.set_xlim(min(all_x_coords) - padding, max(all_x_coords) + padding)
        ax.set_ylim(min(all_y_coords) - padding, max(all_y_coords) + padding)
        return scatter_list + line_list

    def update(frame):
        for i, ((coords, times, color), scatter, line, annotations, labels) in enumerate(zip(args, scatter_list, line_list, annotations_list, labels_list)):
            x_data = [coords[j][1] for j in range(frame + 1)]
            y_data = [coords[j][0] for j in range(frame + 1)]
            scatter.set_offsets(list(zip(x_data, y_data)))
            if frame > 0:  # Only add lines between consecutive points
                line.set_data(x_data, y_data)

            # Add labels for the current point if labels are provided
            if labels and frame < len(labels):  # Ensure frame index is within bounds
                annotation = ax.annotate(labels[frame], (coords[frame][1], coords[frame][0]), fontsize=8, color='black')
                annotations.append(annotation)

        # Remove old annotations to avoid clutter
        for annotations in annotations_list:
            while len(annotations) > frame + 1:
                annotations.pop(0).remove()

        return scatter_list + line_list + [ann for annotations in annotations_list for ann in annotations]

    ani = FuncAnimation(fig, update, frames=len(args[0][1]), init_func=init, blit=True, interval=interval)
    ax.legend()  # Add legend to the plot
    plt.grid(True)

    if save_path:
        ani.save(save_path, writer='ffmpeg', fps=1, dpi=dpi)  # Set dpi to 1080 for high resolution
        print(f"Animation saved to {save_path}")
    else:
        plt.show()

# Example usage:
# make_frames_multiple(...existing code..., save_path="output.mp4")

agcsv = read_person_csv('agustin_arandia_calls (1).csv', filter=True,  source_filter='Agustin Arandia')
antcsv = read_person_csv('antony_zeballos_calls (1).csv', filter=True,  source_filter='Antony Zeballos')
andcsv = read_person_csv('andrea_rojas_calls (1).csv', filter=True, source_filter='Andrea Rojas')



make_frames_multiple(
    (geojson.GeoJSONBuilder.extract_coordinates('sospechoso1.json'), agcsv['Date-Time'], 'blue'),
    (geojson.GeoJSONBuilder.extract_coordinates('sospechoso2.json'), antcsv['Date-Time'], 'red'),
    (geojson.GeoJSONBuilder.extract_coordinates('calls.json'), andcsv['Date-Time'], 'green'),
    labels_list=[
        [f'{agcsv["Destination"].iloc[i]}-{agcsv["Event Type"].iloc[i]}' for i in range(len(agcsv))],
        [f'{antcsv["Destination"].iloc[i]}-{antcsv["Event Type"].iloc[i]}' for i in range(len(antcsv))],
        [f'{andcsv["Destination"].iloc[i]}-{andcsv["Event Type"].iloc[i]}' for i in range(len(andcsv))],

    ],
    interval=1300,
    dpi = 1080,
    save_path="output.mp4",
    legend_labels=["Agustin Arandia", "Antoni Zeballos", "Andrea Rojas"],
)

def format_tooltip(agcsv, i):
    """
    Format the tooltip text for the GeoJSON builder.
    :return: Formatted tooltip text.
    """
    print(agcsv, agcsv.shape)
    date_time = agcsv['Date-Time'].iloc[i]   # Format Date-Time field
    return f"Fecha-Hora: {date_time}<br/>Origen: {agcsv['Source'].iloc[i]}<br/>Destino: {agcsv['Destination'].iloc[i]}<br/>Evento: {agcsv['Event Type'].iloc[i]}<br/>"
def process_cameras(builder: geojson.GeoJSONBuilder, cameras_geojson_path, cameras_info_csv_path, save_path=None, properties_to_change={}):
    import json, pandas as pd
    f = open(cameras_geojson_path)
    info = pd.read_csv(cameras_info_csv_path)
    print(info)
    # Date-Time,Location,Status
    data = json.load(f)
    f.close()
    features = data['features']
    for i, feature in enumerate(features):
        for prop, value in properties_to_change.items():
            feature['properties'][prop] = value
        feature['properties']['tooltip'] = f"Fecha-Hora: {info['Date-Time'].iloc[i]}<br/>Ubicacion: {info['Location'].iloc[i]}<br/>Estado: {info['Status'].iloc[i]}<br/>"
        builder.add_direct_feature( feature )
    if save_path is not None:
        builder.save_to_file(save_path)
    return builder 

builder = process_calls(towers,  call_coords #, save_path="andrea_rojas.geojson"
                        , builder=builder,
                        fill_color="#0000ff", line_color="#0000ff", alpha=0.1,
                        tooltips=[format_tooltip(andcsv, i) for i in range(6)] )

builder = process_calls(towers,  geojson.GeoJSONBuilder.extract_coordinates('sospechoso1.json') #, save_path="agustin_arandia.geojson"
                        , builder=builder,
                        fill_color="#00ff00",
                        tooltips=[format_tooltip(antcsv, i) for i in range(6)],)

builder = process_calls(towers,  geojson.GeoJSONBuilder.extract_coordinates('sospechoso2.json') #, save_path="antony_zeballos.geojson"
                        , builder=builder,
                        fill_color="#00ffff", 
                        tooltips=  [format_tooltip(agcsv, i) for i in range(6)])
process_cameras(builder, 'escenarios/camaras_asesino_completo.json',cameras_info_csv_path="cameras_csv/antony_zeballos.csv"
                #, save_path='antony_zeballos.geojson'
                , properties_to_change={'marker-color': '#ff0000'})
process_cameras(builder, 'escenarios/camaras_a.json', cameras_info_csv_path="cameras_csv/andrea_rojas.csv",  properties_to_change={'marker-color': '#ff0000'},
                )#save_path='andrea_rojas.geojson')
process_cameras(builder, 'escenarios/camaras_agustin.json', cameras_info_csv_path="cameras_csv/agustin_arandia.csv",  properties_to_change={'marker-color': '#ff0000'},
 save_path="ruta_completa.geojson") #save_path='agustin_arandia.geojson')
