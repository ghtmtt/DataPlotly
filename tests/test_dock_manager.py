"""Plot factory test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from pathlib import Path

import pytest

from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QByteArray, QFile, QIODevice
from qgis.PyQt.QtGui import QValidator
from qgis.PyQt.QtXml import QDomDocument

from DataPlotly.core.core_utils import restore, restore_safe_str_xml, safe_str_xml
from DataPlotly.gui.add_new_dock_dlg import DataPlotlyNewDockIdValidator
from DataPlotly.gui.dock import DataPlotlyDock, DataPlotlyDockManager


def read_project(project_path: Path) -> QDomDocument:
    """Return a document from qgs file

    Args:
        project_path (str): path to qgs file

    Returns:
        QDocument: document
    """
    xml_file = QFile(project_path)
    if xml_file.open(QIODevice.ReadOnly):
        xml_doc = QDomDocument()
        xml_doc.setContent(xml_file)
        xml_file.close()
        return xml_doc
    return None


@pytest.fixture(scope="module")
def dock_manager(qgis_iface: QgisInterface) -> DataPlotlyDockManager:
    dock_widgets = {}
    return DataPlotlyDockManager(
        iface=qgis_iface,
        dock_widgets=dock_widgets,
    )


def test_002_add_new_dock(dock_manager: DataPlotlyDockManager):
    """
    Test addNewDock of DataPlotlyDockManager
    """

    dock_widgets = dock_manager.dock_widgets

    # checks DataPlotly main dock
    assert "DataPlotly" not in dock_widgets
    dock_widget = dock_manager.addNewDock()
    assert isinstance(dock_widget, DataPlotlyDock)
    assert "DataPlotly" in dock_widgets
    assert dock_widget is dock_widgets["DataPlotly"]

    # checks it's not possible to add a new dock with DataPlotly as dock_id
    dock_widget2 = dock_manager.addNewDock(
        dock_title="NewDataPlotly",
        dock_id="DataPlotly",
    )

    assert dock_widget2 is dock_widget

    # checks we can not add new dock with same dock_id
    dock_params = {"dock_title": "DataPlotly2", "dock_id": "DataPlotly2"}
    dock_manager.addNewDock(**dock_params)
    assert "DataPlotly2" in dock_widgets
    new_dock_widget = dock_manager.addNewDock(
        dock_title="DataPlotly2b",
        dock_id="DataPlotly2",
    )
    assert not new_dock_widget


def test_003_remove_dock(dock_manager: DataPlotlyDockManager):
    """
    Test removeDock
    """
    dock_widgets = dock_manager.dock_widgets

    dock_id = "dock_to_remove"
    dock_manager.addNewDock(dock_id=dock_id)
    assert dock_id in dock_widgets
    dock_manager.removeDock(dock_id)
    assert dock_id not in dock_widgets


def test_004_remove_docks(dock_manager: DataPlotlyDockManager):
    """
    Test removeDocks
    """
    dock_widgets = dock_manager.dock_widgets

    docks = ["DataPlotly", "DataPlotly2", "DataPlotly3"]
    for dock in docks:
        dock_manager.addNewDock(dock_id=dock)
    dock_manager.removeDocks()
    # do not remove DataPlotly main dock
    assert "DataPlotly" in dock_widgets
    assert len(dock_widgets) == 1


def test_005_get_dock(dock_manager: DataPlotlyDockManager):
    """
    Test getDock
    """
    dock_widgets = dock_manager.dock_widgets

    docks = ["DataPlotly", "DataPlotly2", "DataPlotly3"]
    for dock in docks:
        dock_manager.addNewDock(dock_id=dock)

    dock = dock_manager.getDock("DataPloty4_wrong_id")
    assert dock is None
    dock = dock_manager.getDock("DataPlotly3")
    assert isinstance(dock, DataPlotlyDock)
    assert dock is dock_widgets["DataPlotly3"]


def test_006_read_project(data: Path, dock_manager: DataPlotlyDockManager):
    """
    Test read_project with or without StateDataPlotly
    """
    # project with StateDataPlotly dom
    project_path = str(data.joinpath("test_project_with_state.qgs"))
    document = read_project(project_path)
    assert dock_manager.read_from_project(document)

    # project without StateDataPlotly dom
    project_path = str(data.joinpath("test_project_without_state.qgs"))
    document = read_project(project_path)
    assert not dock_manager.read_from_project(document)


def test_007_utils_xml_function():
    """
    Test restore, restore_safe_str_xml, safe_str_xml
    """
    test_string = "My test"
    assert test_string == restore_safe_str_xml(safe_str_xml(test_string))

    test_string = b"test"
    str_b64 = str(QByteArray(test_string).toBase64(), "utf-8")
    assert test_string == restore(str_b64)


def test_008_add_docks_from_project(data: Path, dock_manager: DataPlotlyDockManager):
    """
    Test docks are added, custom project without StateDataPlotly node
    """
    dock_widgets = dock_manager.dock_widgets

    project_path = str(data.joinpath("test_project_without_state.qgs"))
    document = read_project(project_path)
    dock_manager.addDocksFromProject(document)
    # all docks except main DataPlotlyDock are created
    dock_id = "my-test"
    dock_title = "My Test"
    assert dock_id in dock_widgets
    # . is replace by space My.Test -> My Test
    assert dock_widgets[dock_id].title == dock_title


def test_009_add_new_dock_validator(dock_manager: DataPlotlyDockManager):
    """
    Test DockIdValidator
    """
    dock_widgets = dock_manager.dock_widgets

    validator = DataPlotlyNewDockIdValidator(dock_widgets=dock_widgets)
    docks = ["DataPlotly", "DataPlotly2", "DataPlotly3"]
    for dock in docks:
        dock_manager.addNewDock(dock_id=dock)

    # Dockid is valid
    state, _, _ = validator.validate("NewDockId", None)
    assert state == QValidator.Acceptable

    # Dockid can not be empty / No underscore / Not already taken
    for bad_dock_id in ["", "with_underscore", "DataPlotly2"]:
        state, _, _ = validator.validate(bad_dock_id, None)
        assert state == QValidator.Intermediate
