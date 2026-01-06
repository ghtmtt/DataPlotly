"""Tests for QGIS functionality.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

__author__ = 'tim@linfiniti.com'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

"""
from qgis.core import (
    QgsProviderRegistry,
    QgsCoordinateReferenceSystem,
)


def test_qgis_environment():
    """QGIS environment has the expected providers"""

    r = QgsProviderRegistry.instance()
    providers = r.providerList()
    assert 'gdal' in providers
    assert 'ogr' in providers
    assert 'postgres' in providers


def test_projection():
    """Test that QGIS properly parses a wkt string.
    """
    crs = QgsCoordinateReferenceSystem()
    wkt = (
        'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
        'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
        'PRIMEM["Greenwich",0.0],UNIT["Degree",'
        '0.0174532925199433]]')
    crs.createFromWkt(wkt)
    auth_id = crs.authid()
    expected_auth_id = 'EPSG:4326'
    assert auth_id == expected_auth_id
