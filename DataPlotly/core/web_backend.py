"""Web Backend

Picks the Qt web module available at runtime: QtWebKit when present, QtWebEngine otherwise.
Selecting by QGIS version is not enough, because some QGIS 3 builds ship without QtWebKit
(e.g. Debian, built with WITH_QTWEBKIT=FALSE).
QtWebKit is tried first so QGIS 3 installs that already work keep the same rendering.

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

try:
    from qgis.PyQt import QtWebKitWidgets  # noqa: F401
except ImportError:
    USE_WEBENGINE = True
else:
    USE_WEBENGINE = False
