import configparser
import importlib
import logging
import sys

from pathlib import Path
from typing import (
    Any,
    Optional,
)

import pytest
import semver

from qgis.core import Qgis, QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt import Qt


def pytest_report_header(config):
    from osgeo import gdal

    return (
        f"QGIS : {Qgis.QGIS_VERSION_INT}\n"
        f"Python GDAL : {gdal.VersionInfo('VERSION_NUM')}\n"
        f"Python : {sys.version}\n"
        f"QT : {Qt.QT_VERSION_STR}"
    )


@pytest.fixture(scope="session")
def rootdir(request: pytest.FixtureRequest) -> Path:
    return request.config.rootpath


@pytest.fixture(scope="session")
def data(rootdir: Path) -> Path:
    return rootdir.joinpath("data")


@pytest.fixture(scope="session")
def output_dir(rootdir: Path) -> Path:
    outdir = rootdir.joinpath("__output__")
    outdir.mkdir(exist_ok=True)
    return outdir


@pytest.fixture(autouse=True, scope="session")
def plugin(
    rootdir: Path,
    qgis_processing: None,
    qgis_iface: QgisInterface,
) -> Any:
    # Load plugin
    plugin_path = rootdir.parent.joinpath("DataPlotly")
    plugin = _load_plugin(plugin_path, qgis_iface)

    yield plugin


def pytest_sessionstart(session: pytest.Session):
    _install_logger_hook()


def _install_logger_hook():
    """Install message log hook"""
    logging.debug("Installing logger hook")
    from qgis.core import Qgis

    # Add a hook to qgis  message log
    def writelogmessage(message, tag, level):
        arg = "{}: {}".format(tag, message)
        if level == Qgis.Warning:
            logging.warning(arg)
        elif level == Qgis.Critical:
            logging.error(arg)
        else:
            # Qgis is somehow very noisy
            logging.debug(arg)

    messageLog = QgsApplication.messageLog()
    messageLog.messageReceived.connect(writelogmessage)


def _load_plugin(plugin_path: Path, iface: QgisInterface) -> Any:
    logging.info("Loading plugin: %s", plugin_path)

    cp = configparser.ConfigParser()
    with plugin_path.joinpath("metadata.txt").open() as f:
        cp.read_file(f)
        assert _check_qgis_version(
            cp["general"].get("qgisMinimumVersion"),
            cp["general"].get("qgisMaximumVersion"),
        )

    sys.path.append(str(plugin_path.parent))

    plugin = plugin_path.name

    package = importlib.import_module(plugin)
    assert plugin in sys.modules

    init = package.classFactory(iface)
    init.initProcessing()

    return init


def _check_qgis_version(minver: Optional[str], maxver: Optional[str]) -> bool:
    version = semver.Version.parse(Qgis.QGIS_VERSION.split("-", maxsplit=1)[0])

    def _version(ver: Optional[str]) -> semver.Version:
        if not ver:
            return version

        # Normalize version
        parts = ver.split(".")
        match len(parts):
            case 1:
                parts.extend(("0", "0"))
            case 2:
                parts.append("0")
        return semver.Version.parse(".".join(parts))

    return _version(minver) <= version <= _version(maxver)
