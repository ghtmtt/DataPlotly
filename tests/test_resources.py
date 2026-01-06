"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

__author__ = 'matteo.ghetta@gmail.com'
__date__ = '2017-03-05'
__copyright__ = 'Copyright 2017, matteo ghetta'
"""

from qgis.PyQt.QtGui import QIcon


def test_icon_png():
    """Test we can load resources."""
    path = ':/plugins/DataPlotly/icon.png'
    icon = QIcon(path)
    assert not icon.isNull()
