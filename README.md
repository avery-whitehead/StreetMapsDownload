## Street Maps Download

Produces a series of static map images using the ArcGIS REST API of a location's surrounding area at different elevation levels
GIS stuff, machine learning stuff and image processing stuff in one handy map-making bundle

## Main files

`main.py` - Regular single-location map

`main_postcodes.py` - Groups locations by postcodes and produces one map per postcode, as well as an overview map of every postcode

`main_clusters.py` - Uses DBSCAN to create clusters of locations and produces one map per cluster

## Library files

`colourgen.py` - Creates a list of n visually distinct colours used to label the markers on the map, used in all main files

`getmaps.py` - Constructs one or more [ExportWebMap](https://developers.arcgis.com/rest/services-reference/exportwebmap-specification.htm) JSON representations to be passed to the ArcGIS REST API, returning a URL of the web maps, used in all main files

`createprints.py` - Uses the Pillow imaging library to create an image of the web maps laid out on a A4-sized template and converts the image to a PDF, used in all main files

`clustering.py` - Uses the scikit-learn machine learning library's implementation of DBSCAN to create a list of clusters given a list of locations, used in `main_clusters.py`

### JSON files

`web_map.json` - Basic ExportWebMap representation for a single location, used in `main.py`

`web_map_clustered.json` - Extension of `web_map.json` to allow for multiple locations to be marked on each map, used in `main_postcodes.py` and `main_clusters.py`

### SQL files

`get_location.sql` - Returns some geodetic info (WGS84 latitudes and longitudes, OSGB36 easting and northings) and some address data for a single location, used in `main.py`

`get_all_locations.sql` - Returns the same geodetic and address info, but for an arbitrary number of locations, used in `main_postcodes.py` and `main_clusters.py`

## Example

![example map](https://raw.githubusercontent.com/james-whitehead/StreetMapsDownload/master/examples/overview.jpg)
(Left) An overview map of every location group determined by postcode  
(Middle and right) Higher-detail maps of two of the location groups found in the overview map