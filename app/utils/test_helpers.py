from shapely.geometry import Point, LineString
from geoalchemy2.shape import to_shape, from_shape

def create_test_point(x, y, srid=4326):
    """Create a PostGIS point geometry from coordinates"""
    point = Point(x, y)
    return from_shape(point, srid=srid)

def create_test_linestring(coordinates, srid=4326):
    """Create a PostGIS linestring geometry from coordinates"""
    line = LineString(coordinates)
    return from_shape(line, srid=srid)