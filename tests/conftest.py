import logging
import os
import sys

from pathlib import Path

import pytest

from qgis.core import Qgis, QgsApplication
from qgis.PyQt import Qt
from qgis.testing import start_app

# with warnings.catch_warnings():
#    warnings.filterwarnings("ignore", category=DeprecationWarning)
#    from osgeo import gdal


def pytest_report_header(config):
    from osgeo import gdal

    message = (
        f"QGIS : {Qgis.QGIS_VERSION_INT}\n"
        f"Python GDAL : {gdal.VersionInfo('VERSION_NUM')}\n"
        f"Python : {sys.version}\n"
        f"QT : {Qt.QT_VERSION_STR}"
    )
    return message


#
# Fixtures
#


@pytest.fixture(scope="session")
def rootdir(request: pytest.FixtureRequest) -> Path:
    return Path(request.config.rootdir.strpath)


@pytest.fixture(scope="session")
def data(rootdir: Path) -> Path:
    return rootdir.joinpath("data")


#
# Session
#


# Path the 'qgis.utils.iface' property
# Which is not initialized when QGIS app
# is initialized from testing module
def _patch_iface():
    import qgis.utils

    from qgis.testing.mocked import get_iface

    qgis.utils.iface = get_iface()


def pytest_sessionstart(session):
    """Start qgis application"""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    sys.path.append("/usr/share/qgis/python")

    # NOTE: we need to prevent cleanup in this case
    # because failing tests leads to a segfault.
    start_app(cleanup=False)
    install_logger_hook(verbose=True)
    
    # XXX The mock does not work here

    # Patch 'iface' in qgis.utils
    #_patch_iface()


#
# Logger hook
#


def install_logger_hook(verbose: bool = False) -> None:
    """Install message log hook"""
    from qgis.core import Qgis

    # Add a hook to qgis  message log
    def writelogmessage(message, tag, level):
        arg = f"{tag}: {message}"
        if level == Qgis.MessageLevel.Warning:
            logging.warning(arg)
        elif level == Qgis.MessageLevel.Critical:
            logging.error(arg)
        elif verbose:
            # Qgis is somehow very noisy
            # log only if verbose is set
            logging.info(arg)

    messageLog = QgsApplication.messageLog()
    messageLog.messageReceived.connect(writelogmessage)
