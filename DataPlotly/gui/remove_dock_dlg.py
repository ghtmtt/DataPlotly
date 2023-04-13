"""
Minimal dlg with combobox to remove DataPlotlyDialog
"""
from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import Qt

from DataPlotly.gui.gui_utils import GuiUtils


WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('remove_dock_dlg.ui'))


# pylint: disable=too-few-public-methods
class DataPlotlyRemoveDockDialog(QDialog, WIDGET):
    """Dialog to remove new dock"""
    def __init__(self, dock_widgets=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        dock_ids = [dock_id for dock_id in dock_widgets.keys() if dock_id != 'DataPlotly']
        self.DockIdsComboBox.addItems(dock_ids)
        for i, dock_id in enumerate(dock_ids):
            self.DockIdsComboBox.setItemData(i, dock_widgets[dock_id].title, Qt.ToolTipRole)

    def get_param(self):
        """Return the dock_id to delete"""
        return self.DockIdsComboBox.currentText()
