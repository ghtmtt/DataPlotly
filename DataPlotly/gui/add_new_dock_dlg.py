"""
Dialog to add new DataPlotlyDock with custom validator
"""
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QValidator
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

from DataPlotly.core.core_utils import uuid_suffix
from DataPlotly.gui.gui_utils import GuiUtils

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('add_dock_dlg.ui'))


class DataPlotlyNewDockDialog(QDialog, WIDGET):
    """Dialog to add new dock"""

    def __init__(self, dock_widgets=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.DockIdInformationLabel.hide()
        validator = DataPlotlyNewDockIdValidator(dock_widgets=dock_widgets)
        self.DockIdLineEdit.setValidator(validator)
        validator.validationChanged.connect(self.update_dlg)
        self.DockTitleLineEdit.valueChanged.connect(self.updateDockIdLineEdit)
        self.mCustomizeGroupBox.clicked.connect(self.updateDockIdLineEdit)

    def update_dlg(self, state, msg):
        """validator slot"""
        is_valid = state != QValidator.State.Intermediate
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(is_valid)
        label = self.DockIdInformationLabel
        lineEdit = self.DockIdLineEdit
        style_border = ""
        if not is_valid:
            style_border = "border: 3px solid red"
            label.show()
        else:
            label.hide()
        label.setText(msg)
        lineEdit.setStyleSheet(style_border)

    def updateDockIdLineEdit(self):
        """update the dockid with uuid suffix when
        <Customize dockid> checkbox is unchecked
        """
        if not self.mCustomizeGroupBox.isChecked():
            title = self.DockTitleLineEdit.value()
            self.DockIdLineEdit.setValue(uuid_suffix(title))

    def get_params(self):
        """greturn dock_title and dock_id"""
        dock_title = self.DockTitleLineEdit.value()
        dock_id = self.DockIdLineEdit.value()
        return dock_title, dock_id


# pylint: disable=too-few-public-methods
class DataPlotlyNewDockIdValidator(QValidator):
    """Custom validator to prevent some users action"""
    validationChanged = pyqtSignal(QValidator.State, str)

    def __init__(self, parent=None, dock_widgets=None):
        """Constructor."""
        super().__init__(parent)
        self.dock_widgets = dock_widgets

    def validate(self, dock_id, pos):
        """Checks if dock_id is not empty and not is already present"""
        state = QValidator.State.Acceptable
        msg = None

        if dock_id == "":
            state = QValidator.State.Intermediate
            msg = self.tr('DockId can not be empty')

        if dock_id in self.dock_widgets:
            state = QValidator.State.Intermediate
            msg = self.tr(f'DockId {dock_id} is already taken')

        if '_' in dock_id:
            state = QValidator.State.Intermediate
            msg = self.tr('The underscore _ is not allowed')

        self.validationChanged.emit(state, msg)

        return state, dock_id, pos
