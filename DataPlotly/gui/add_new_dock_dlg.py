import uuid

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QValidator
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

from DataPlotly.gui.gui_utils import GuiUtils


WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('add_dock_dlg.ui'))

def uuid_suffix(string: str) -> str:
    return f"{string}{uuid.uuid4()}"


class DataPlotlyNewDockDialog(QDialog, WIDGET):
    def __init__(self, dock_widgets = None, parent = None):
        """Dialog to add new dock"""
        super().__init__(parent)
        self.setupUi(self)
        
        self.DockIdInformationLabel.hide()
        validator = DataPlotlyNewDockIdValidator(dock_widgets=dock_widgets)
        self.DockIdLineEdit.setValidator(validator)
        validator.validationChanged.connect(self.update_dlg)
        self.DockTitleLineEdit.valueChanged.connect(self.updateDockIdLineEdit)
        self.mCustomizeGroupBox.clicked.connect(self.updateDockIdLineEdit)

    def update_dlg(self, state, msg):
        is_valid = state != QValidator.Intermediate
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(is_valid)
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

    def updateDockIdLineEdit(self, signal):
        if not self.mCustomizeGroupBox.isChecked():
            title = self.DockTitleLineEdit.value()
            self.DockIdLineEdit.setValue(uuid_suffix(title))
    
    def get_params(self):
        dock_title = self.DockTitleLineEdit.value()
        dock_id = self.DockIdLineEdit.value()
        return dock_title, dock_id


class DataPlotlyNewDockIdValidator(QValidator):

    validationChanged = pyqtSignal(QValidator.State, str)
    
    def __init__(self, parent = None, dock_widgets = None):
        """Constructor."""
        super().__init__(parent)
        self.dock_widgets = dock_widgets

    def validate(self, dock_id, pos):
        """Checks if dock_id is not empty and not is already present"""
        state = QValidator.Acceptable
        msg = None

        if dock_id == "":
            state = QValidator.Intermediate
            msg = self.tr(f'DockId can not be empty')

        if dock_id in self.dock_widgets:
            state = QValidator.Intermediate
            msg = self.tr(f'DockId {dock_id} is already taken')
        
        if '_' in dock_id:
            state = QValidator.Intermediate
            msg = self.tr('The underscore _ is not allowed')

        self.validationChanged.emit(state, msg)

        return state, dock_id, pos
