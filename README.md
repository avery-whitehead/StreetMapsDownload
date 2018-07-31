## Street Maps Download

Produces a series of static map images using the ArcGIS REST API of a location's surrounding area at different elevation levels
GIS stuff, machine learning stuff and image processing stuff in one handy map-making bundle

## Main files

`main.py` - Regular single-location map

`main_postcodes.py` - Groups locations by postcodes and produces one map per postcode, as well as an overview map of every postcode

`main_clusters.py` - Uses DBSCAN to create clusters of locations and produces one map per cluster

## Library files

`colourgen.py` - Creates a list of n visually distinct colours used to label the markers on the map

`getmaps.py` - Constructs one or more [ExportWebMap](https://developers.arcgis.com/rest/services-reference/exportwebmap-specification.htm) JSON representations to be passed to the ArcGIS REST API, returning a URL of the web maps

`createprints.py` - Uses the Pillow imaging library to create an image of the web maps laid out on a A4-sized template, and converts the image to a PDF

`clustering.py` - Helper functions for `main_clusters.py`, uses the scikit-learn machine learning library's implementation of DBSCAN to create a list of clusters given a list of locations

## Examples

![example map](https://raw.githubusercontent.com/james-whitehead/StreetMapsDownload/master/examples/overview.jpg)
(Left) An overview map of every location group determined by postcode
(Middle and right) Higher-detail maps of two of the location groups found in the overview map