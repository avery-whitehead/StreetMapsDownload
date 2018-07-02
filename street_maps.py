"""
street_maps.py
How to run:
Install pyodbc version 4.0.22 or greater
From the command line, run `py -3 resolve_uprn.py [uprn]`, or leave the
UPRN field blank and be prompted at the command line
How it works:
Given a UPRN as input, uses it to resolve latitude, longitude and
address. Uses these values to create a static MapBox image
"""

import json
import sys
import requests
import pyodbc

class Location:
    """
    Represents a geographical location associated with a UPRN
    """
    def __init__(self, lat: str, lng: str, address: str, uprn: str):
        """
        Args:
            lat (str): The latitude of this location
            lng (str): The longitude of this location
            address (str): The address of this location
            uprn (str): The UPRN of this location
        """
        self.lat = lat
        self.lng = lng
        self.address = address
        self.uprn = uprn

    def print_location(self):
        """
        Prints the values stored in each variable. Each line is formatted
        <name>: <value>
        """
        for attr, value in self.__dict__.items():
            print(f'{attr}: {value}')


def database_connect(config_path: str) -> pyodbc.Connection:
    """
    Creates a connection to a SQL Server database
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the connection string parameters
    Returns:
        pyodbc.Connection: A Connection object used as a connection
        to the database
    Raises:
        pyodbc.DatabaseError, pyodbc.InterfaceError: If the connection
        fails
    """
    with open (config_path, 'r') as config_f:
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
    Queries the SQL database for the latitude, longitude and address
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
    return Location(loc.lat, loc.lng, loc.address, uprn)

def get_map(location: Location, zoom: str, width: str, height: str) -> None:
    """
    Uses the Requests library and the Mapbox API to download a static map
    image of the location
    Args:
        location (Location): The location to get a map for
        zoom (str): The zoom level of the map (minimum 0, maximum 20)
        width (str): The width of the image (px)
        height (str): The height of the image (px)
    """
    with open('./mapbox.key', 'r') as key_f:
        access_token = key_f.read()
    map_uri = 'https://api.mapbox.com/styles/v1/mapbox/streets-v10/static/' \
    f'{location.lng},{location.lat},{zoom},0,0/{width}x{height}?' \
    f'access_token={access_token}'
    # Download image to file
    req = requests.get(map_uri)
    if req.status_code == 200:
        with open(f'./img/{location.uprn}-{zoom}.png', 'wb') as image_f:
            image_f.write(req.content)


if __name__ == '__main__':
    try:
        # Connect to the database
        connection = database_connect('.\\.config')
        # Get the UPRN from command line arguments or user input
        uprn = get_uprn_from_input()
        location = get_location_from_uprn(connection, uprn)
        location.print_location()
        get_map(location, 14, 600, 600)
    except (pyodbc.DatabaseError, pyodbc.InterfaceError, ValueError) as error:
        print(error)
