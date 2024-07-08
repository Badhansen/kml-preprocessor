import os
import random
from pykml import parser
from pykml.factory import KML_ElementMaker as KML
from lxml import etree


def extract_details_from_kml(file_path):
    with open(file_path) as f:
        doc = parser.parse(f)

    polygons = {}
    
    for placemark in doc.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        # Get placemark name
        placemark_name = placemark.name.text.strip() if placemark.name is not None else "Unnamed Placemark"
        
        # Check if the placemark contains a polygon
        polygon = placemark.find('.//{http://www.opengis.net/kml/2.2}Polygon')
        if polygon is not None:
            # Extract coordinates of the polygon
            coordinates = polygon.outerBoundaryIs.LinearRing.coordinates.text.strip()
            # Split the coordinates string into individual points
            points = coordinates.split()
            # polygons[placemark_name] = coordinates
            # # Print the placemark name
            # print("Placemark:", placemark_name)
            # # Print the points of the polygon
            # print("Polygon:")
            polygon_points = []
            for point in points:
                lon, lat, _ = point.split(',')
                polygon_points.append((lon, lat))
                # print(f"Longitude: {lon}, Latitude: {lat}")
            polygons[placemark_name] = polygon_points

    random_key = random.choice(list(polygons.keys()))
    # print(polygons[random_key])
    # print('Total polygons: ', len(polygons))
    return polygons

def create_kml_from_placemark_polygons(placemark_data, file_path):
    # Create a KML document
    filename = os.path.basename(file_path)
    kml_doc = KML.kml(
        KML.Document(
            KML.name(filename)
        )
    )
    index = 1
    # Iterate through the placemark data and create placemarks with polygons
    for placemark_name, polygon_coordinates in placemark_data.items():
        # Create placemark element
        placemark = KML.Placemark(
            KML.name(index),
            # KML.snippet(),
            # KML.description(cdata_content),
            KML.ExtendedData(),
            KML.Polygon(
                KML.outerBoundaryIs(
                    KML.LinearRing(
                        KML.coordinates(' '.join([f'{lon},{lat},0.0' for lon, lat in polygon_coordinates]))
                    )
                )
            )
            
        )
        # Append placemark to the document
        kml_doc.Document.append(placemark)
        index += 1

    # Create an ElementTree object and serialize it to a string
    kml_string = etree.tostring(kml_doc, pretty_print=True, encoding='utf-8', xml_declaration=True)

    # Save the KML string to a file
    with open(file_path, 'wb') as f:
        f.write(kml_string)

    print("KML file saved as " + file_name)


if __name__ == "__main__":
    folder_name = 'data'
    original_file_name = "DUBLIN_ORG.kml"
    file_name = "Dublin.kml"
    current_directory  = os.getcwd()
    # Construct the full folder path
    folder_path = os.path.join(current_directory, folder_name)
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    original_file_path = os.path.join(folder_path, original_file_name)
    save_file_path =  os.path.join(folder_path, file_name)
    
    data = extract_details_from_kml(original_file_path)
    create_kml_from_placemark_polygons(data, save_file_path)