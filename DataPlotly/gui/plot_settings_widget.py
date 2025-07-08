"""
/***************************************************************************
 DataPlotlyDialog
                                 A QGIS plugin
 D3 Plots for QGIS
                             -------------------
        begin                : 2017-03-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by matteo ghetta
        email                : matteo.ghetta@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import json
from collections import OrderedDict
from shutil import copyfile
from functools import partial
import sys

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QListWidgetItem,
    QVBoxLayout,
    QFileDialog,
    QMenu
)
from qgis.PyQt.QtXml import QDomDocument

from qgis.PyQt.QtGui import (
    QFont,
    QImage,
    QPainter,
    QColor
)
from qgis.PyQt.QtCore import (
    QUrl,
    pyqtSignal,
    QDir,
    Qt
)
from qgis.PyQt.QtWebKit import QWebSettings
from qgis.PyQt.QtWebKitWidgets import (
    QWebView
)

from qgis.core import (
    Qgis,
    QgsNetworkAccessManager,
    QgsFeatureRequest,
    QgsMapLayerProxyModel,
    QgsProject,
    QgsFileUtils,
    QgsReferencedRectangle,
    QgsExpressionContextGenerator,
    QgsPropertyCollection,
    QgsLayoutItemRegistry,
    QgsPropertyDefinition
)
from qgis.gui import (
    QgsPanelWidget,
    QgsMessageBar,
    QgsPropertyOverrideButton
)
from qgis.utils import iface

from DataPlotly.core.core_utils import DOC_URL
from DataPlotly.core.plot_factory import PlotFactory
from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.gui.gui_utils import GuiUtils

WIDGET, _ = uic.loadUiType(
    GuiUtils.get_ui_file_path('dataplotly_dockwidget_base.ui'))

class DataPlotlyPanelWidget(QgsPanelWidget, WIDGET):  # pylint: disable=too-many-lines,too-many-instance-attributes,too-many-public-methods
    """
    Main configuration panel widget for plot settings
    """

    MODE_CANVAS = 'CANVAS'
    MODE_LAYOUT = 'LAYOUT'

    # emit signal when dialog is resized
    resizeWindow = pyqtSignal()

    def __init__(self, mode=MODE_CANVAS, parent=None, override_iface=None, message_bar: QgsMessageBar = None,  # pylint: disable=too-many-statements,too-many-arguments
                 dock_title: str = None, dock_id: str = None, project: QDomDocument = None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        if override_iface is None:
            self.iface = iface
        else:
            self.iface = override_iface

        self.mode = mode
        self.message_bar = message_bar
        self.dock_title = dock_title
        self.dock_id = dock_id

        self.setPanelTitle(self.tr('Plot Properties'))

        self.save_to_project = True
        self.read_from_project = True

        self.data_defined_properties = QgsPropertyCollection()

        # listen out for project save/restore, and update our state accordingly
        QgsProject.instance().writeProject.connect(self.write_project)
        QgsProject.instance().readProject.connect(self.read_project)
        QgsProject.instance().cleared.connect(self.clearPlotView)

        if self.iface is not None:
            self.listWidget.setIconSize(self.iface.iconSize(False))
        self.listWidget.setMaximumWidth(
            int(self.listWidget.iconSize().width() * 1.18))

        # connect signal to function to reload the plot view
        self.resizeWindow.connect(self.reloadPlotCanvas)

        # create the reload button with text and icon
        self.reload_btn.setText("Reload")
        self.reload_btn.setIcon(GuiUtils.get_icon('reload.svg'))
        self.clear_btn.setIcon(GuiUtils.get_icon('clean.svg'))
        self.update_btn.setIcon(GuiUtils.get_icon('refresh.svg'))
        self.draw_btn.setIcon(GuiUtils.get_icon('create_plot.svg'))
        # connect the button to the reload function
        self.reload_btn.clicked.connect(self.reloadPlotCanvas2)

        self.configuration_menu = QMenu(self)
        action_load_configuration = self.configuration_menu.addAction(
            self.tr("Load Configuration…"))
        action_load_configuration.triggered.connect(self.load_configuration)
        action_save_configuration = self.configuration_menu.addAction(
            self.tr("Save Configuration…"))
        action_save_configuration.triggered.connect(self.save_configuration)
        self.configuration_btn.setMenu(self.configuration_menu)

        # ListWidget icons and themes
        self.listWidget_icons = [
            QListWidgetItem(GuiUtils.get_icon('list_properties.svg'), ""),
            QListWidgetItem(GuiUtils.get_icon('list_custom.svg'), ""),
        ]

        if self.mode == DataPlotlyPanelWidget.MODE_CANVAS:
            self.listWidget_icons.extend([
                QListWidgetItem(GuiUtils.get_icon('list_plot.svg'), ""),
                QListWidgetItem(GuiUtils.get_icon('list_help.svg'), ""),
                QListWidgetItem(GuiUtils.get_icon('list_code.svg'), "")
            ])

        # fill the QListWidget with items and icons
        for i in self.listWidget_icons:
            self.listWidget.addItem(i)

        # highlight the first row when starting the first time
        self.listWidget.setCurrentRow(0)

        self.marker_size.setValue(10)
        self.marker_size.setSingleStep(0.2)
        self.marker_size.setClearValue(10)

        self.marker_width.setValue(1)
        self.marker_width.setSingleStep(0.2)
        self.marker_width.setClearValue(0, self.tr('None'))

        # pie_hole
        self.pie_hole.setClearValue(0, self.tr('None'))

        # Populate PlotTypes combobox
        # we sort available types by translated name
        type_classes = [clazz for _, clazz in PlotFactory.PLOT_TYPES.items()]
        type_classes.sort(key=lambda x: x.name().lower())
        for clazz in type_classes:
            self.plot_combo.addItem(
                clazz.icon(), clazz.name(), clazz.type_name())
        # default to scatter plots
        self.set_plot_type('scatter')

        # SubPlots combobox
        self.subcombo.addItem(self.tr('Single Plot'), 'single')
        self.subcombo.addItem(self.tr('Subplots'), 'subplots')

        # connect to the functions to clean the UI and fill with the correct
        # widgets
        self.refreshWidgets()
        self.refreshWidgets2()
        self.plot_combo.currentIndexChanged.connect(self.refreshWidgets)
        self.plot_combo.currentIndexChanged.connect(self.helpPage)
        self.subcombo.currentIndexChanged.connect(self.refreshWidgets2)
        self.marker_type_combo.currentIndexChanged.connect(
            self.refreshWidgets3)

        # fill the layer combobox with vector layers
        self.layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)

        # connect the combo boxes to the setLegend function
        self.x_combo.fieldChanged.connect(self.setLegend)
        self.y_combo.fieldChanged.connect(self.setLegend)
        self.z_combo.fieldChanged.connect(self.setLegend)

        self.draw_btn.clicked.connect(self.create_plot)
        self.update_btn.clicked.connect(self.UpdatePlot)
        self.clear_btn.clicked.connect(self.clearPlotView)
        self.save_plot_btn.clicked.connect(self.save_plot_as_image)
        self.save_plot_html_btn.clicked.connect(self.save_plot_as_html)
        self.save_plot_btn.setIcon(GuiUtils.get_icon('save_as_image.svg'))
        self.save_plot_html_btn.setIcon(GuiUtils.get_icon('save_as_html.svg'))

        # initialize the empty dictionary of plots
        self.plot_factories = {}
        # start the index counter
        self.idx = 1

        # load the help html page into the help widget
        self.layouth = QVBoxLayout()
        self.layouth.setContentsMargins(0, 0, 0, 0)
        self.help_widget.setLayout(self.layouth)
        self.help_view = QWebView()
        self.layouth.addWidget(self.help_view)
        self.helpPage()

        # load the webview of the plot a the first running of the plugin
        self.layoutw = QVBoxLayout()
        self.layoutw.setContentsMargins(0, 0, 0, 0)
        self.plot_qview.setLayout(self.layoutw)
        self.plot_view = QWebView()
        self.plot_view.page().setNetworkAccessManager(
            QgsNetworkAccessManager.instance())
        self.plot_view.statusBarMessage.connect(self.getJSmessage)
        plot_view_settings = self.plot_view.settings()
        plot_view_settings.setAttribute(QWebSettings.WebGLEnabled, True)
        plot_view_settings.setAttribute(
            QWebSettings.DeveloperExtrasEnabled, True)
        plot_view_settings.setAttribute(
            QWebSettings.Accelerated2dCanvasEnabled, True)
        self.layoutw.addWidget(self.plot_view)

        # get the plot type from the combobox
        self.ptype = self.plot_combo.currentData()

        self.layer_combo.layerChanged.connect(self.selected_layer_changed)
        # fill combo boxes when launching the UI
        self.selected_layer_changed(self.layer_combo.currentLayer())

        self.register_data_defined_button(
            self.feature_subset_defined_button, PlotSettings.PROPERTY_FILTER)
        self.register_data_defined_button(
            self.size_defined_button, PlotSettings.PROPERTY_MARKER_SIZE)
        self.size_defined_button.registerEnabledWidget(
            self.marker_size, natural=False)
        self.register_data_defined_button(
            self.stroke_defined_button, PlotSettings.PROPERTY_STROKE_WIDTH)
        self.stroke_defined_button.registerEnabledWidget(
            self.marker_width, natural=False)
        self.register_data_defined_button(
            self.in_color_defined_button, PlotSettings.PROPERTY_COLOR)
        self.in_color_defined_button.registerEnabledWidget(
            self.in_color_combo, natural=False)
        self.in_color_defined_button.changed.connect(
            self.data_defined_color_updated)
        self.register_data_defined_button(
            self.out_color_defined_button, PlotSettings.PROPERTY_STROKE_COLOR)
        self.out_color_defined_button.registerEnabledWidget(
            self.out_color_combo, natural=False)
        self.register_data_defined_button(
            self.plot_title_defined_button, PlotSettings.PROPERTY_TITLE)
        self.plot_title_defined_button.registerEnabledWidget(
            self.plot_title_line, natural=False)
        self.register_data_defined_button(
            self.legend_title_defined_button, PlotSettings.PROPERTY_LEGEND_TITLE)
        self.legend_title_defined_button.registerEnabledWidget(
            self.legend_title, natural=False)
        self.register_data_defined_button(
            self.x_axis_title_defined_button, PlotSettings.PROPERTY_X_TITLE)
        self.x_axis_title_defined_button.registerEnabledWidget(
            self.x_axis_title, natural=False)
        self.register_data_defined_button(
            self.y_axis_title_defined_button, PlotSettings.PROPERTY_Y_TITLE)
        self.y_axis_title_defined_button.registerEnabledWidget(
            self.y_axis_title, natural=False)
        self.register_data_defined_button(
            self.z_axis_title_defined_button, PlotSettings.PROPERTY_Z_TITLE)
        self.z_axis_title_defined_button.registerEnabledWidget(
            self.z_axis_title, natural=False)
        self.register_data_defined_button(
            self.x_axis_min_defined_button, PlotSettings.PROPERTY_X_MIN)
        self.x_axis_min_defined_button.registerEnabledWidget(
            self.x_axis_min, natural=False)
        self.register_data_defined_button(
            self.x_axis_max_defined_button, PlotSettings.PROPERTY_X_MAX)
        self.x_axis_max_defined_button.registerEnabledWidget(
            self.x_axis_max, natural=False)
        self.register_data_defined_button(
            self.y_axis_min_defined_button, PlotSettings.PROPERTY_Y_MIN)
        self.y_axis_min_defined_button.registerEnabledWidget(
            self.y_axis_min, natural=False)
        self.register_data_defined_button(
            self.y_axis_max_defined_button, PlotSettings.PROPERTY_Y_MAX)
        self.y_axis_max_defined_button.registerEnabledWidget(
            self.y_axis_max, natural=False)

        # connect to refreshing function of listWidget and stackedWidgets
        self.listWidget.currentRowChanged.connect(self.updateStacked)

        # connect the plot changing to the color data defined buttons
        self.plot_combo.currentIndexChanged.connect(
            self.data_defined_color_updated)

        # better default colors
        self.in_color_combo.setColor(QColor('#8EBAD9'))
        self.out_color_combo.setColor(QColor('#1F77B4'))
        self.font_title_color.setColor(QColor('#000000'))
        self.font_xlabel_color.setColor(QColor('#000000'))
        self.font_xticks_color.setColor(QColor('#000000'))
        self.font_ylabel_color.setColor(QColor('#000000'))
        self.font_yticks_color.setColor(QColor('#000000'))

        # default fonts
        self.font_title_style.setCurrentFont(QFont('Arial', 10))
        self.font_xlabel_style.setCurrentFont(QFont('Arial', 10))
        self.font_xticks_style.setCurrentFont(QFont('Arial', 10))
        self.font_ylabel_style.setCurrentFont(QFont('Arial', 10))
        self.font_yticks_style.setCurrentFont(QFont('Arial', 10))

        # set range of axis min/max spin boxes
        self.x_axis_min.setRange(sys.float_info.max * -1, sys.float_info.max)
        self.x_axis_max.setRange(sys.float_info.max * -1, sys.float_info.max)
        self.y_axis_min.setRange(sys.float_info.max * -1, sys.float_info.max)
        self.y_axis_max.setRange(sys.float_info.max * -1, sys.float_info.max)

        # default gridaxis color
        self.layout_grid_axis_color.setColor(QColor('#bdbfc0'))

        self.pid = None
        self.plot_path = None
        self.plot_url = None
        self.plot_file = None

        if self.mode == DataPlotlyPanelWidget.MODE_LAYOUT:
            self.update_btn.setEnabled(True)
            # hide for now
            self.draw_btn.setVisible(False)
            self.clear_btn.setVisible(False)
            self.subcombo.setVisible(False)
            self.subcombo_label.setVisible(False)
            self.visible_feature_check.setVisible(False)
            self.selected_feature_check.setVisible(False)
        else:
            self.iface.mapCanvas().extentsChanged.connect(self.update_plot_visible_rect)
            self.label_linked_map.setVisible(False)
            self.linked_map_combo.setVisible(False)
            self.filter_by_map_check.setVisible(False)
            self.filter_by_atlas_check.setVisible(False)

        QgsProject.instance().layerWillBeRemoved.connect(self.layer_will_be_removed)

        # new dock instance from project
        if project:
            self.read_project(project)

    def updateStacked(self, row):
        """
        according to the listWdiget row change the stackedWidget and
        nestedStackedWidget
        """

        # stackedWidget index = 1 and change just the nestedStackedWidgets
        if 0 <= row <= 1:
            self.stackedPlotWidget.setCurrentIndex(0)
            self.stackedNestedPlotWidget.setCurrentIndex(row)

        # change the stackedWidgets index
        elif row > 1:
            self.stackedPlotWidget.setCurrentIndex(row - 1)

    def registerExpressionContextGenerator(self, generator: QgsExpressionContextGenerator):
        """
        Register the panel's expression context generator with all relevant children
        """
        self.x_combo.registerExpressionContextGenerator(generator)
        self.y_combo.registerExpressionContextGenerator(generator)
        self.z_combo.registerExpressionContextGenerator(generator)
        self.additional_info_combo.registerExpressionContextGenerator(
            generator)

        buttons = self.findChildren(QgsPropertyOverrideButton)
        for button in buttons:
            button.registerExpressionContextGenerator(generator)

    def register_data_defined_button(self, button, property_key: int):
        """
        Registers a new data defined button, linked to the given property key (see values in PlotSettings)
        """
        button.init(property_key, self.data_defined_properties,
                    PlotSettings.DYNAMIC_PROPERTIES, None, False)
        button.changed.connect(self._update_property)

    def _update_property(self):
        """
        Triggered when a property override button value is changed
        """
        button = self.sender()
        self.data_defined_properties.setProperty(
            button.propertyKey(), button.toProperty())

    def update_data_defined_button(self, button):
        """
        Updates the current state of a property override button to reflect the current
        property value
        """
        if button.propertyKey() < 0:
            return

        button.blockSignals(True)
        button.setToProperty(
            self.data_defined_properties.property(button.propertyKey()))
        button.blockSignals(False)

    def set_print_layout(self, print_layout):
        """
        Sets the print layout linked with the widget, if in print layout mode
        """
        self.linked_map_combo.setCurrentLayout(print_layout)
        self.linked_map_combo.setItemType(QgsLayoutItemRegistry.LayoutMap)

    def set_plot_type(self, plot_type: str):
        """
        Sets the current plot type shown in the dialog
        """
        self.plot_combo.setCurrentIndex(self.plot_combo.findData(plot_type))

    def data_defined_color_updated(self):
        """
        refreshing function for color data defined button

        sets the vector layer to the data defined buttons

        checks is the datadefined button is active and check also the plot type
        in order to deactivate the color when not needed
        """

        # set the vector layer for all the data defined buttons
        layer = self.layer_combo.currentLayer()
        buttons = self.findChildren(QgsPropertyOverrideButton)
        for button in buttons:
            button.setVectorLayer(layer)

        # if data defined button is active
        if self.in_color_defined_button.isActive():
            # if plot is type for which using an expression for the color selection makes sense
            if self.ptype in ['scatter', 'bar', 'pie', 'ternary', 'histogram']:
                self.in_color_combo.setEnabled(False)
                self.color_scale_data_defined_in.setVisible(True)
                self.color_scale_data_defined_in.setEnabled(True)
                self.color_scale_data_defined_in_label.setVisible(True)
                self.color_scale_data_defined_in_label.setEnabled(True)
                self.color_scale_data_defined_in_check.setVisible(True)
                self.color_scale_data_defined_in_check.setEnabled(True)
                self.color_scale_data_defined_in_invert_check.setVisible(True)
                self.color_scale_data_defined_in_invert_check.setEnabled(True)
            # if plot is type for which using an expression for the color selection does not make sense
            else:
                self.in_color_combo.setEnabled(True)
                self.color_scale_data_defined_in.setVisible(False)
                self.color_scale_data_defined_in.setEnabled(False)
                self.color_scale_data_defined_in_label.setVisible(False)
                self.color_scale_data_defined_in_label.setEnabled(False)
                self.color_scale_data_defined_in_check.setVisible(False)
                self.color_scale_data_defined_in_check.setEnabled(False)
                self.color_scale_data_defined_in_invert_check.setVisible(False)
                self.color_scale_data_defined_in_invert_check.setEnabled(False)
        # if datadefined button is deactivated
        else:
            self.in_color_combo.setEnabled(True)
            self.color_scale_data_defined_in.setVisible(False)
            self.color_scale_data_defined_in.setEnabled(False)
            self.color_scale_data_defined_in_label.setVisible(False)
            self.color_scale_data_defined_in_check.setVisible(False)
            self.color_scale_data_defined_in_invert_check.setVisible(False)

    def selected_layer_changed(self, layer):
        """
        Trigger actions after selected layer changes
        """
        self.y_fields_combo.clear()
        self.x_combo.setLayer(layer)
        self.y_combo.setLayer(layer)
        self.y_combo_radar_label.setLayer(layer)
        self.z_combo.setLayer(layer)
        self.additional_info_combo.setLayer(layer)

        if layer is not None :
            self.y_fields_combo.addItems([field.name() for field in layer.fields()])
        buttons = self.findChildren(QgsPropertyOverrideButton)
        for button in buttons:
            button.setVectorLayer(layer)

    def layer_will_be_removed(self, layer_id):
        """
        Triggered when a layer is about to be removed
        """
        self.plot_factories = {k: v for k, v in self.plot_factories.items() if
                               not v.source_layer or v.source_layer.id() != layer_id}

    def getJSmessage(self, status):
        """
        landing method for statusBarMessage signal coming from PLOT.js_callback
        it decodes feature ids of clicked or selected plot elements,
        selects on map canvas and triggers a pan/zoom to them

        the method handles several exceptions:
            the first try/except is due to the connection to the init method

            second try/except looks into the decoded status, that is, it decodes
            the js dictionary and loop where it is necessary

            the dic js dictionary contains several information useful to handle
            correctly every operation
        """

        try:
            dic = json.JSONDecoder().decode(status)
        except:  # pylint: disable=bare-except  # noqa: F401
            dic = None

        # print('STATUS', status, dic)

        try:
            # check the user behavior linked to the js script

            # if a selection event is performed
            if dic['mode'] == 'selection':
                if dic['type'] == 'scatter':
                    self.layer_combo.currentLayer().selectByIds(dic['id'])
                else:
                    self.layer_combo.currentLayer().selectByIds(dic['tid'])

            # if a clicking event is performed depending on the plot type
            elif dic["mode"] == 'clicking':
                if dic['type'] == 'scatter':
                    self.layer_combo.currentLayer().selectByIds([dic['fidd']])
                elif dic["type"] == 'pie':
                    exp = """ "{}" = '{}' """.format(
                        dic['field'], dic['label'])
                    # set the iterator with the expression as filter in feature request
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds(
                        [f.id() for f in it])
                elif dic["type"] == 'histogram':
                    vmin = dic['id'] - dic['bin_step'] / 2
                    vmax = dic['id'] + dic['bin_step'] / 2
                    exp = """ "{}" <= {} AND "{}" > {} """.format(
                        dic['field'], vmax, dic['field'], vmin)
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds(
                        [f.id() for f in it])
                elif dic["type"] == 'scatterternary':
                    self.layer_combo.currentLayer().selectByIds([dic['fid']])
                else:
                    # build the expression from the js dic (customdata)
                    exp = """ "{}" = '{}' """.format(dic['field'], dic['id'])
                    # set the iterator with the expression as filter in feature request
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds(
                        [f.id() for f in it])
                    # print(exp)
        except:  # pylint: disable=bare-except # noqa: F401
            pass

    def helpPage(self):
        """
        change the page of the manual according to the plot type selected and
        the language (looks for translations)
        """

        # locale = QSettings().value('locale/userLocale', 'en_US')[0:2]

        self.help_view.load(QUrl(''))
        self.layouth.addWidget(self.help_view)
        help_url = QUrl(f'{DOC_URL}/en/latest/{self.ptype}.html')
        self.help_view.load(help_url)

    def resizeEvent(self, event):
        """
        reimplemented event to detect the dialog resizing
        """
        self.resizeWindow.emit()
        return super().resizeEvent(event)  # pylint:disable=super-with-arguments

    def reloadPlotCanvas(self):
        """
        just reload the plot view controlling the check state
        """
        if self.live_update_check.isChecked():
            self.plot_view.reload()

    def reloadPlotCanvas2(self):
        """
        just reload the plot view
        """
        self.plot_view.reload()

    def refreshListWidget(self):
        """
        highlight the item in the QListWidget when the QStackWidget changes

        needed to highligh the correct icon when the plot is rendered
        """
        self.listWidget.setCurrentRow(self.stackedPlotWidget.currentIndex())

    def refreshWidgets(self):  # pylint: disable=too-many-statements,too-many-branches
        """
        just for refreshing the UI

        widgets depending on the plot type in the combobox to have a cleaner
        interface

        self.widgetType is a dict of widget depending on the plot type chosen
        'all': is for all the plot type, else the name of the plot is
        explicitated

        BE AWARE: if loops are just for widgets that already exist! If a widget
        is proper to a specific plot and is put within the if statement, the
        method p.buildProperties will fail!
        In the statement there have to be only widgets that, for example, need
        to be re-rendered (label name...)
        """

        # get the plot type from the combobox
        self.ptype = self.plot_combo.currentData()
        # BoxPlot BarPlot and Histogram orientation (same values)
        self.orientation_combo.clear()
        self.orientation_combo.addItem(self.tr('Vertical'), 'v')
        self.orientation_combo.addItem(self.tr('Horizontal'), 'h')

        # BoxPlot and Violin outliers
        self.outliers_combo.clear()
        self.outliers_combo.addItem(self.tr('No Outliers'), False)
        self.outliers_combo.addItem(self.tr('Standard Outliers'), 'outliers')
        self.outliers_combo.addItem(
            self.tr('Suspected Outliers'), 'suspectedoutliers')
        self.outliers_combo.addItem(self.tr('All Points'), 'all')

        # BoxPlot statistic types
        self.box_statistic_combo.clear()
        self.box_statistic_combo.addItem(self.tr('None'), False)
        self.box_statistic_combo.addItem(self.tr('Mean'), True)
        self.box_statistic_combo.addItem(self.tr('Standard Deviation'), 'sd')

        # BoxPlot and ScatterPlot X axis type
        self.x_axis_mode_combo.clear()
        self.x_axis_mode_combo.addItem(self.tr('Linear'), 'linear')
        self.x_axis_mode_combo.addItem(self.tr('Logarithmic'), 'log')
        self.x_axis_mode_combo.addItem(self.tr('Categorized'), 'category')
        self.y_axis_mode_combo.clear()
        self.y_axis_mode_combo.addItem(self.tr('Linear'), 'linear')
        self.y_axis_mode_combo.addItem(self.tr('Logarithmic'), 'log')
        self.y_axis_mode_combo.addItem(self.tr('Categorized'), 'category')

        # ScatterPlot marker types
        self.marker_types = OrderedDict([
            (self.tr('Points'), 'markers'),
            (self.tr('Lines'), 'lines'),
            (self.tr('Points and Lines'), 'lines+markers')
        ])
        self.marker_type_combo.clear()
        for k, v in self.marker_types.items():
            self.marker_type_combo.addItem(k, v)

        # Point types
        self.point_types = OrderedDict([
            (GuiUtils.get_icon('circle.svg'), 'circle'),
            (GuiUtils.get_icon('square.svg'), 'square'),
            (GuiUtils.get_icon('diamond.svg'), 'diamond'),
            (GuiUtils.get_icon('cross.svg'), 'cross'),
            (GuiUtils.get_icon('x.svg'), 'x'),
            (GuiUtils.get_icon('triangle.svg'), 'triangle'),
            (GuiUtils.get_icon('penta.svg'), 'penta'),
            (GuiUtils.get_icon('star.svg'), 'star'),
        ])

        self.point_types2 = OrderedDict([
            ('circle', 0),
            ('square', 1),
            ('diamond', 2),
            ('cross', 3),
            ('x', 4),
            ('triangle', 5),
            ('penta', 13),
            ('star', 17),
        ])

        self.point_combo.clear()
        for k, v in self.point_types.items():
            self.point_combo.addItem(k, '', v)

        self.line_types = OrderedDict([
            (GuiUtils.get_icon('solid.png'), self.tr('Solid Line')),
            (GuiUtils.get_icon('dot.png'), self.tr('Dot Line')),
            (GuiUtils.get_icon('dash.png'), self.tr('Dash Line')),
            (GuiUtils.get_icon('longdash.png'), self.tr('Long Dash Line')),
            (GuiUtils.get_icon('dotdash.png'), self.tr('Dot Dash Line')),
            (GuiUtils.get_icon('longdashdot.png'), self.tr('Long Dash Dot Line')),
        ])

        self.line_types2 = OrderedDict([
            (self.tr('Solid Line'), 'solid'),
            (self.tr('Dot Line'), 'dot'),
            (self.tr('Dash Line'), 'dash'),
            (self.tr('Long Dash Line'), 'longdash'),
            (self.tr('Dot Dash Line'), 'dashdot'),
            (self.tr('Long Dash Dot Line'), 'longdashdot'),
        ])

        self.line_combo.clear()
        self.line_combo_threshold.clear()
        for k, v in self.line_types.items():
            self.line_combo.addItem(k, v)
            self.line_combo_threshold.addItem(k,v)



        # BarPlot bar mode
        self.bar_mode_combo.clear()
        self.bar_mode_combo.addItem(self.tr('Grouped'), 'group')
        self.bar_mode_combo.addItem(self.tr('Stacked'), 'stack')
        self.bar_mode_combo.addItem(self.tr('Overlay'), 'overlay')

        # Histogram normalization mode
        self.hist_norm_combo.clear()
        self.hist_norm_combo.addItem(self.tr('Enumerated'), '')
        self.hist_norm_combo.addItem(self.tr('Percents'), 'percent')
        self.hist_norm_combo.addItem(self.tr('Probability'), 'probability')
        self.hist_norm_combo.addItem(self.tr('Density'), 'density')
        self.hist_norm_combo.addItem(
            self.tr('Prob Density'), 'probability density')

        # Contour Plot rendering type
        self.contour_type = OrderedDict([
            (self.tr('Fill'), 'fill'),
            (self.tr('Heatmap'), 'heatmap'),
            (self.tr('Only Lines'), 'lines'),
        ])
        self.contour_type_combo.clear()
        for k, v in self.contour_type.items():
            self.contour_type_combo.addItem(k, v)

        # Contour Plot color scale and Data Defined Color scale

        scale_color_dict = {'Grey Scale': 'Greys',
                            'Green Scale': 'Greens',
                            'Fire Scale': 'Hot',
                            'BlueYellowRed': 'Portland',
                            'BlueGreenRed': 'Jet',
                            'BlueToRed': 'RdBu',
                            'BlueToRed Soft': 'Bluered',
                            'BlackRedYellowBlue': 'Blackbody',
                            'Terrain': 'Earth',
                            'Electric Scale': 'Electric',
                            'RedOrangeYellow': 'YlOrRd', # fix from https://github.com/plotly/graphing-library-docs/issues/14
                            'DeepblueBlueWhite': 'YlGnBu', # fix from https://github.com/plotly/graphing-library-docs/issues/14
                            'BlueWhitePurple': 'Picnic'}

     
        self.color_scale_combo.clear()
        self.color_scale_data_defined_in.clear()

        for k, v in scale_color_dict.items():
            self.color_scale_combo.addItem(k, v)
            self.color_scale_data_defined_in.addItem(k, v)

        # according to the plot type, change the label names

        # BoxPlot
        if self.ptype in ('box', 'violin'):
            self.x_label.setText(self.tr('Grouping field \n(optional)'))
            # set the horizontal and vertical size of the label and reduce the label font size
            ff = QFont()
            ff.setPointSizeF(8)
            self.x_label.setFont(ff)
            self.x_label.setFixedWidth(100)
            self.orientation_label.setText(self.tr('Box orientation'))
            self.in_color_lab.setText(self.tr('Box color'))
            self.register_data_defined_button(
                self.in_color_defined_button, PlotSettings.PROPERTY_COLOR)

        elif self.ptype in ('scatter', 'ternary', 'bar', '2dhistogram', 'contour', 'polar','radar'):
            self.x_label.setText(self.tr('X field'))
            self.x_label.setFont(self.font())

            if self.ptype in ('scatter', 'ternary'):
                self.in_color_lab.setText(self.tr('Marker color'))
            elif self.ptype == 'bar':
                self.orientation_label.setText(self.tr('Bar orientation'))
                self.in_color_lab.setText(self.tr('Bar color'))
            self.register_data_defined_button(
                self.in_color_defined_button, PlotSettings.PROPERTY_COLOR)

        elif self.ptype == 'pie':
            self.x_label.setText(self.tr('Grouping field'))
            ff = QFont()
            ff.setPointSizeF(8.5)
            self.x_label.setFont(ff)
            self.x_label.setFixedWidth(80)
            # Register button again with more specific help text
            self.in_color_defined_button.init(
                PlotSettings.PROPERTY_COLOR, self.data_defined_properties.property(
                    PlotSettings.PROPERTY_COLOR),
                QgsPropertyDefinition(
                    'color', QgsPropertyDefinition.DataTypeString, 'Color Array',
                    "string [<b>r,g,b,a</b>] as int 0-255 or #<b>AARRGGBB</b> as hex or <b>color</b> as color's name, "
                    "or an array of such strings"
                ), None, False
            )
            self.in_color_defined_button.changed.connect(self._update_property)

        elif self.ptype == 'histogram':
            # Register button again with more specific help text
            self.in_color_defined_button.init(
                PlotSettings.PROPERTY_COLOR, self.data_defined_properties.property(
                    PlotSettings.PROPERTY_COLOR),
                QgsPropertyDefinition(
                    'color', QgsPropertyDefinition.DataTypeString, 'Color Array',
                    "string [<b>r,g,b,a</b>] as int 0-255 or #<b>AARRGGBB</b> as hex or <b>color</b> as color's name, "
                    "or an array of such strings"
                ), None, False
            )

        # change the label and the spin box value when the bar plot is chosen
        if self.ptype == 'bar':
            self.marker_size_lab.setText(self.tr('Bar width'))
            self.marker_size.setValue(0.0)
            self.marker_size.setClearValue(0.0, self.tr('Auto'))
            self.marker_size.setToolTip(self.tr('Set to Auto to automatically resize the bar width'))

        # change the label and the spin box value when the scatter plot is chosen
        if self.ptype == 'scatter':
            self.marker_size_lab.setText(self.tr('Marker size'))
            self.marker_size.setValue(10)

        # info combo for data hovering
        self.info_combo.clear()
        self.info_combo.addItem(self.tr('All Values'), 'all')
        self.info_combo.addItem(self.tr('X Values'), 'x')
        self.info_combo.addItem(self.tr('Y Values'), 'y')
        self.info_combo.addItem(self.tr('No Data'), 'none')

        # label text position choice
        self.combo_text_position.clear()
        self.combo_text_position.addItem(self.tr('Automatic'), 'auto')
        self.combo_text_position.addItem(self.tr('Inside bar'), 'inside')
        self.combo_text_position.addItem(self.tr('Outside bar'), 'outside')

        # Violin side
        self.violinSideCombo.clear()
        self.violinSideCombo.addItem(self.tr('Both Sides'), 'both')
        self.violinSideCombo.addItem(self.tr('Only Left'), 'negative')
        self.violinSideCombo.addItem(self.tr('Only right'), 'positive')

        # dictionary with all the widgets and the plot they belong to
        self.widgetType = {
            # plot properties
            self.layer_combo: ['all'],
            self.feature_subset_defined_button: ['all'],
            self.x_label: ['scatter', 'bar', 'box', 'pie', '2dhistogram','histogram', 'polar', 'ternary', 'violin', 'contour'],
            self.x_combo: ['scatter', 'bar', 'box','pie' '2dhistogram','histogram', 'polar', 'ternary', 'violin', 'contour'],
            self.y_fields_label: ['radar'],
            self.y_fields_combo: ['radar'],
            self.y_combo_radar_label: ['radar'],
            self.y_radar_label: ['radar'],
            self.y_label: ['scatter', 'bar', 'box', 'pie', '2dhistogram', 'polar', 'ternary', 'contour', 'violin'],
            self.y_combo: ['scatter', 'bar', 'box', 'pie', '2dhistogram', 'polar', 'ternary', 'contour', 'violin'],
            self.z_label: ['ternary'],
            self.z_combo: ['ternary'],
            self.info_label: ['scatter'],
            self.info_combo: ['scatter'],
            self.in_color_lab: ['scatter', 'bar', 'box', 'pie', 'histogram', 'polar', 'ternary', 'violin'],
            self.in_color_combo: ['scatter', 'bar', 'box', 'pie', 'histogram', 'polar', 'ternary', 'violin'],
            self.in_color_defined_button: ['scatter', 'bar', 'box', 'pie', 'histogram', 'polar', 'ternary'],
            self.color_scale_data_defined_in: ['scatter', 'bar', 'pie', 'histogram', 'ternary'],
            self.color_scale_data_defined_in_label: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in_check: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in_invert_check: ['bar', 'ternary'],
            self.out_color_lab: ['scatter', 'bar', 'box', 'pie', 'histogram', 'polar', 'ternary', 'violin'],
            self.out_color_combo: ['scatter', 'bar', 'box', 'pie', 'histogram', 'polar', 'ternary', 'violin'],
            self.out_color_defined_button: ['scatter', 'bar', 'box', 'pie', 'histogram', 'polar', 'ternary', 'violin'],
            self.marker_width_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.marker_width: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.stroke_defined_button: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.marker_size_lab: ['scatter', 'polar', 'ternary', 'bar', 'radar'],
            self.marker_size: ['scatter', 'polar', 'ternary', 'bar', 'radar'],
            self.size_defined_button: ['scatter', 'polar','ternary', 'bar'],
            self.marker_type_lab: ['scatter', 'polar','radar'],
            self.marker_type_combo: ['scatter', 'polar','radar'],
            self.alpha_lab: ['scatter', 'bar', 'box', 'histogram', 'polar','radar', 'ternary', 'violin', 'contour'],
            self.opacity_widget: ['scatter', 'bar', 'box', 'pie', 'histogram', 'polar', 'radar','ternary', 'violin', 'contour'],
            self.properties_group_box: ['scatter', 'bar', 'box', 'pie', 'histogram', 'polar', 'radar','ternary', 'contour', '2dhistogram',
                                        'violin'],
            self.bar_mode_lab: ['bar', 'histogram'],
            self.bar_mode_combo: ['bar', 'histogram'],
            self.legend_label: ['all'],
            self.legend_title: ['all'],
            self.legend_title_defined_button: ['all'],
            self.point_lab: ['scatter', 'ternary', 'polar'],
            self.point_combo: ['scatter', 'ternary', 'polar'],
            self.line_lab: ['scatter', 'polar', 'radar',],
            self.line_combo: ['scatter', 'polar', 'radar'],
            self.color_scale_label: ['contour', '2dhistogram', 'radar'],
            self.color_scale_combo: ['contour', '2dhistogram', 'radar'],
            self.contour_type_label: ['contour'],
            self.contour_type_combo: ['contour'],
            self.show_lines_check: ['contour'],
            # layout customization
            self.show_legend_check: ['all'],
            self.orientation_legend_check: ['scatter', 'bar', 'box', 'histogram', 'ternary', 'pie', 'violin'],
            self.plot_title_lab: ['all'],
            self.plot_title_line: ['all'],
            self.plot_title_defined_button: ['all'],
            self.font_title_label: ['all'],
            self.font_xlabel_label: ['scatter', 'bar', 'box', 'pie', '2dhistogram','histogram', 'polar','ternary', 'contour', 'violin'],
            self.font_xticks_label: ['all'],
            self.font_ylabel_label: ['all'],
            self.font_yticks_label: ['scatter', 'bar', 'box', 'pie', '2dhistogram','histogram', 'polar','ternary', 'contour', 'violin'],
            self.font_title_style: ['all'],
            self.font_xlabel_style:  ['scatter', 'bar', 'box', 'pie', '2dhistogram','histogram', 'polar','ternary', 'contour', 'violin'],
            self.font_xticks_style: ['all'],
            self.font_ylabel_style: ['all'],
            self.font_yticks_style:  ['scatter', 'bar', 'box', 'pie', '2dhistogram','histogram', 'polar','ternary', 'contour', 'violin'],
            self.font_title_color: ['all'],
            self.font_xlabel_color:  ['scatter', 'bar', 'box', 'pie', '2dhistogram','histogram', 'polar','ternary', 'contour', 'violin'],
            self.font_xticks_color: ['all'],
            self.font_ylabel_color: ['all'],
            self.font_yticks_color:  ['scatter', 'bar', 'box', 'pie', '2dhistogram','histogram', 'polar','ternary', 'contour', 'violin'],
            self.x_axis_label: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary', 'violin'],
            self.x_axis_title: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary', 'violin'],
            self.x_axis_title_defined_button: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary', 'violin'],
            self.y_axis_label: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary', 'violin'],
            self.y_axis_title: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary', 'violin'],
            self.y_axis_title_defined_button: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary', 'violin'],
            self.z_axis_label: ['ternary'],
            self.z_axis_title: ['ternary'],
            self.z_axis_title_defined_button: ['ternary'],
            self.x_axis_mode_label: ['scatter', 'box'],
            self.y_axis_mode_label: ['scatter', 'box'],
            self.x_axis_mode_combo: ['scatter', 'box'],
            self.y_axis_mode_combo: ['scatter', 'box'],
            self.invert_x_check: ['scatter', 'bar', 'box', 'histogram', '2dhistogram'],
            self.invert_y_check: ['scatter', 'bar', 'box', 'histogram', '2dhistogram'],
            self.x_axis_bounds_check: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.x_axis_min_label: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.x_axis_max_label: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.x_axis_min: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.x_axis_max: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.x_axis_min_defined_button: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.x_axis_max_defined_button: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.y_axis_bounds_check: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.y_axis_min_label: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.y_axis_max_label: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.y_axis_min: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.y_axis_max: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.y_axis_min_defined_button: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.y_axis_max_defined_button: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'violin'],
            self.orientation_label: ['bar', 'box', 'histogram', 'violin'],
            self.orientation_combo: ['bar', 'box', 'histogram', 'violin'],
            self.box_statistic_label: ['box'],
            self.box_statistic_combo: ['box'],
            self.outliers_label: ['box', 'violin'],
            self.outliers_combo: ['box', 'violin'],
            self.showMeanCheck: ['violin'],
            self.range_slider_combo: ['scatter'],
            self.hist_norm_label: ['histogram'],
            self.hist_norm_combo: ['histogram'],
            self.additional_info_label: ['scatter', 'ternary', 'bar'],
            self.additional_info_combo: ['scatter', 'ternary', 'bar'],
            self.hover_as_text_check: ['scatter'],
            self.label_text_position: ['bar'],
            self.combo_text_position: ['bar'],
            self.cumulative_hist_check: ['histogram'],
            self.invert_hist_check: ['histogram'],
            self.bins_check: ['histogram'],
            self.bins_value: ['histogram'],
            self.bar_gap_label: ['histogram'],
            self.bar_gap: ['histogram'],
            self.violinSideLabel: ['violin'],
            self.violinSideCombo: ['violin'],
            self.violinBox: ['violin'],
            self.pie_hole_label : ['pie'],
            self.pie_hole : ['pie'],
            self.fill : ['radar'],
            self.threshold: ['radar'],
            self.threshold_value: ['radar'],
            self.line_threshold_value: ['radar'],
            self.line_combo_threshold: ['radar'],
            self.threshold_value_label: ['radar']

        }
        # enable the widget according to the plot type
        for k, v in self.widgetType.items():
            if 'all' in v or self.ptype in v:
                k.setEnabled(True)
                k.setVisible(True)
            else:
                k.setEnabled(False)
                k.setVisible(False)

        # disable by default the bins value box
        # if not explicit, the upper loop will enable it
        self.bins_value.setEnabled(False)

        # disable at first run the color data defined buttons
        self.color_scale_data_defined_in.setVisible(False)
        self.color_scale_data_defined_in_label.setVisible(False)
        self.color_scale_data_defined_in_check.setVisible(False)
        self.color_scale_data_defined_in_invert_check.setVisible(False)

        self.refreshWidgets3()

    def refreshWidgets2(self):
        """
        just refresh the UI to make the radiobuttons visible when SubPlots
        """

        # enable radio buttons for subplots
        if self.subcombo.currentData() == 'subplots':
            self.radio_rows.setEnabled(True)
            self.radio_rows.setVisible(True)
            self.radio_columns.setEnabled(True)
            self.radio_columns.setVisible(True)
        else:
            self.radio_rows.setEnabled(False)
            self.radio_rows.setVisible(False)
            self.radio_columns.setEnabled(False)
            self.radio_columns.setVisible(False)

    def refreshWidgets3(self):
        """
        refresh the UI according to Point, Lines or both choosen for the symbols
        of scatterplot
        """

        if self.marker_type_combo.currentText() == self.tr('Points'):
            self.point_lab.setEnabled(True)
            self.point_lab.setVisible(True)
            self.point_combo.setEnabled(True)
            self.point_combo.setVisible(True)
            self.line_lab.setEnabled(False)
            self.line_lab.setVisible(False)
            self.line_combo.setEnabled(False)
            self.line_combo.setVisible(False)
        elif self.marker_type_combo.currentText() == self.tr('Lines'):
            self.point_lab.setEnabled(False)
            self.point_lab.setVisible(False)
            self.point_combo.setEnabled(False)
            self.point_combo.setVisible(False)
            self.line_lab.setEnabled(True)
            self.line_lab.setVisible(True)
            self.line_combo.setEnabled(True)
            self.line_combo.setVisible(True)
        else:
            self.point_lab.setEnabled(True)
            self.point_lab.setVisible(True)
            self.point_combo.setEnabled(True)
            self.point_combo.setVisible(True)
            self.line_lab.setEnabled(True)
            self.line_lab.setVisible(True)
            self.line_combo.setEnabled(True)
            self.line_combo.setVisible(True)

    def setLegend(self):
        """
        set the legend from the fields combo boxes
        """
        if self.ptype in ('box', 'bar'):
            self.legend_title.setText(self.y_combo.currentText())
        elif self.ptype == 'histogram':
            self.legend_title.setText(self.x_combo.currentText())

        else:
            legend_title_string = (
                f'{self.x_combo.currentText()} - {self.y_combo.currentText()}')
            self.legend_title.setText(legend_title_string)

    def get_settings(self) -> PlotSettings:  # pylint: disable=R0915
        """
        Returns the plot settings as currently defined in the dialog
        """
        # get the plot type from the combo box
        self.ptype = self.plot_combo.currentData()
        # if colorscale should be visible or not
        color_scale_visible = self.color_scale_data_defined_in_check.isVisible(
        ) and self.color_scale_data_defined_in_check.isChecked()

        # dictionary of all the plot properties
        plot_properties = {'custom': [self.x_combo.currentText()],
                           'hover_text': self.info_combo.currentData(),
                           'hover_label_text': '+text' if self.hover_as_text_check.isChecked() else None,
                           'hover_label_position': self.combo_text_position.currentData(),
                           'x_name': self.x_combo.currentText(),
                           'y_name': self.y_combo.currentText(),
                           'z_name': self.z_combo.currentText(),
                           'in_color': self.in_color_combo.color().name(),
                           'show_colorscale_legend': color_scale_visible,
                           'invert_color_scale': self.color_scale_data_defined_in_invert_check.isChecked(),
                           'out_color': self.out_color_combo.color().name(),
                           'marker_width': self.marker_width.value(),
                           'marker_size': self.marker_size.value(),
                           'marker_symbol': self.point_types2[self.point_combo.currentData()],
                           'line_dash': self.line_types2[self.line_combo.currentText()],
                           'box_orientation': self.orientation_combo.currentData(),
                           'marker': self.marker_types[self.marker_type_combo.currentText()],
                           'opacity': self.opacity_widget.opacity(),
                           'box_stat': self.box_statistic_combo.currentData(),
                           'box_outliers': self.outliers_combo.currentData(),
                           'name': self.legend_title.text(),
                           'normalization': self.hist_norm_combo.currentData(),
                           'cont_type': self.contour_type[self.contour_type_combo.currentText()],
                           'color_scale': None,
                           'show_lines': self.show_lines_check.isChecked(),
                           'cumulative': self.cumulative_hist_check.isChecked(),
                           'invert_hist': 'decreasing' if self.invert_hist_check.isChecked() else 'increasing',
                           'bins': self.bins_value.value(),
                           'show_mean_line': self.showMeanCheck.isChecked(),
                           'violin_side': self.violinSideCombo.currentData(),
                           'violin_box': self.violinBox.isChecked(),
                           'selected_features_only': self.selected_feature_check.isChecked(),
                           'visible_features_only': self.visible_feature_check.isChecked(),
                           'color_scale_data_defined_in_check': False,
                           'color_scale_data_defined_in_invert_check': False,
                           'marker_type_combo': self.marker_type_combo.currentText(),
                           'point_combo': self.point_combo.currentText(),
                           'line_combo': self.line_combo.currentText(),
                           'contour_type_combo': self.contour_type_combo.currentText(),
                           'show_lines_check': self.show_lines_check.isChecked(),
                           'layout_filter_by_map': self.filter_by_map_check.isChecked(),
                           'layout_filter_by_atlas': self.filter_by_atlas_check.isChecked(),
                           'pie_hole': self.pie_hole.value(),
                           'fill':  self.fill.isChecked(),
                           'threshold':  self.threshold.isChecked(),
                           'y_combo_radar_label': self.y_combo_radar_label.currentText(),
                           'line_dash_threshold':  self.line_types2[self.line_combo_threshold.currentText()],
                           'line_combo_threshold':  self.line_combo_threshold.currentText(),
                           'threshold_value': self.threshold_value.value(),
                           'y_fields_combo': ', '.join(self.y_fields_combo.checkedItems())
                           }

        if self.in_color_defined_button.isActive():
            plot_properties['color_scale_data_defined_in_check'] = self.color_scale_data_defined_in_check.isChecked()
            plot_properties[
                'color_scale_data_defined_in_invert_check'] = self.color_scale_data_defined_in_invert_check.isChecked()
            if self.ptype in self.widgetType[self.color_scale_data_defined_in]:
                plot_properties['color_scale'] = self.color_scale_data_defined_in.currentData(
                )
        else:
            plot_properties['color_scale'] = self.color_scale_combo.currentData()

        # add widgets properties to the dictionary

        # build the layout customizations
        layout_properties = {'legend': self.show_legend_check.isChecked(),
                             'legend_orientation': 'h' if self.orientation_legend_check.isChecked() else 'v',

                             'title': self.plot_title_line.text(),
                             'font_title_size': max(
            self.font_title_style.currentFont().pixelSize(),
            self.font_title_style.currentFont().pointSize()),
            'font_title_family': self.font_title_style.currentFont().family(),
            'font_title_color': self.font_title_color.color().name(),
            'font_xlabel_size': max(
            self.font_xlabel_style.currentFont().pixelSize(),
            self.font_xlabel_style.currentFont().pointSize()),
            'font_xlabel_family': self.font_xlabel_style.currentFont().family(),
            'font_xlabel_color': self.font_xlabel_color.color().name(),
            'font_xticks_size': max(
            self.font_xticks_style.currentFont().pixelSize(),
            self.font_xticks_style.currentFont().pointSize()),
            'font_xticks_family': self.font_xticks_style.currentFont().family(),
            'font_xticks_color': self.font_xticks_color.color().name(),
            'font_ylabel_size': max(
            self.font_ylabel_style.currentFont().pixelSize(),
            self.font_ylabel_style.currentFont().pointSize()),
            'font_ylabel_family': self.font_ylabel_style.currentFont().family(),
            'font_ylabel_color': self.font_ylabel_color.color().name(),
            'font_yticks_size': max(
            self.font_yticks_style.currentFont().pixelSize(),
            self.font_yticks_style.currentFont().pointSize()),
            'font_yticks_family': self.font_yticks_style.currentFont().family(),
            'font_yticks_color': self.font_yticks_color.color().name(),
            'x_title': self.x_axis_title.text(),
            'y_title': self.y_axis_title.text(),
            'z_title': self.z_axis_title.text(),
            'range_slider': {'visible': self.range_slider_combo.isChecked(),
                             'borderwidth': 1},
            'bar_mode': self.bar_mode_combo.currentData(),
            'x_type': self.x_axis_mode_combo.currentData(),
            'y_type': self.y_axis_mode_combo.currentData(),
            'x_inv': None if not self.invert_x_check.isChecked() else 'reversed',
            'y_inv': None if not self.invert_y_check.isChecked() else 'reversed',
            'x_min': self.x_axis_min.value() if self.x_axis_bounds_check.isChecked() else None,
            'x_max': self.x_axis_max.value() if self.x_axis_bounds_check.isChecked() else None,
            'y_min': self.y_axis_min.value() if self.y_axis_bounds_check.isChecked() else None,
            'y_max': self.y_axis_max.value() if self.y_axis_bounds_check.isChecked() else None,
            'bargaps': self.bar_gap.value(),
            'additional_info_expression': self.additional_info_combo.expression(),
            'bins_check': self.bins_check.isChecked(),
            'gridcolor': self.layout_grid_axis_color.color().name()}
        settings = PlotSettings(plot_type=self.ptype, properties=plot_properties, layout=layout_properties,
                                source_layer_id=self.layer_combo.currentLayer().id(
                                ) if self.layer_combo.currentLayer() else None,
                                dock_title=self.dock_title,
                                dock_id=self.dock_id)
        settings.data_defined_properties = self.data_defined_properties
        return settings

    def set_layer_id(self, layer_id: str):
        """
        Sets the layer to use for plotting, by layer ID
        """
        layer = QgsProject.instance().mapLayer(layer_id)
        if not layer:
            return

        self.layer_combo.setLayer(layer)

    def set_settings(self, settings: PlotSettings):  # pylint: disable=too-many-statements
        """
        Takes a PlotSettings object and fill the widgets with the settings
        """

        self.set_plot_type(settings.plot_type)

        # Set the plot properties
        self.set_layer_id(settings.source_layer_id)
        self.selected_feature_check.setChecked(
            settings.properties.get('selected_features_only', False))
        self.visible_feature_check.setChecked(
            settings.properties.get('visible_features_only', False))

        self.data_defined_properties = settings.data_defined_properties
        buttons = self.findChildren(QgsPropertyOverrideButton)
        for button in buttons:
            self.update_data_defined_button(button)

        # trigger methods depending on data defined button properties
        self.data_defined_color_updated()

        self.filter_by_map_check.setChecked(
            settings.properties.get('layout_filter_by_map', False))
        self.filter_by_atlas_check.setChecked(
            settings.properties.get('layout_filter_by_atlas', False))
        self.x_combo.setExpression(settings.properties.get('x_name', ''))
        self.y_combo.setExpression(settings.properties.get('y_name', ''))
        self.z_combo.setExpression(settings.properties.get('z_name', ''))
        self.in_color_combo.setColor(
            QColor(settings.properties.get('in_color', '#8ebad9')))
        self.marker_size.setValue(settings.properties.get('marker_size', 10))

        self.color_scale_data_defined_in.setCurrentIndex(
            self.color_scale_data_defined_in.findData(settings.properties.get('color_scale', None)))
        self.color_scale_data_defined_in_check.setChecked(
            settings.properties.get('color_scale_data_defined_in_check', False))
        self.color_scale_data_defined_in_invert_check.setChecked(
            settings.properties.get('color_scale_data_defined_in_invert_check', False))
        self.out_color_combo.setColor(
            QColor(settings.properties.get('out_color', '#1f77b4')))
        self.marker_width.setValue(settings.properties.get('marker_width', 1))
        self.marker_type_combo.setCurrentText(
            settings.properties.get('marker_type_combo', 'Points'))
        self.point_combo.setCurrentText(
            settings.properties.get('point_combo', ''))
        self.line_combo.setCurrentText(
            settings.properties.get('line_combo', 'Solid Line'))
        self.contour_type_combo.setCurrentText(
            settings.properties.get('contour_type_combo', 'Fill'))
        self.show_lines_check.setChecked(
            settings.properties.get('show_lines_check', False))
        self.color_scale_combo.setCurrentIndex(self.color_scale_combo.findData(
            settings.properties.get('color_scale', None)))
        self.opacity_widget.setOpacity(settings.properties.get('opacity', 1))
        self.orientation_legend_check.setChecked(
            settings.layout.get('legend_orientation') == 'h')
        self.range_slider_combo.setChecked(
            settings.layout['range_slider']['visible'])
        self.plot_title_line.setText(
            settings.layout.get('title', 'Plot Title'))
        self.legend_title.setText(settings.properties.get('name', ''))
        self.font_title_style.setCurrentFont(
            QFont(settings.layout.get('font_title_family', "Arial"),
                  settings.layout.get('font_title_size', 10)))
        self.font_title_color.setColor(
            QColor(settings.layout.get('font_title_color', "#000000")))
        self.font_xticks_style.setCurrentFont(
            QFont(settings.layout.get('font_xticks_family', "Arial"),
                  settings.layout.get('font_xticks_size', 10)))
        self.font_xticks_color.setColor(
            QColor(settings.layout.get('font_xticks_color', "#000000")))
        self.font_xlabel_style.setCurrentFont(
            QFont(settings.layout.get('font_xlabel_family', "Arial"),
                  settings.layout.get('font_xlabel_size', 10)))
        self.font_xlabel_color.setColor(
            QColor(settings.layout.get('font_xlabel_color', "#000000")))
        self.font_yticks_style.setCurrentFont(
            QFont(settings.layout.get('font_yticks_family', "Arial"),
                  settings.layout.get('font_yticks_size', 10)))
        self.font_yticks_color.setColor(
            QColor(settings.layout.get('font_yticks_color', "#000000")))
        self.font_ylabel_style.setCurrentFont(
            QFont(settings.layout.get('font_ylabel_family', "Arial"),
                  settings.layout.get('font_ylabel_size', 10)))
        self.font_ylabel_color.setColor(
            QColor(settings.layout.get('font_ylabel_color', "#000000")))
        self.x_axis_title.setText(settings.layout.get('x_title', ''))
        self.y_axis_title.setText(settings.layout.get('y_title', ''))
        self.z_axis_title.setText(settings.layout.get('z_title', ''))
        self.info_combo.setCurrentIndex(self.info_combo.findData(
            settings.properties.get('hover_text', None)))
        self.additional_info_combo.setExpression(
            settings.layout.get('additional_info_expression', ''))
        self.hover_as_text_check.setChecked(
            settings.properties.get('hover_label_text') == '+text')
        self.combo_text_position.setCurrentIndex(
            self.combo_text_position.findData(settings.layout.get('hover_label_position', 'auto')))
        self.invert_x_check.setChecked(
            settings.layout.get('x_inv') == 'reversed')
        self.x_axis_mode_combo.setCurrentIndex(
            self.x_axis_mode_combo.findData(settings.layout.get('x_type', None)))
        self.invert_y_check.setChecked(
            settings.layout.get('y_inv') == 'reversed')
        self.y_axis_mode_combo.setCurrentIndex(
            self.y_axis_mode_combo.findData(settings.layout.get('y_type', None)))
        self.x_axis_bounds_check.setChecked(
            settings.layout.get('x_min', None) is not None)
        self.x_axis_bounds_check.setCollapsed(
            settings.layout.get('x_min', None) is None)
        self.x_axis_min.setValue(settings.layout.get(
            'x_min') if settings.layout.get('x_min', None) is not None else 0.0)
        self.x_axis_max.setValue(settings.layout.get(
            'x_max') if settings.layout.get('x_max', None) is not None else 0.0)
        self.y_axis_bounds_check.setChecked(
            settings.layout.get('y_min', None) is not None)
        self.y_axis_bounds_check.setCollapsed(
            settings.layout.get('y_min', None) is None)
        self.y_axis_min.setValue(settings.layout.get(
            'y_min') if settings.layout.get('y_min', None) is not None else 0.0)
        self.y_axis_max.setValue(settings.layout.get(
            'y_max') if settings.layout.get('y_max', None) is not None else 0.0)
        self.orientation_combo.setCurrentIndex(self.orientation_combo.findData(
            settings.properties.get('box_orientation', 'v')))
        self.bar_mode_combo.setCurrentIndex(
            self.bar_mode_combo.findData(settings.layout.get('bar_mode', None)))
        self.hist_norm_combo.setCurrentIndex(self.hist_norm_combo.findData(
            settings.properties.get('normalization', None)))
        self.box_statistic_combo.setCurrentIndex(
            self.box_statistic_combo.findData(settings.properties.get('box_stat', None)))
        self.outliers_combo.setCurrentIndex(self.outliers_combo.findData(
            settings.properties.get('box_outliers', None)))
        self.violinSideCombo.setCurrentIndex(self.violinSideCombo.findData(
            settings.properties.get('violin_side', None)))
        self.violinBox.setChecked(settings.properties.get('violin_box', False))
        self.showMeanCheck.setChecked(
            settings.properties.get('show_mean_line', False))
        self.cumulative_hist_check.setChecked(
            settings.properties.get('cumulative', False))
        self.invert_hist_check.setChecked(
            settings.properties.get('invert_hist') == 'decreasing')
        self.bins_check.setChecked(settings.layout.get('bins_check', False))
        self.bins_value.setValue(settings.properties.get('bins', 0))
        self.bar_gap.setValue(settings.layout.get('bargaps', 0))
        self.show_legend_check.setChecked(settings.layout.get('legend', True))
        self.layout_grid_axis_color.setColor(
            QColor(settings.layout.get('gridcolor') or '#bdbfc0'))
        self.pie_hole.setValue(settings.properties.get('pie_hole', 0))
        if settings.properties.get('y_fields_combo'):
            for name in settings.properties.get('y_fields_combo', '').split(", "):
                self.y_fields_combo.setItemCheckState(self.y_fields_combo.findText(name), Qt.CheckState.Checked)
        self.line_combo_threshold.setCurrentText(
            settings.properties.get('line_combo_threshold', 'Dash Line')
        )
        self.y_combo_radar_label.setExpression(settings.properties.get('y_combo_radar_label', ''))
        self.threshold.setChecked(settings.properties.get('threshold', True))
        self.threshold_value.setValue(settings.properties.get('threshold_value', 1))     
        self.fill.setChecked(settings.properties.get('fill', False))

    def create_plot_factory(self) -> PlotFactory:
        """
        Creates a PlotFactory based on the settings defined in the dialog
        """
        settings = self.get_settings()
        visible_region = None
        if settings.properties['visible_features_only']:
            visible_region = QgsReferencedRectangle(self.iface.mapCanvas().extent(),
                                                    self.iface.mapCanvas().mapSettings().destinationCrs())

        # plot instance
        plot_factory = PlotFactory(settings, visible_region=visible_region)
        # unique name for each plot trace (name is idx_plot, e.g. 1_scatter)
        self.pid = f'{self.idx}_{settings.plot_type}'

        # create default dictionary that contains all the plot and properties
        self.plot_factories[self.pid] = plot_factory

        plot_factory.plot_built.connect(
            partial(self.refresh_plot, plot_factory))

        # just add 1 to the index
        self.idx += 1

        # enable the Update Plot button
        self.update_btn.setEnabled(True)

        return plot_factory

    def update_plot_visible_rect(self):
        """
        Called when the canvas rect changes, and we may need to update filtered plots
        """
        region = QgsReferencedRectangle(self.iface.mapCanvas().extent(),
                                        self.iface.mapCanvas().mapSettings().destinationCrs())
        for _, factory in self.plot_factories.items():
            factory.set_visible_region(region)

    def refresh_plot(self, factory):
        """
        Refreshes the plot built by the specified factory
        """
        self.plot_path = factory.build_figure()
        self.refreshPlotView()

    def create_plot(self):
        """
        call the method to effectively draw the final plot

        before creating the plot, it calls the method plotProperties in order
        to create the plot instance with all the properties taken from the UI
        """

        # call the method to build all the Plot plotProperties
        plot_factory = self.create_plot_factory()

        # set the correct index page of the widget
        self.stackedPlotWidget.setCurrentIndex(1)
        # highlight the correct plot row in the listwidget
        self.listWidget.setCurrentRow(2)

        if self.subcombo.currentData() == 'single':

            # plot single plot, check the object dictionary length
            if len(self.plot_factories) <= 1 or self.ptype == 'radar':
                self.plot_path = plot_factory.build_figure()

            # to plot many plots in the same figure
            else:
                # plot list ready to be called within go.Figure
                pl = []
                for _, v in self.plot_factories.items():
                    pl.append(v.trace[0])
                self.plot_path = plot_factory.build_figures(self.ptype, pl)

        # choice to draw subplots instead depending on the combobox
        elif self.subcombo.currentData() == 'subplots':
            try:
                gr = len(self.plot_factories)
                pl = []

                for _, v in self.plot_factories.items():
                    pl.append(v.trace[0])

                # plot in single row and many columns
                if self.radio_rows.isChecked():

                    self.plot_path = plot_factory.build_sub_plots(
                        'row', 1, gr, pl)

                # plot in single column and many rows
                elif self.radio_columns.isChecked():

                    self.plot_path = plot_factory.build_sub_plots(
                        'col', gr, 1, pl)
            except:  # pylint: disable=bare-except  # noqa: F401
                if self.message_bar:
                    self.message_bar.pushMessage(
                        self.tr("{} plot is not compatible for subplotting\n see ").format(self.ptype),
                        Qgis.MessageLevel(2), duration=5)
                return

        # connect to a simple function that reloads the view
        self.refreshPlotView()

    def UpdatePlot(self):
        """
        updates only the LAST plot created
        get the key of the last plot created and delete it from the plot container
        and call the method to create the plot with the updated settings
        """
        if self.mode == DataPlotlyPanelWidget.MODE_CANVAS:
            plot_to_update = sorted(self.plot_factories.keys())[-1]
            del self.plot_factories[plot_to_update]

            self.create_plot()
        else:
            self.widgetChanged.emit()

    def refreshPlotView(self):
        """
        just refresh the view, if the reload method is called immediately after
        the view creation it won't reload the page
        """

        self.plot_url = QUrl.fromLocalFile(self.plot_path)
        self.plot_view.load(self.plot_url)
        self.layoutw.addWidget(self.plot_view)

        self.raw_plot_text.clear()
        with open(self.plot_path, encoding="utf8") as myfile:
            plot_text = myfile.read()

        self.raw_plot_text.setPlainText(plot_text)

    def clearPlotView(self):
        """
        clear the content of the QWebView by loading an empty url and clear the
        raw text of the QPlainTextEdit
        """

        self.plot_factories = {}

        try:
            self.plot_view.load(QUrl(''))
            self.layoutw.addWidget(self.plot_view)
            self.raw_plot_text.clear()
            if self.mode == DataPlotlyPanelWidget.MODE_CANVAS:
                # disable the Update Plot Button
                self.update_btn.setEnabled(False)
        except:  # pylint: disable=bare-except  # noqa: F401
            pass

    def save_plot_as_image(self):
        """
        Save the current plot view as a png image.
        The user can choose the path and the file name
        """
        plot_file, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Plot"), "", "*.png")
        if not plot_file:
            return

        plot_file = QgsFileUtils.ensureFileNameHasExtension(plot_file, ['png'])

        frame = self.plot_view.page().mainFrame()
        self.plot_view.page().setViewportSize(frame.contentsSize())
        # render image
        image = QImage(self.plot_view.page().viewportSize(),
                       QImage.Format_ARGB32)
        painter = QPainter(image)
        frame.render(painter)
        painter.end()
        image.save(plot_file)
        if self.message_bar:
            self.message_bar.pushSuccess(self.tr('DataPlotly'),
                                         self.tr('Plot saved to <a href="{}">{}</a>').format(
                                             QUrl.fromLocalFile(
                                                 plot_file).toString(),
                                             QDir.toNativeSeparators(plot_file)))

    def save_plot_as_html(self):
        """
        Saves the plot as a local html file. Basically just let the user choose
        where to save the already existing html file created by plotly
        """

        plot_file, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Plot"), "", "*.html")
        if not plot_file:
            return

        plot_file = QgsFileUtils.ensureFileNameHasExtension(plot_file, [
                                                            'html'])

        copyfile(self.plot_path, plot_file)
        if self.message_bar:
            self.message_bar.pushSuccess(self.tr('DataPlotly'),
                                         self.tr('Saved plot to <a href="{}">{}</a>').format(
                                             QUrl.fromLocalFile(
                                                 plot_file).toString(),
                                             QDir.toNativeSeparators(plot_file)))

    def showPlotFromDic(self, plot_input_dic):
        """
        Allows to call the plugin from the python console

        param:
            plot_input_dic (dictionary): dictionary with specific structure,
            see below


        Code usage example:

        #import the plugins of QGIS
        from qgis.utils import plugins
        # create the instace of the plugin
        myplugin = plugins['DataPlotly']

        # create a dictionary of values that will be elaborated by the method

        vl = iface.activeLayer()
        # empty dictionary that should filled up with GUI values
        dq = {}
        dq['plot_prop'] = {}
        dq['layout_prop'] = {}
        # plot type
        dq['plot_type'] = 'scatter'
        # vector layer
        dq["layer"] = vl
        # minimum X and Y axis values
        dq['plot_prop']['x'] = [i["some_field"] for i in vl.getFeatures()]
        dq['plot_prop']['y'] = [i["some_field"] for i in vl.getFeatures()]

        # call the final method
        myplugin.loadPlotFromDic(dq)
        """
        # keys of the nested plot_prop and layout_prop have to be the SAME of
        # those created in buildProperties and buildLayout method

        # set some dialog widget from the input dictionary
        # plot type in the plot_combo combobox
        self.plot_combo.setCurrentIndex(
            self.plot_combo.findData(plot_input_dic["plot_type"]))
        try:
            self.layer_combo.setLayer(plot_input_dic["layer"])
            if 'x_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["x_name"]:
                self.x_combo.setField(plot_input_dic["plot_prop"]["x_name"])
            if 'y_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["y_name"]:
                self.y_combo.setField(plot_input_dic["plot_prop"]["y_name"])
            if 'z_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["z_name"]:
                self.z_combo.setField(plot_input_dic["plot_prop"]["z_name"])
            if 'y_radar_label' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["y_radar_label"]:
                self.y_combo_radar_label.setField(plot_input_dic["plot_prop"]["y_radar_label"])
            if 'y_radar_fields' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["y_radar_fields"]:
                for name in plot_input_dic["plot_prop"]["y_radar_fields"]:
                    self.y_fields_combo.setItemCheckState(self.y_fields_combo.findText(name), Qt.CheckState.Checked)
        except:  # pylint: disable=bare-except  # noqa: F401
            pass

        settings = PlotSettings(plot_input_dic['plot_type'],
                                properties=plot_input_dic["plot_prop"],
                                layout=plot_input_dic["layout_prop"])
        # create Plot instance
        factory = PlotFactory(settings)

        standalone_plot_path = factory.build_figure()
        standalone_plot_url = QUrl.fromLocalFile(standalone_plot_path)

        self.plot_view.load(standalone_plot_url)
        self.layoutw.addWidget(self.plot_view)

        # enable the Update Button to allow the updating of the plot
        self.update_btn.setEnabled(True)

        # the following code is necessary to let the user add other plots in
        # different plot canvas after the creation of the standolone plot

        # unique name for each plot trace (name is idx_plot, e.g. 1_scatter)
        self.pid = ('{}_{}'.format(str(self.idx), plot_input_dic["plot_type"]))

        # create default dictionary that contains all the plot and properties
        self.plot_factories[self.pid] = factory

        # just add 1 to the index
        self.idx += 1

    def write_project(self, document: QDomDocument):
        """
        Called when the current project is being saved.

        If the dialog opts to store its current settings in the project, it will
        use this hook to store them in the project XML
        """
        if not self.save_to_project:
            return

        settings = self.get_settings()
        settings.write_to_project(document)

    def read_project(self, document: QDomDocument):
        """
        Called when the current project is being read.

        If the dialog opts to read its current settings from a project, it will
        use this hook to read them from the project XML
        """
        if not self.read_from_project:
            return

        settings = PlotSettings(
            dock_title=self.dock_title, dock_id=self.dock_id)
        if settings.read_from_project(document):
            # update the dock state to match the read settings
            self.set_settings(settings)
            self.create_plot()

    def load_configuration(self):
        """
        Loads configuration settings from a file
        """
        file, _ = QFileDialog.getOpenFileName(self, self.tr(
            "Load Configuration"), "", "XML files (*.xml)")
        if file:
            settings = PlotSettings()
            if settings.read_from_file(file):
                self.set_settings(settings)
            else:
                if self.message_bar:
                    self.message_bar.pushWarning(self.tr('DataPlotly'), self.tr(
                        'Could not read settings from file'))

    def save_configuration(self):
        """
        Saves configuration settings to a file
        """
        file, _ = QFileDialog.getSaveFileName(self, self.tr(
            "Save Configuration"), "", "XML files (*.xml)")
        if file:
            file = QgsFileUtils.ensureFileNameHasExtension(file, ['xml'])
            self.get_settings().write_to_file(file)
            if self.message_bar:
                self.message_bar.pushSuccess(self.tr('DataPlotly'),
                                             self.tr('Saved configuration to <a href="{}">{}</a>').format(
                                                 QUrl.fromLocalFile(file).toString(), QDir.toNativeSeparators(file)))
