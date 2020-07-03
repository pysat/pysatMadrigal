"""
tests the pysat coords area
"""
import numpy as np

from pysatMadrigal import coords


def test_geodetic_to_geocentric_single():
    """Test conversion from geodetic to geocentric coordinates"""

    lat, lon, rad = coords.geodetic_to_geocentric(45.0, lon_in=8.0)

    assert abs(lat - 44.807576784018046) < 1.0e-6
    assert abs(lon - 8.0) < 1.0e-6
    assert abs(rad - 6367.489543863465) < 1.0e-6


def test_geocentric_to_geodetic_single():
    """Test conversion from geocentric to geodetic coordinates"""

    lat, lon, rad = coords.geodetic_to_geocentric(45.0, lon_in=8.0,
                                                  inverse=True)

    assert abs(lat - 45.192423215981954) < 1.0e-6
    assert abs(lon - 8.0) < 1.0e-6
    assert abs(rad - 6367.345908499981) < 1.0e-6


def test_geodetic_to_geocentric_mult():
    """Test array conversion from geodetic to geocentric coordinates"""

    arr = np.ones(shape=(10,), dtype=float)
    lat, lon, rad = coords.geodetic_to_geocentric(45.0 * arr, lon_in=8.0 * arr)

    assert lat.shape == arr.shape
    assert lon.shape == arr.shape
    assert rad.shape == arr.shape
    assert abs(lat - 44.807576784018046).max() < 1.0e-6
    assert abs(lon - 8.0).max() < 1.0e-6
    assert abs(rad - 6367.489543863465).max() < 1.0e-6


def test_geocentric_to_geodetic_mult():
    """Test array conversion from geocentric to geodetic coordinates"""

    arr = np.ones(shape=(10,), dtype=float)
    lat, lon, rad = coords.geodetic_to_geocentric(45.0 * arr, lon_in=8.0 * arr,
                                                  inverse=True)

    assert lat.shape == arr.shape
    assert lon.shape == arr.shape
    assert rad.shape == arr.shape
    assert abs(lat - 45.192423215981954).max() < 1.0e-6
    assert abs(lon - 8.0).max() < 1.0e-6
    assert abs(rad - 6367.345908499981).max() < 1.0e-6


def test_geodetic_to_geocentric_inverse():
    """Tests the reversibility of geodetic to geocentric conversions"""

    lat1 = 37.5
    lon1 = 117.3
    lat2, lon2, rad_e = coords.geodetic_to_geocentric(lat1, lon_in=lon1,
                                                      inverse=False)
    lat3, lon3, rad_e = coords.geodetic_to_geocentric(lat2, lon_in=lon2,
                                                      inverse=True)
    assert abs(lon1 - lon3) < 1.0e-6
    assert abs(lat1 - lat3) < 1.0e-6


###############################################
# Geodetic / Geocentric Horizontal conversions

def test_geodetic_to_geocentric_horz_single():
    """Test conversion from geodetic to geocentric coordinates"""

    lat, lon, rad, az, el = \
        coords.geodetic_to_geocentric_horizontal(45.0, 8.0, 52.0, 63.0)

    assert abs(lat - 44.807576784018046) < 1.0e-6
    assert abs(lon - 8.0) < 1.0e-6
    assert abs(rad - 6367.489543863465) < 1.0e-6
    assert abs(az - 51.70376774257361) < 1.0e-6
    assert abs(el - 62.8811403841008) < 1.0e-6


def test_geocentric_to_geodetic_horz_single():
    """Test conversion from geocentric to geodetic coordinates"""

    lat, lon, rad, az, el = \
        coords.geodetic_to_geocentric_horizontal(45.0, 8.0, 52.0, 63.0,
                                                 inverse=True)

    assert abs(lat - 45.192423215981954) < 1.0e-6
    assert abs(lon - 8.0) < 1.0e-6
    assert abs(rad - 6367.345908499981) < 1.0e-6
    assert abs(az - 52.29896101551479) < 1.0e-6
    assert abs(el - 63.118072033649916) < 1.0e-6


def test_geodetic_to_geocentric_horz_mult():
    """Test array conversion from geodetic to geocentric coordinates"""

    arr = np.ones(shape=(10,), dtype=float)
    lat, lon, rad, az, el = \
        coords.geodetic_to_geocentric_horizontal(45.0 * arr, 8.0 * arr,
                                                 52.0 * arr, 63.0 * arr)

    assert lat.shape == arr.shape
    assert lon.shape == arr.shape
    assert rad.shape == arr.shape
    assert az.shape == arr.shape
    assert el.shape == arr.shape
    assert abs(lat - 44.807576784018046).max() < 1.0e-6
    assert abs(lon - 8.0).max() < 1.0e-6
    assert abs(rad - 6367.489543863465).max() < 1.0e-6
    assert abs(az - 51.70376774257361).max() < 1.0e-6
    assert abs(el - 62.8811403841008).max() < 1.0e-6


def test_geocentric_to_geodetic_horz_mult():
    """Test array conversion from geocentric to geodetic coordinates"""

    arr = np.ones(shape=(10,), dtype=float)
    lat, lon, rad, az, el = \
        coords.geodetic_to_geocentric_horizontal(45.0 * arr, 8.0 * arr,
                                                 52.0 * arr, 63.0 * arr,
                                                 inverse=True)

    assert lat.shape == arr.shape
    assert lon.shape == arr.shape
    assert rad.shape == arr.shape
    assert az.shape == arr.shape
    assert el.shape == arr.shape
    assert abs(lat - 45.192423215981954).max() < 1.0e-6
    assert abs(lon - 8.0).max() < 1.0e-6
    assert abs(rad - 6367.345908499981).max() < 1.0e-6
    assert abs(az - 52.29896101551479).max() < 1.0e-6
    assert abs(el - 63.118072033649916).max() < 1.0e-6


def test_geodetic_to_geocentric_horizontal_inverse():
    """Tests the reversibility of geodetic to geocentric horiz conversions

    Note:  inverse of az and el angles currently non-functional"""

    lat1 = -17.5
    lon1 = 187.3
    az1 = 52.0
    el1 = 63.0
    lat2, lon2, rad_e, az2, el2 = \
        coords.geodetic_to_geocentric_horizontal(lat1, lon1, az1, el1,
                                                 inverse=False)
    lat3, lon3, rad_e, az3, el3 = \
        coords.geodetic_to_geocentric_horizontal(lat2, lon2, az2, el2,
                                                 inverse=True)

    assert abs(lon1 - lon3) < 1.0e-6
    assert abs(lat1 - lat3) < 1.0e-6
    assert abs(az1 - az3) < 1.0e-6
    assert abs(el1 - el3) < 1.0e-6


####################################
# Spherical / Cartesian conversions

def test_spherical_to_cartesian_single():
    """Test conversion from spherical to cartesian coordinates"""

    x, y, z = coords.spherical_to_cartesian(45.0, 30.0, 1.0)

    assert abs(x - y) < 1.0e-6
    assert abs(z - 0.5) < 1.0e-6


def test_cartesian_to_spherical_single():
    """Test conversion from cartesian to spherical coordinates"""

    x = 0.6123724356957946
    az, el, r = coords.spherical_to_cartesian(x, x, 0.5,
                                              inverse=True)

    assert abs(az - 45.0) < 1.0e-6
    assert abs(el - 30.0) < 1.0e-6
    assert abs(r - 1.0) < 1.0e-6


def test_spherical_to_cartesian_mult():
    """Test array conversion from spherical to cartesian coordinates"""

    arr = np.ones(shape=(10,), dtype=float)
    x, y, z = coords.spherical_to_cartesian(45.0 * arr, 30.0 * arr, arr)

    assert x.shape == arr.shape
    assert y.shape == arr.shape
    assert z.shape == arr.shape
    assert abs(x - y).max() < 1.0e-6
    assert abs(z - 0.5).max() < 1.0e-6


def test_cartesian_to_spherical_mult():
    """Test array conversion from cartesian to spherical coordinates"""

    arr = np.ones(shape=(10,), dtype=float)
    x = 0.6123724356957946
    az, el, r = coords.spherical_to_cartesian(x * arr, x * arr, 0.5 * arr,
                                              inverse=True)

    assert az.shape == arr.shape
    assert el.shape == arr.shape
    assert r.shape == arr.shape
    assert abs(az - 45.0).max() < 1.0e-6
    assert abs(el - 30.0).max() < 1.0e-6
    assert abs(r - 1.0).max() < 1.0e-6


def test_spherical_to_cartesian_inverse():
    """Tests the reversibility of spherical to cartesian conversions"""

    x1 = 3000.0
    y1 = 2000.0
    z1 = 2500.0
    az, el, r = coords.spherical_to_cartesian(x1, y1, z1,
                                              inverse=True)
    x2, y2, z2 = coords.spherical_to_cartesian(az, el, r,
                                               inverse=False)

    assert abs(x1 - x2) < 1.0e-6
    assert abs(y1 - y2) < 1.0e-6
    assert abs(z1 - z2) < 1.0e-6


########################################
# Global / Local Cartesian conversions

def test_global_to_local_cartesian_single():
    """Test conversion from global to local cartesian coordinates"""

    x, y, z = coords.global_to_local_cartesian(7000.0, 8000.0, 9000.0,
                                               37.5, 289.0, 6380.0)

    assert abs(x + 9223.175264852474) < 1.0e-6
    assert abs(y + 2239.835278362686) < 1.0e-6
    assert abs(z - 11323.126851088331) < 1.0e-6


def test_local_cartesian_to_global_single():
    """Test conversion from local cartesian to global coordinates"""

    x, y, z = coords.global_to_local_cartesian(7000.0, 8000.0, 9000.0,
                                               37.5, 289.0, 6380.0,
                                               inverse=True)

    assert abs(x + 5709.804676635975) < 1.0e-6
    assert abs(y + 4918.397556010223) < 1.0e-6
    assert abs(z - 15709.577500484005) < 1.0e-6


def test_global_to_local_cartesian_mult():
    """Test array conversion from global to local cartesian coordinates"""

    arr = np.ones(shape=(10,), dtype=float)
    x, y, z = coords.global_to_local_cartesian(7000.0 * arr, 8000.0 * arr,
                                               9000.0 * arr, 37.5 * arr,
                                               289.0 * arr, 6380.0 * arr)

    assert x.shape == arr.shape
    assert y.shape == arr.shape
    assert z.shape == arr.shape
    assert abs(x + 9223.175264852474).max() < 1.0e-6
    assert abs(y + 2239.835278362686).max() < 1.0e-6
    assert abs(z - 11323.126851088331).max() < 1.0e-6


def test_local_cartesian_to_global_mult():
    """Test array conversion from local cartesian to global coordinates"""

    arr = np.ones(shape=(10,), dtype=float)
    x, y, z = coords.global_to_local_cartesian(7000.0 * arr, 8000.0 * arr,
                                               9000.0 * arr, 37.5 * arr,
                                               289.0 * arr, 6380.0 * arr,
                                               inverse=True)

    assert x.shape == arr.shape
    assert y.shape == arr.shape
    assert z.shape == arr.shape
    assert abs(x + 5709.804676635975).max() < 1.0e-6
    assert abs(y + 4918.397556010223).max() < 1.0e-6
    assert abs(z - 15709.577500484005).max() < 1.0e-6


def test_global_to_local_cartesian_inverse():
    """Tests the reversibility of the global to loc cartesian transform"""

    x1 = 7000.0
    y1 = 8000.0
    z1 = 9500.0
    lat = 37.5
    lon = 289.0
    rad = 6380.0
    x2, y2, z2 = coords.global_to_local_cartesian(x1, y1, z1,
                                                  lat, lon, rad,
                                                  inverse=False)
    x3, y3, z3 = coords.global_to_local_cartesian(x2, y2, z2,
                                                  lat, lon, rad,
                                                  inverse=True)
    assert abs(x1 - x3) < 1.0e-6
    assert abs(y1 - y3) < 1.0e-6
    assert abs(z1 - z3) < 1.0e-6


########################################
# Local Horizontal / Global conversions

def test_local_horizontal_to_global_geo_geodetic():
    """Tests the conversion of the local horizontal to global geo"""

    az = 30.0
    el = 45.0
    dist = 1000.0
    lat0 = 45.0
    lon0 = 0.0
    alt0 = 400.0

    lat, lon, rad = \
        coords.local_horizontal_to_global_geo(az, el, dist,
                                              lat0, lon0, alt0)

    assert abs(lat - 50.419037572472625) < 1.0e-6
    assert abs(lon + 7.694008395350697) < 1.0e-6
    assert abs(rad - 7172.15486518744) < 1.0e-6


def test_local_horizontal_to_global_geo():
    """Tests the conversion of the local horizontal to global geo"""

    az = 30.0
    el = 45.0
    dist = 1000.0
    lat0 = 45.0
    lon0 = 0.0
    alt0 = 400.0

    lat, lon, rad = \
        coords.local_horizontal_to_global_geo(az, el, dist,
                                              lat0, lon0, alt0,
                                              geodetic=False)

    assert abs(lat - 50.414315865044202) < 1.0e-6
    assert abs(lon + 7.6855551809119502) < 1.0e-6
    assert abs(rad - 7185.6983665760772) < 1.0e-6
