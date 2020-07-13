"""
tests the pysat coords area
"""
import numpy as np

import pytest

from pysatMadrigal.utils import coords


@pytest.mark.parametrize("Nvals", [1, 10])
@pytest.mark.parametrize("inverse,input,target",
                         [(False, [45.0, 8.0],
                          [44.8075768, 8.0, 6367.48954386]),
                          (True, [45.0, 8.0],
                           [45.1924232, 8.0, 6367.3459085])])
def test_geodetic_to_geocentric_multi(Nvals, input, inverse, target):
    """Test array conversion from geodetic to geocentric coordinates"""

    lat_in = input[0] * np.ones(shape=(Nvals,), dtype=float)
    lon_in = input[1] * np.ones(shape=(Nvals,), dtype=float)

    output = coords.geodetic_to_geocentric(lat_in, lon_in=lon_in,
                                           inverse=inverse)

    for i in range(3):
        assert output[i].shape == lat_in.shape
        assert abs(output[i] - target[i]).max() < 1.0e-6


def test_geodetic_to_geocentric_and_back():
    """Tests the reversibility of geodetic to geocentric conversions"""

    input = [35.0, 17.0]
    temp_vals = coords.geodetic_to_geocentric(input[0], lon_in=input[1],
                                              inverse=False)
    output = coords.geodetic_to_geocentric(temp_vals[0],
                                           lon_in=temp_vals[1],
                                           inverse=True)
    for i in range(2):
        assert abs(input[i] - output[i]) < 1.0e-6


class TestGeodeticGeocentric():

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'lat': 45.0, 'lon': 8.0, 'az': 52.0, 'el': 63.0}
        self.arr = {}
        for key in self.val.keys():
            self.arr[key] = self.val[key] * arr

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val, self.arr,

    ###############################################
    # Geodetic / Geocentric Horizontal conversions

    def test_geodetic_to_geocentric_horz_single(self):
        """Test conversion from geodetic to geocentric coordinates"""

        lat, lon, rad, az, el = \
            coords.geodetic_to_geocentric_horizontal(self.val['lat'],
                                                     self.val['lon'],
                                                     self.val['az'],
                                                     self.val['el'])

        assert abs(lat - 44.807576784018046) < 1.0e-6
        assert abs(lon - 8.0) < 1.0e-6
        assert abs(rad - 6367.489543863465) < 1.0e-6
        assert abs(az - 51.70376774257361) < 1.0e-6
        assert abs(el - 62.8811403841008) < 1.0e-6

    def test_geocentric_to_geodetic_horz_single(self):
        """Test conversion from geocentric to geodetic coordinates"""

        lat, lon, rad, az, el = \
            coords.geodetic_to_geocentric_horizontal(self.val['lat'],
                                                     self.val['lon'],
                                                     self.val['az'],
                                                     self.val['el'],
                                                     inverse=True)

        assert abs(lat - 45.192423215981954) < 1.0e-6
        assert abs(lon - 8.0) < 1.0e-6
        assert abs(rad - 6367.345908499981) < 1.0e-6
        assert abs(az - 52.29896101551479) < 1.0e-6
        assert abs(el - 63.118072033649916) < 1.0e-6

    def test_geodetic_to_geocentric_horz_mult(self):
        """Test array conversion from geodetic to geocentric coordinates"""

        lat, lon, rad, az, el = \
            coords.geodetic_to_geocentric_horizontal(self.arr['lat'],
                                                     self.arr['lon'],
                                                     self.arr['az'],
                                                     self.arr['el'])

        assert lat.shape == self.arr['lat'].shape
        assert lon.shape == self.arr['lat'].shape
        assert rad.shape == self.arr['lat'].shape
        assert az.shape == self.arr['lat'].shape
        assert el.shape == self.arr['lat'].shape
        assert abs(lat - 44.807576784018046).max() < 1.0e-6
        assert abs(lon - 8.0).max() < 1.0e-6
        assert abs(rad - 6367.489543863465).max() < 1.0e-6
        assert abs(az - 51.70376774257361).max() < 1.0e-6
        assert abs(el - 62.8811403841008).max() < 1.0e-6

    def test_geocentric_to_geodetic_horz_mult(self):
        """Test array conversion from geocentric to geodetic coordinates"""

        lat, lon, rad, az, el = \
            coords.geodetic_to_geocentric_horizontal(self.arr['lat'],
                                                     self.arr['lon'],
                                                     self.arr['az'],
                                                     self.arr['el'],
                                                     inverse=True)

        assert lat.shape == self.arr['lat'].shape
        assert lon.shape == self.arr['lat'].shape
        assert rad.shape == self.arr['lat'].shape
        assert az.shape == self.arr['lat'].shape
        assert el.shape == self.arr['lat'].shape
        assert abs(lat - 45.192423215981954).max() < 1.0e-6
        assert abs(lon - 8.0).max() < 1.0e-6
        assert abs(rad - 6367.345908499981).max() < 1.0e-6
        assert abs(az - 52.29896101551479).max() < 1.0e-6
        assert abs(el - 63.118072033649916).max() < 1.0e-6

    def test_geodetic_to_geocentric_horizontal_inverse(self):
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


class TestSphereCart():

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'az': 45.0, 'el': 30.0, 'r': 1.0,
                    'x': 0.6123724356957946, 'z': 0.5}
        self.arr = {}
        for key in self.val.keys():
            self.arr[key] = self.val[key] * arr

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val, self.arr,

    def test_spherical_to_cartesian_single(self):
        """Test conversion from spherical to cartesian coordinates"""

        x, y, z = coords.spherical_to_cartesian(self.val['az'],
                                                self.val['el'],
                                                self.val['r'])

        assert abs(x - y) < 1.0e-6
        assert abs(z - 0.5) < 1.0e-6

    def test_cartesian_to_spherical_single(self):
        """Test conversion from cartesian to spherical coordinates"""

        az, el, r = coords.spherical_to_cartesian(self.val['x'], self.val['x'],
                                                  self.val['z'], inverse=True)

        assert abs(az - 45.0) < 1.0e-6
        assert abs(el - 30.0) < 1.0e-6
        assert abs(r - 1.0) < 1.0e-6

    def test_spherical_to_cartesian_mult(self):
        """Test array conversion from spherical to cartesian coordinates"""

        x, y, z = coords.spherical_to_cartesian(self.arr['az'],
                                                self.arr['el'],
                                                self.arr['r'])

        assert x.shape == self.arr['x'].shape
        assert y.shape == self.arr['x'].shape
        assert z.shape == self.arr['x'].shape
        assert abs(x - y).max() < 1.0e-6
        assert abs(z - 0.5).max() < 1.0e-6

    def test_cartesian_to_spherical_mult(self):
        """Test array conversion from cartesian to spherical coordinates"""

        az, el, r = coords.spherical_to_cartesian(self.arr['x'],
                                                  self.arr['x'],
                                                  self.arr['z'],
                                                  inverse=True)

        assert az.shape == self.arr['x'].shape
        assert el.shape == self.arr['x'].shape
        assert r.shape == self.arr['x'].shape
        assert abs(az - 45.0).max() < 1.0e-6
        assert abs(el - 30.0).max() < 1.0e-6
        assert abs(r - 1.0).max() < 1.0e-6

    def test_spherical_to_cartesian_inverse(self):
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

class TestGlobalLocal():

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'x': 7000.0, 'y': 8000.0, 'z': 9000.0,
                    'lat': 37.5, 'lon': 289.0, 'rad': 6380.0}
        self.arr = {}
        for key in self.val.keys():
            self.arr[key] = self.val[key] * arr

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val, self.arr,

    def test_global_to_local_cartesian_single(self):
        """Test conversion from global to local cartesian coordinates"""

        x, y, z = coords.global_to_local_cartesian(self.val['x'],
                                                   self.val['y'],
                                                   self.val['z'],
                                                   self.val['lat'],
                                                   self.val['lon'],
                                                   self.val['rad'])

        assert abs(x + 9223.175264852474) < 1.0e-6
        assert abs(y + 2239.835278362686) < 1.0e-6
        assert abs(z - 11323.126851088331) < 1.0e-6

    def test_local_cartesian_to_global_single(self):
        """Test conversion from local cartesian to global coordinates"""

        x, y, z = coords.global_to_local_cartesian(self.val['x'],
                                                   self.val['y'],
                                                   self.val['z'],
                                                   self.val['lat'],
                                                   self.val['lon'],
                                                   self.val['rad'],
                                                   inverse=True)

        assert abs(x + 5709.804676635975) < 1.0e-6
        assert abs(y + 4918.397556010223) < 1.0e-6
        assert abs(z - 15709.577500484005) < 1.0e-6

    def test_global_to_local_cartesian_mult(self):
        """Test array conversion from global to local cartesian coordinates"""

        x, y, z = coords.global_to_local_cartesian(self.arr['x'],
                                                   self.arr['y'],
                                                   self.arr['z'],
                                                   self.arr['lat'],
                                                   self.arr['lon'],
                                                   self.arr['rad'])

        assert x.shape == self.arr['x'].shape
        assert y.shape == self.arr['x'].shape
        assert z.shape == self.arr['x'].shape
        assert abs(x + 9223.175264852474).max() < 1.0e-6
        assert abs(y + 2239.835278362686).max() < 1.0e-6
        assert abs(z - 11323.126851088331).max() < 1.0e-6

    def test_local_cartesian_to_global_mult(self):
        """Test array conversion from local cartesian to global coordinates"""

        x, y, z = coords.global_to_local_cartesian(self.arr['x'],
                                                   self.arr['y'],
                                                   self.arr['z'],
                                                   self.arr['lat'],
                                                   self.arr['lon'],
                                                   self.arr['rad'],
                                                   inverse=True)

        assert x.shape == self.arr['x'].shape
        assert y.shape == self.arr['x'].shape
        assert z.shape == self.arr['x'].shape
        assert abs(x + 5709.804676635975).max() < 1.0e-6
        assert abs(y + 4918.397556010223).max() < 1.0e-6
        assert abs(z - 15709.577500484005).max() < 1.0e-6

    def test_global_to_local_cartesian_inverse(self):
        """Tests the reversibility of the global to loc cartesian transform"""

        x2, y2, z2 = coords.global_to_local_cartesian(self.val['x'],
                                                      self.val['y'],
                                                      self.val['z'],
                                                      self.val['lat'],
                                                      self.val['lon'],
                                                      self.val['rad'],
                                                      inverse=False)
        x3, y3, z3 = coords.global_to_local_cartesian(x2, y2, z2,
                                                      self.val['lat'],
                                                      self.val['lon'],
                                                      self.val['rad'],
                                                      inverse=True)
        assert abs(self.val['x'] - x3) < 1.0e-6
        assert abs(self.val['y'] - y3) < 1.0e-6
        assert abs(self.val['z'] - z3) < 1.0e-6


class TestLocalHorzGlobal():
    """Tests for local horizontal to global geo and back """

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'az': 30.0, 'el': 45.0, 'dist': 1000.0,
                    'lat': 45.0, 'lon': 0.0, 'alt': 400.0}
        self.arr = {}
        for key in self.val.keys():
            self.arr[key] = self.val[key] * arr

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val, self.arr,

    def test_local_horizontal_to_global_geo_geodetic(self):
        """Tests the conversion of the local horizontal to global geo"""

        lat, lon, rad = \
            coords.local_horizontal_to_global_geo(self.val['az'],
                                                  self.val['el'],
                                                  self.val['dist'],
                                                  self.val['lat'],
                                                  self.val['lon'],
                                                  self.val['alt'])

        assert abs(lat - 50.419037572472625) < 1.0e-6
        assert abs(lon + 7.694008395350697) < 1.0e-6
        assert abs(rad - 7172.15486518744) < 1.0e-6

    def test_local_horizontal_to_global_geo(self):
        """Tests the conversion of the local horizontal to global geo"""

        lat, lon, rad = \
            coords.local_horizontal_to_global_geo(self.val['az'],
                                                  self.val['el'],
                                                  self.val['dist'],
                                                  self.val['lat'],
                                                  self.val['lon'],
                                                  self.val['alt'],
                                                  geodetic=False)

        assert abs(lat - 50.414315865044202) < 1.0e-6
        assert abs(lon + 7.6855551809119502) < 1.0e-6
        assert abs(rad - 7185.6983665760772) < 1.0e-6

    def test_local_horizontal_to_global_geo_geodetic_mult(self):
        """Tests the conversion of the local horizontal to global geo"""

        lat, lon, rad = \
            coords.local_horizontal_to_global_geo(self.arr['az'],
                                                  self.arr['el'],
                                                  self.arr['dist'],
                                                  self.arr['lat'],
                                                  self.arr['lon'],
                                                  self.arr['alt'])

        assert lat.shape == self.arr['lat'].shape
        assert lon.shape == self.arr['lat'].shape
        assert rad.shape == self.arr['lat'].shape
        assert abs(lat - 50.419037572472625).max() < 1.0e-6
        assert abs(lon + 7.694008395350697).max() < 1.0e-6
        assert abs(rad - 7172.15486518744).max() < 1.0e-6

    def test_local_horizontal_to_global_geo_mult(self):
        """Tests the conversion of the local horizontal to global geo"""

        lat, lon, rad = \
            coords.local_horizontal_to_global_geo(self.arr['az'],
                                                  self.arr['el'],
                                                  self.arr['dist'],
                                                  self.arr['lat'],
                                                  self.arr['lon'],
                                                  self.arr['alt'],
                                                  geodetic=False)

        assert lat.shape == self.arr['lat'].shape
        assert lon.shape == self.arr['lat'].shape
        assert rad.shape == self.arr['lat'].shape
        assert abs(lat - 50.414315865044202).max() < 1.0e-6
        assert abs(lon + 7.6855551809119502).max() < 1.0e-6
        assert abs(rad - 7185.6983665760772).max() < 1.0e-6
