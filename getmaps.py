"""
getmaps.py
A custom Location class and a series of functions used to perform a request to
either the ArcGIS or Mapbox REST APIs to return a static map image
"""

from typing import List, Tuple
import json
import sys
from shapely.geometry import MultiPoint, Polygon
from latlon_to_bng import WGS84toOSGB36 as lat_long_to_x_y
import requests
import pyodbc


class Location:
    """
    Represents a geographical location associated with a UPRN
    """
    def __init__(
            self,
            x: str,
            y: str,
            lat: str,
            lng: str,
            address: str,
            street: str,
            town: str,
            postcode: str,
            uprn: str,
            rounds: List[str]):
        """
        Args:
            x (str): The x-coordinate of this location
            y (str): The y-coordinate of this location
            lat (str): The latitude of this location
            lng (str): The longitude of this location
            address (str): The full address of this location
            street (str): The street this location is on
            town (str): The town this location is in
            postcode (str): The postcode this location is in
            uprn (str): The UPRN of this location
            rounds (List[str]): The rounds this location is under
        """
        self.x = x
        self.y = y
        self.lat = lat
        self.lng = lng
        self.address = address
        self.street = street
        self.town = town
        self.postcode = postcode
        self.uprn = uprn
        self.rounds = rounds

    def print_location(self):
        """
        Prints the values stored in each variable. Each line is formatted
        <name>: <value>
        """
        for attr, value in self.__dict__.items():
            print(f'{attr}: {value}')

    def __iter__(self):
        """
        Overrides the bult-in __iter__ method to return a list of a
        Location's attributes
        """
        return iter([
            self.x,
            self.y,
            self.lat,
            self.lng,
            self.address,
            self.street,
            self.town,
            self.postcode,
            self.uprn,
            self.rounds])


def database_connect(config_path: str) -> pyodbc.Connection:
    """
    Creates a connection to a SQL Server database
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the connection string parameters
    Returns:
        pyodbc.Connection: A Connection object used as a connection
        to the database
    """
    with open(config_path, 'r') as config_f:
        config = json.load(config_f)
    return pyodbc.connect(
        driver=config['driver'],
        server=config['server'],
        database=config['database'],
        uid=config['uid'],
        pwd=config['pwd'])


def get_uprn_from_input() -> str:
    """
    Gets the UPRN as a command line argument, or prompts the user for
    input if no command line argument exists
    Returns:
        str: The UPRN input by the user
    Raises:
        ValueError: If there is more than one argument or if the
        argument isn't a valid UPRN
    """
    # If there are too many arguments
    if len(sys.argv) > 2:
        raise ValueError(f'{len(sys.argv) -1} arguments found (1 max)')
    # If there is one extra argument found, check validity
    if len(sys.argv) == 2:
        uprn = sys.argv[1]
        if len(uprn) != 12:
            raise ValueError(f'{uprn} is not a valid UPRN')
        return uprn
    # If no arguments are found, prompt for input
    uprn = input('Enter a 12-digit UPRN: ')
    return uprn


def get_location_from_uprn(conn: pyodbc.Connection, uprn: str) -> Location:
    """
    Queries the SQL database for the X, Y, latitude, longitude and address
    associated with a UPRN and creates a Location object out of it
    Args:
        conn (pyodbc.Connection): The connection to the database to query
        uprn (str): The UPRN to query with
    Returns:
        Location: The Location object containing the latitude, longitude and
        address of the given UPRN, as well as the UPRN itself
    """
    with open('.\\get_location.sql', 'r') as loc_query_f:
        loc_query = loc_query_f.read()
    cursor = conn.cursor()
    cursor.execute(loc_query, uprn)
    loc = cursor.fetchone()
    return Location(
        str(loc.x),
        str(loc.y),
        str(loc.lat),
        str(loc.lng),
        loc.addr,
        loc.street,
        loc.town,
        loc.postcode,
        uprn,
        [loc.REF, loc.RECY, loc.MIX, loc.GLASS, loc.GW])


def get_all_locations(conn: pyodbc.Connection) -> List[Location]:
    """
    Queries the SQL database for every X, Y, latitude, longitude, address
    and UPRN under a specific constraint and creates a list of location
    objects containing each one
    Args:
        conn (pyodbc.Connection): The connection to the database to query
    Returns:
        List[Location]: A list of Location objects containing information
        about the locations returned by the SQL query
    """
    locations = []
    with open('.\\get_all_locations_per_round.sql', 'r') as loc_query_f:
        loc_query_all = loc_query_f.read()
    cursor = conn.cursor()
    cursor.execute(loc_query_all)
    locs = cursor.fetchall()
    for loc in locs:
        locations.append(Location(
            '{:.2f}'.format(loc.x),
            '{:.2f}'.format(loc.y),
            '{:.15f}'.format(loc.lat),
            '{:.15f}'.format(loc.lng),
            loc.addr,
            loc.street,
            loc.town,
            loc.postcode,
            str(loc.uprn),
            [loc.REF, loc.RECY, loc.MIX, loc.GLASS, loc.GW]))
    return locations


def get_arcgis_map(
        location: Location,
        scale: str,
        x_size: int,
        y_size: int,
        dpi: int,
        prefix: str) -> None:
    """
    Uses the Requests library and the ArcGIS API to download a static map
    image of the location
    Args:
        location (Location): The location to get a map for
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
        dpi (int): The DPI of the output image (default is 96)
        prefix(str): The filename prefix to save the file with
    """
    map_uri = 'https://ccvgisapp01:6443/arcgis/rest/services/Printing/' \
        'HDCExportWebMap/GPServer/Export Web Map/execute'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    web_map = _get_json(location.x, location.y, scale, x_size, y_size, dpi)
    payload = {
        'Web_Map_as_JSON': web_map,
        'Format': 'JPG',
        'f': 'json',
        'Layout_Template': 'MAP_ONLY'}
    cafile = '.\\cacert.pem'
    req = requests.post(map_uri, headers=headers, data=payload, verify=cafile)
    if req.status_code == 200:
        # Returns a JSON formatted bytes type
        resp = req.content.decode('utf8')
        img_url = json.loads(resp)['results'][0]['value']['url']
        img_req = requests.get(img_url)
        img_path = f'./img/{prefix}-{scale}.jpg'
        with open(img_path, 'wb') as image_f:
            image_f.write(img_req.content)


def _get_json(
        x: str,
        y: str,
        scale: str,
        x_size: int,
        y_size: int,
        dpi: int) -> str:
    """
    Loads the JSON template from file, fills in the x and y values and
    removes the whitespace so it can be passed as a parameter to the ArcGIS API
    Args:
        x (str): The x-coordinate of the location
        y (str): The y-coordinate of the location
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
        dpi (int): The DPI of the output image (default is 96)
    Returns:
        string: The filled in and formatted JSON template as a string
    """
    with open('.\\web_map.json', 'r') as web_map_f:
        web_map = json.load(web_map_f)
    web_map['mapOptions']['extent']['xmin'] = x
    web_map['mapOptions']['extent']['xmax'] = x
    web_map['mapOptions']['extent']['ymin'] = y
    web_map['mapOptions']['extent']['ymax'] = y
    web_map['mapOptions']['scale'] = scale
    web_map['exportOptions']['outputSize'] = [x_size, y_size]
    web_map['exportOptions']['dpi'] = dpi
    return str(web_map)


def get_clustered_map(
        postcodes: List['Postcode'],
        scale: str,
        circle_size: int,
        outline_width: float,
        x_size: int,
        y_size: int,
        dpi: int,
        prefix: str) -> None:
    """
    Uses the Requests library and the ArcGIS API to download a static map
    image of a cluster of locations, with each location highlighted with
    a marker
    Args:
        cluster (List[Location]): The cluster of locations to display on a map
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        circle_size (int): The radius of the circle markers
        outline_width (float): The width of the circle marker outline
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
        dpi (int): The DPI of the output image (default is 96)
        prefix(str): The filename prefix to save the file with
    """
    map_uri = 'https://ccvgisapp01:6443/arcgis/rest/services/Printing/' \
        'HDCExportWebMap/GPServer/Export Web Map/execute'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    web_map = _get_json_from_postcodes(
        scale,
        circle_size,
        outline_width,
        postcodes,
        x_size,
        y_size,
        dpi)
    payload = {
        'Web_Map_as_JSON': web_map,
        'Format': 'JPG',
        'f': 'json',
        'Layout_Template': 'MAP_ONLY'}
    cafile = '.\\cacert.pem'
    req = requests.post(map_uri, headers=headers, data=payload, verify=cafile)
    if req.status_code == 200:
        # Returns a JSON formatted bytes type
        resp = req.content.decode('utf8')
        img_url = json.loads(resp)['results'][0]['value']['url']
        img_req = requests.get(img_url)
        img_path = f'./img/{prefix}-{scale}.jpg'
        with open(img_path, 'wb') as image_f:
            image_f.write(img_req.content)


def _get_json_from_postcodes(
        scale: str,
        circle_size: int,
        outline_width: float,
        postcodes: List['Postcode'],
        x_size: int,
        y_size: int,
        dpi: int) -> str:
    """
    Loads the JSON template from file, fills in the x and y values and
    removes the whitespace so it can be passed as a parameter to the ArcGIS API
    Unless this is an overview map, a single-element Postcode list will be
    passed in
    Args:
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        circle_size (int): The radius of the circle markers
        outline_width (float): The width of the circle marker outline
        postcodes (List[Postcode]): The list of Postcode objects to draw as
        features on the map
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
        dpi (int): The DPI of the output image (default is 96)
    Returns:
        string: The filled in and formatted JSON template as a string
    """
    with open('.\\web_map_clustered.json', 'r') as web_map_f:
        web_map = json.load(web_map_f)
    (x, y) = _get_centroid(postcodes)
    web_map['mapOptions']['extent']['xmin'] = x
    web_map['mapOptions']['extent']['xmax'] = x
    web_map['mapOptions']['extent']['ymin'] = y
    web_map['mapOptions']['extent']['ymax'] = y
    web_map['mapOptions']['scale'] = scale
    web_map['operationalLayers'] = _convert_postcodes_to_layers(
        postcodes, circle_size, outline_width)
    web_map['exportOptions']['outputSize'] = [x_size, y_size]
    web_map['exportOptions']['dpi'] = dpi
    return json.dumps(web_map)


def _get_centroid(postcodes: List['Postcode']) -> Tuple[float, float]:
    """
    Given a list of Postcode objects, flattens the list of Location objects
    found in each, gets the centre point of all the Location lat/long pairs
    and converts them to X/Y coordinates
    Args:
        postcodes (List[Postcode]): The Location objects containing the
        lat/long pairs
    Returns:
        Tuple(float, float): The X and Y coordinate of the centre point
    """
    lat_long_list = []
    for postcode in postcodes:
        for location in postcode.locations:
            lat_long_list.append([float(location.lat), float(location.lng)])
    # If there are less than three locations, the x and y need to be
    # calculated and input manually        
    if len(postcodes) < 3:
        return(lat_long_list[0][0], lat_long_list[0][1])
    elif len(postcodes) >= 3:
        poly = Polygon(lat_long_list)
        centroid_tuple = poly.centroid.coords[0]
    else:
        points = MultiPoint(lat_long_list)
        centroid_tuple = list(points.centroid.coords)[0]
    return lat_long_to_x_y(centroid_tuple[0], centroid_tuple[1])


def _convert_postcodes_to_layers(
        postcodes: List['Postcode'],
        circle_size: int,
        outline_width: int) -> dict:
    """
    Converts the list of Location objects in a Postcode object to a JSON array
    to be used in ArcGIS's ExportWebMap JSON
    Args:
        cluster (List[Location]): The cluster of Location objects to draw as
        features on the map
    Returns:
        str: The operationalLayers array containing the cluster locations as a
        JSON-style dict
    """
    operational_layers = []
    for postcode in postcodes:
        features = []
        for location in postcode.locations:
            feature = {}
            geometry = {}
            geometry['x'] = float(location.x)
            geometry['y'] = float(location.y)
            geometry['spatialReference'] = {}
            geometry['spatialReference']['wkid'] = 27700
            feature['geometry'] = geometry
            features.append(feature)
        feature_set = {}
        feature_set['features'] = features
        layers = {}
        layer_definition = {}
        layer_definition['name'] = 'pointLayer'
        layer_definition['geometryType'] = 'esriGeometryPoint'
        layer_definition['drawingInfo'] = {}
        layer_definition['drawingInfo']['renderer'] = {}
        layer_definition['drawingInfo']['renderer']['type'] = 'simple'
        layer_definition['drawingInfo']['renderer']['symbol'] = {}
        layer_definition['drawingInfo']['renderer']['symbol']['type'] = 'esriSMS'
        layer_definition['drawingInfo']['renderer']['symbol']['style'] = 'esriSMSCircle'
        layer_definition['drawingInfo']['renderer']['symbol']['color'] = postcode.fill_colour
        layer_definition['drawingInfo']['renderer']['symbol']['size'] = circle_size
        layer_definition['drawingInfo']['renderer']['symbol']['outline'] = {}
        layer_definition['drawingInfo']['renderer']['symbol']['outline']['color'] = postcode.outline_colour
        layer_definition['drawingInfo']['renderer']['symbol']['outline']['width'] = outline_width
        layers['layerDefinition'] = layer_definition
        layers['featureSet'] = feature_set
        feature_collection = {}
        feature_collection['layers'] = [layers]
        operational_layer = {}
        operational_layer['id'] = postcode.postcode
        operational_layer['opacity'] = 0.9
        operational_layer['featureCollection'] = feature_collection
        operational_layers.append(operational_layer)
    basic_layer = {}
    basic_layer['id'] = 'Default1_5042'
    basic_layer['title'] = 'Basic Layers'
    basic_layer['opacity'] = 1
    basic_layer['minScale'] = 0
    basic_layer['maxScale'] = 0
    basic_layer['url'] = 'https://ccvgisapp01:6443/arcgis/rest/services/Portal/Default1/MapServer'
    basic_layer['visibleLayers'] = [0, 12, 14, 15]
    operational_layers.append(basic_layer)
    return operational_layers
