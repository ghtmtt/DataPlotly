"""
Test Suite.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import sys
import os
import unittest
import tempfile
from osgeo import gdal
import qgis  # pylint: disable=unused-import

try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

try:
    import coverage
except ImportError:
    pipmain(['install', 'coverage'])
    import coverage

__author__ = 'Alessandro Pasotti'
__revision__ = '$Format:%H$'
__date__ = '30/04/2018'
__copyright__ = (
    'Copyright 2018, North Road')


def _run_tests(test_suite, package_name, with_coverage=False):
    """Core function to test a test suite."""
    count = test_suite.countTestCases()
    print('########')
    print('{} tests has been discovered in {}'.format(count, package_name))
    print('Python GDAL : %s' % gdal.VersionInfo('VERSION_NUM'))
    print('########')
    if with_coverage:
        cov = coverage.Coverage(
            source=['/DataPlotly'],
            omit=['*/test/*'],
        )
        cov.start()

    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(test_suite)

    if with_coverage:
        cov.stop()
        cov.save()
        with tempfile.NamedTemporaryFile(delete=False) as report:
            cov.report(file=report)
        # Produce HTML reports in the `htmlcov` folder and open index.html
        # cov.html_report()
        with open(report.name, encoding='utf8') as fin:
            print(fin.read())


def test_package(package='DataPlotly'):
    """Test package.
    This function is called by travis without arguments.

    :param package: The package to test.
    :type package: str
    """
    test_loader = unittest.defaultTestLoader
    try:
        test_suite = test_loader.discover(package)
    except ImportError:
        test_suite = unittest.TestSuite()
    _run_tests(test_suite, package)


def test_environment():
    """Test package with an environment variable."""
    package = os.environ.get('TESTING_PACKAGE', 'DataPlotly')
    test_loader = unittest.defaultTestLoader
    test_suite = test_loader.discover(package)
    _run_tests(test_suite, package)


if __name__ == '__main__':
    test_package()
