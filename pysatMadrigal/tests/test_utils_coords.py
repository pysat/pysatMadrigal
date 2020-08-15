"""
tests the pysat coords area
"""
import numpy as np

import pytest

from pysatMadrigal.utils import coords


class TestGeodeticGeocentric():

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.val = {'lat': 45.0, 'lon': 8.0, 'az': 52.0, 'el': 63.0}

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val

    @pytest.mark.parametrize("kwargs,target",
                             [({}, [44.8075768, 8.0, 6367.48954386]),
                              ({'inverse': False},
                               [44.8075768, 8.0, 6367.48954386]),
                              ({'inverse': True},
                               [45.1924232, 8.0, 6367.3459085])])
    def test_geodetic_to_geocentric(self, kwargs, target):
        """Test conversion from geodetic to geocentric coordinates"""

        lat, lon, rad = coords.geodetic_to_geocentric(self.val['lat'],
                                                      lon_in=self.val['lon'],
                                                      **kwargs)

        assert np.all(abs(lat - target[0]) < 1.0e-6)
        assert np.all(abs(lon - target[1]) < 1.0e-6)
        assert np.all(abs(rad - target[2]) < 1.0e-6)
        if isinstance(lat, np.ndarray):
            assert lat.shape == self.val['lat'].shape
            assert lon.shape == self.val['lat'].shape
            assert rad.shape == self.val['lat'].shape

    def test_geodetic_to_geocentric_and_back(self):
        """Tests the reversibility of geodetic to geocentric conversions"""

        lat2, lon2, rad = coords.geodetic_to_geocentric(self.val['lat'],
                                                        lon_in=self.val['lon'],
                                                        inverse=False)
        lat3, lon3, rad = coords.geodetic_to_geocentric(lat2,
                                                        lon_in=lon2,
                                                        inverse=True)
        assert np.all(abs(self.val['lat'] - lat3) < 1.0e-6)
        assert np.all(abs(self.val['lon'] - lon3) < 1.0e-6)

    @pytest.mark.parametrize("kwargs,target",
                             [({}, [44.8075768, 8.0, 6367.48954386,
                                    51.7037677, 62.8811403]),
                              ({'inverse': False},
                               [44.8075768, 8.0, 6367.48954386,
                                51.7037677, 62.8811403]),
                              ({'inverse': True},
                               [45.1924232, 8.0, 6367.3459085,
                                52.2989610, 63.1180720])])
    def test_geodetic_to_geocentric_horizontal(self, kwargs, target):
        """Test conversion from geodetic to geocentric coordinates"""

        lat, lon, rad, az, el = \
            coords.geodetic_to_geocentric_horizontal(self.val['lat'],
                                                     self.val['lon'],
                                                     self.val['az'],
                                                     self.val['el'],
                                                     **kwargs)

        assert np.all(abs(lat - target[0]) < 1.0e-6)
        assert np.all(abs(lon - target[1]) < 1.0e-6)
        assert np.all(abs(rad - target[2]) < 1.0e-6)
        assert np.all(abs(az - target[3]) < 1.0e-6)
        assert np.all(abs(el - target[4]) < 1.0e-6)
        if isinstance(lat, np.ndarray):
            assert lat.shape == self.val['lat'].shape
            assert lon.shape == self.val['lat'].shape
            assert rad.shape == self.val['lat'].shape
            assert az.shape == self.val['lat'].shape
            assert el.shape == self.val['lat'].shape

    def test_geodetic_to_geocentric_horizontal_and_back(self):
        """Tests the reversibility of geodetic to geocentric horiz conversions

        Note:  inverse of az and el angles currently non-functional

        """

        lat2, lon2, rad_e, az2, el2 = \
            coords.geodetic_to_geocentric_horizontal(self.val['lat'],
                                                     self.val['lon'],
                                                     self.val['az'],
                                                     self.val['el'],
                                                     inverse=False)
        lat3, lon3, rad_e, az3, el3 = \
            coords.geodetic_to_geocentric_horizontal(lat2, lon2, az2, el2,
                                                     inverse=True)

        assert np.all(abs(self.val['lon'] - lon3) < 1.0e-6)
        assert np.all(abs(self.val['lat'] - lat3) < 1.0e-6)
        assert np.all(abs(self.val['az'] - az3) < 1.0e-6)
        assert np.all(abs(self.val['el'] - el3) < 1.0e-6)


class TestGeodeticGeocentricArray(TestGeodeticGeocentric):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'lat': 45.0 * arr,
                    'lon': 8.0 * arr,
                    'az': 52.0 * arr,
                    'el': 63.0 * arr}

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val


class TestSphereCartesian():

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.val = {'az': 45.0, 'el': 30.0, 'r': 1.0,
                    'x': 0.6123724356957946, 'z': 0.5}

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val

    @pytest.mark.parametrize("kwargs,input,target",
                             [({}, ['az', 'el', 'r'],
                               ['x', 'x', 'z']),
                              ({'inverse': False},  ['az', 'el', 'r'],
                               ['x', 'x', 'z']),
                              ({'inverse': True}, ['x', 'x', 'z'],
                               ['az', 'el', 'r'])])
    def test_spherical_to_cartesian(self, kwargs, input, target):
        """Test conversion from spherical to cartesian coordinates"""

        a, b, c = coords.spherical_to_cartesian(self.val[input[0]],
                                                self.val[input[1]],
                                                self.val[input[2]],
                                                **kwargs)

        assert np.all(abs(a - self.val[target[0]]) < 1.0e-6)
        assert np.all(abs(b - self.val[target[1]]) < 1.0e-6)
        assert np.all(abs(c - self.val[target[2]]) < 1.0e-6)
        if isinstance(self.val['az'], np.ndarray):
            assert a.shape == self.val['x'].shape
            assert b.shape == self.val['x'].shape
            assert c.shape == self.val['x'].shape

    def test_spherical_to_cartesian_and_back(self):
        """Tests the reversibility of spherical to cartesian conversions"""

        az, el, r = coords.spherical_to_cartesian(self.val['x'],
                                                  self.val['x'],
                                                  self.val['z'],
                                                  inverse=True)
        x2, y2, z2 = coords.spherical_to_cartesian(az, el, r,
                                                   inverse=False)

        assert np.all(abs(self.val['x'] - x2) < 1.0e-6)
        assert np.all(abs(self.val['x'] - y2) < 1.0e-6)
        assert np.all(abs(self.val['z'] - z2) < 1.0e-6)


class TestSphereCartesianArray(TestSphereCartesian):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'az': 45.0 * arr, 'el': 30.0 * arr, 'r': 1.0 * arr,
                    'x': 0.6123724356957946 * arr, 'z': 0.5 * arr}

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val


class TestGlobalLocal():

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.val = {'x': 7000.0, 'y': 8000.0, 'z': 9000.0,
                    'lat': 37.5, 'lon': 289.0, 'rad': 6380.0}

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val

    @pytest.mark.parametrize("kwargs,target",
                             [({},
                               [-9223.1752649, -2239.8352784, 11323.1268511]),
                              ({'inverse': False},
                               [-9223.1752649, -2239.8352784, 11323.1268511]),
                              ({'inverse': True},
                               [-5709.804677, -4918.397556, 15709.5775005])])
    def test_global_to_local_cartesian(self, kwargs, target):
        """Test conversion from global to local cartesian coordinates"""

        x, y, z = coords.global_to_local_cartesian(self.val['x'],
                                                   self.val['y'],
                                                   self.val['z'],
                                                   self.val['lat'],
                                                   self.val['lon'],
                                                   self.val['rad'],
                                                   **kwargs)

        assert np.all(abs(x - target[0]) < 1.0e-6)
        assert np.all(abs(y - target[1]) < 1.0e-6)
        assert np.all(abs(z - target[2]) < 1.0e-6)
        if isinstance(self.val['x'], np.ndarray):
            assert x.shape == self.val['x'].shape
            assert y.shape == self.val['x'].shape
            assert z.shape == self.val['x'].shape

    def test_global_to_local_cartesian_and_back(self):
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
        assert np.all(abs(self.val['x'] - x3) < 1.0e-6)
        assert np.all(abs(self.val['y'] - y3) < 1.0e-6)
        assert np.all(abs(self.val['z'] - z3) < 1.0e-6)


class TestGlobalLocalArray(TestGlobalLocal):

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'x': 7000.0 * arr, 'y': 8000.0 * arr, 'z': 9000.0 * arr,
                    'lat': 37.5 * arr, 'lon': 289.0 * arr, 'rad': 6380.0 * arr}

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val


class TestLocalHorizontalGlobal():
    """Tests for local horizontal to global geo and back """

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.val = {'az': 30.0, 'el': 45.0, 'dist': 1000.0,
                    'lat': 45.0, 'lon': 0.0, 'alt': 400.0}

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val

    @pytest.mark.parametrize("kwargs,target",
                             [({}, [50.4190376, -7.6940084, 7172.1548652]),
                              ({'geodetic': True},
                               [50.4190376, -7.6940084, 7172.1548652]),
                              ({'geodetic': False},
                               [50.4143159, -7.6855552, 7185.6983666])])
    def test_local_horizontal_to_global_geo(self, kwargs, target):
        """Tests the conversion of the local horizontal to global geo"""

        lat, lon, rad = \
            coords.local_horizontal_to_global_geo(self.val['az'],
                                                  self.val['el'],
                                                  self.val['dist'],
                                                  self.val['lat'],
                                                  self.val['lon'],
                                                  self.val['alt'],
                                                  **kwargs)

        assert np.all(abs(lat - target[0]) < 1.0e-6)
        assert np.all(abs(lon - target[1]) < 1.0e-6)
        assert np.all(abs(rad - target[2]) < 1.0e-6)
        if isinstance(self.val['lat'], np.ndarray):
            assert lat.shape == self.val['lat'].shape
            assert lon.shape == self.val['lat'].shape
            assert rad.shape == self.val['lat'].shape


class TestLocalHorizontalGlobalArray(TestLocalHorizontalGlobal):
    """Tests for local horizontal to global geo and back """

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'az': 30.0 * arr, 'el': 45.0 * arr, 'dist': 1000.0 * arr,
                    'lat': 45.0 * arr, 'lon': 0.0 * arr, 'alt': 400.0 * arr}

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        del self.val
