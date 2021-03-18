# -*- coding: utf-8 -*-
"""Plot Layout Gui Handling

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import (
    QCoreApplication,
    QItemSelectionModel
)
from qgis.PyQt.QtWidgets import (
    QListWidget,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout
)
from qgis.gui import (
    QgsLayoutItemAbstractGuiMetadata,
    QgsLayoutItemBaseWidget,
    QgsLayoutItemPropertiesWidget
)

from DataPlotly.layouts.plot_layout_item import ITEM_TYPE
from DataPlotly.gui.gui_utils import GuiUtils
from DataPlotly.gui.plot_settings_widget import DataPlotlyPanelWidget


class PlotLayoutItemWidget(QgsLayoutItemBaseWidget):
    """
    Configuration widget for layout plot items
    """

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        self.plot_item = layout_object
        self.message_bar = None

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)

        plot_tools_layout = QHBoxLayout()

        plot_add_button = QPushButton()
        plot_add_button.setIcon(GuiUtils.get_icon('symbologyAdd.svg'))
        plot_add_button.setToolTip('Add a new plot')
        plot_tools_layout.addWidget(plot_add_button)
        plot_add_button.clicked.connect(self.add_plot)

        plot_remove_button = QPushButton()
        plot_remove_button.setIcon(GuiUtils.get_icon('symbologyRemove.svg'))
        plot_remove_button.setToolTip('Remove selected plot')
        plot_tools_layout.addWidget(plot_remove_button)
        plot_remove_button.clicked.connect(self.remove_plot)

        plot_duplicate_button = QPushButton()
        plot_duplicate_button.setIcon(GuiUtils.get_icon('mActionDuplicateLayer.svg'))
        plot_duplicate_button.setToolTip('Duplicates the selected plot')
        plot_tools_layout.addWidget(plot_duplicate_button)
        plot_duplicate_button.clicked.connect(self.duplicate_plot)

        plot_move_up_button = QPushButton()
        plot_move_up_button.setIcon(GuiUtils.get_icon('mActionArrowUp.svg'))
        plot_move_up_button.setToolTip('Move selected plot up')
        plot_tools_layout.addWidget(plot_move_up_button)
        plot_move_up_button.clicked.connect(self.move_up_plot)

        plot_move_down_button = QPushButton()
        plot_move_down_button.setIcon(GuiUtils.get_icon('mActionArrowDown.svg'))
        plot_move_down_button.setToolTip('Move selected plot down')
        plot_tools_layout.addWidget(plot_move_down_button)
        plot_move_down_button.clicked.connect(self.move_down_plot)

        vl.addLayout(plot_tools_layout)

        self.plot_list = QListWidget()
        self.plot_list.setSelectionMode(QListWidget.SingleSelection)
        self.plot_list.doubleClicked.connect(self.show_properties)
        vl.addWidget(self.plot_list)
        self.populate_plot_list()

        plot_properties_button = QPushButton(self.tr('Setup Selected Plot'))
        vl.addWidget(plot_properties_button)
        plot_properties_button.clicked.connect(self.show_properties)

        self.panel = None
        self.setPanelTitle(self.tr('Plot Properties'))
        self.item_properties_widget = QgsLayoutItemPropertiesWidget(self, layout_object)
        vl.addWidget(self.item_properties_widget)
        self.setLayout(vl)

    def populate_plot_list(self):
        """
        Clears and re-populates the plot list widget. The currently selection is retained
        """
        selected_index = self.plot_list.currentRow()
        self.plot_list.clear()
        for setting in self.plot_item.plot_settings:
            plot_type = setting.plot_type if setting.plot_type is not None else '(not set)'
            legend_title = ('[' + setting.properties.get('name') + ']') \
                if setting.properties.get('name', '') != '' else ''
            self.plot_list.addItem(plot_type + ' ' + legend_title)

        # select index within range [0, len(plot_settings)-1]
        selected_index = max(0, min(len(self.plot_item.plot_settings) - 1, selected_index))
        self.plot_list.setCurrentRow(selected_index, QItemSelectionModel.SelectCurrent)

    def add_plot(self):
        """
         Adds a new plot and updates the plot list and the plot item
        """
        self.plot_item.add_plot()
        self.populate_plot_list()
        self.plot_item.refresh()

    def duplicate_plot(self):
        """
         Duplicates an existing plot and updates the plot list and the plot item
        """

        selected_plot_index = self.plot_list.currentRow()
        if selected_plot_index < 0:
            return

        self.plot_item.duplicate_plot(selected_plot_index)
        self.populate_plot_list()
        self.plot_item.refresh()

    def remove_plot(self):
        """
        Removes the selected plot and updates the plot list and the plot item
        """
        selected_index = self.plot_list.currentRow()
        if selected_index < 0:
            return

        self.plot_item.remove_plot(selected_index)
        self.populate_plot_list()
        self.plot_item.refresh()

    def move_up_plot(self):
        """
        Moves the selected plot up and updates the plot list and the plot item
        """
        selected_index = self.plot_list.currentRow()
        if selected_index <= 0:
            return

        item = self.plot_item.plot_settings.pop(selected_index)
        self.plot_item.plot_settings.insert(selected_index - 1, item)
        self.plot_list.setCurrentRow(selected_index - 1, QItemSelectionModel.SelectCurrent)
        self.populate_plot_list()
        self.plot_item.refresh()

    def move_down_plot(self):
        """
        Moves the selected plot down and updates the plot list and the plot item
        """
        selected_index = self.plot_list.currentRow()
        if selected_index >= len(self.plot_item.plot_settings) - 1:
            return

        item = self.plot_item.plot_settings.pop(selected_index)
        self.plot_item.plot_settings.insert(selected_index + 1, item)
        self.plot_list.setCurrentRow(selected_index + 1, QItemSelectionModel.SelectCurrent)
        self.populate_plot_list()
        self.plot_item.refresh()

    def show_properties(self):
        """
        Shows the plot properties panel
        """
        selected_plot_index = self.plot_list.currentRow()
        if selected_plot_index < 0:
            return

        self.panel = DataPlotlyPanelWidget(mode=DataPlotlyPanelWidget.MODE_LAYOUT, message_bar=self.message_bar)

        # not quite right -- we ideally want to also add the source layer scope into the context given by plot item,
        # but that causes a hard lock in the Python GIL (because PyQt doesn't release the GIL when creating the menu
        # for the property override buttons). Nothing much we can do about that here (or in QGIS,
        # it's a Python/PyQt limitation)
        self.panel.registerExpressionContextGenerator(self.plot_item)
        self.panel.set_print_layout(self.plot_item.layout())

        self.panel.linked_map_combo.blockSignals(True)
        self.panel.linked_map_combo.setItem(self.plot_item.linked_map)
        self.panel.linked_map_combo.blockSignals(False)

        self.panel.linked_map_combo.itemChanged.connect(self.linked_map_changed)

        self.panel.set_settings(self.plot_item.plot_settings[selected_plot_index])
        # self.panel.set_settings(self.layoutItem().plot_settings)
        self.openPanel(self.panel)
        self.panel.widgetChanged.connect(self.update_item_settings)
        self.panel.panelAccepted.connect(self.set_item_settings)

    def update_item_settings(self):
        """
        Updates the plot item without dismissing the properties panel
        """
        if not self.panel:
            return

        self.plot_item.set_plot_settings(self.plot_list.currentRow(), self.panel.get_settings())
        self.populate_plot_list()
        self.plot_item.update()

    def set_item_settings(self):
        """
        Updates the plot item based on the settings from the properties panel
        """
        if not self.panel:
            return

        self.plot_item.set_plot_settings(self.plot_list.currentRow(), self.panel.get_settings())
        self.populate_plot_list()
        self.panel = None
        self.plot_item.update()

    def linked_map_changed(self, linked_map):
        """
        Triggered when the linked map is changed
        """
        self.plot_item.set_linked_map(linked_map)
        self.plot_item.update()

    def setNewItem(self, item):  # pylint: disable=missing-docstring
        if item.type() != ITEM_TYPE:
            return False

        self.plot_item = item
        self.item_properties_widget.setItem(item)
        self.populate_plot_list()

        if self.panel is not None:
            self.panel.set_settings(self.plot_item.plot_settings[0])

            self.panel.linked_map_combo.blockSignals(True)
            self.panel.linked_map_combo.setItem(self.plot_item.linked_map)
            self.panel.linked_map_combo.blockSignals(False)

        return True

    def setDesignerInterface(self, iface):  # pylint: disable=missing-docstring
        super().setDesignerInterface(iface)
        self.message_bar = iface.messageBar()
        if self.panel:
            self.panel.message_bar = self.message_bar


class PlotLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):
    """
    Metadata for plot item GUI classes
    """

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('dataplotly.svg')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return PlotLayoutItemWidget(None, item)
