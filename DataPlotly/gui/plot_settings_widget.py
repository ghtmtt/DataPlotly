# -*- coding: utf-8 -*-
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

import os
import json
from collections import OrderedDict
from shutil import copyfile

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QListWidgetItem,
    QVBoxLayout,
    QFileDialog
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
    QSettings,
    pyqtSignal
)
from qgis.PyQt.QtWebKit import QWebSettings
from qgis.PyQt.QtWebKitWidgets import (
    QWebView
)

from qgis.core import (
    Qgis,
    QgsNetworkAccessManager,
    QgsVectorLayerUtils,
    QgsFeatureRequest,
    QgsMapLayerProxyModel,
    QgsProject,
    QgsSymbolLayerUtils,
    QgsProperty
)
from qgis.gui import QgsPanelWidget
from qgis.utils import iface

from DataPlotly.utils import (
    hex_to_rgb
)
from DataPlotly.core.plot_factory import PlotFactory
from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.gui.gui_utils import GuiUtils

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('dataplotly_dockwidget_base.ui'))


class DataPlotlyPanelWidget(QgsPanelWidget, WIDGET):  # pylint: disable=too-many-lines,too-many-instance-attributes,too-many-public-methods
    """
    Main configuration panel widget for plot settings
    """

    MODE_CANVAS = 'CANVAS'
    MODE_LAYOUT = 'LAYOUT'

    # emit signal when dialog is resized
    resizeWindow = pyqtSignal()

    def __init__(self, mode=MODE_CANVAS, parent=None, override_iface=None):  # pylint: disable=too-many-statements
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        if override_iface is None:
            self.iface = iface
        else:
            self.iface = override_iface

        self.mode = mode

        self.setPanelTitle(self.tr('Plot Properties'))

        self.save_to_project = True
        self.read_from_project = True

        # listen out for project save/restore, and update our state accordingly
        QgsProject.instance().writeProject.connect(self.write_project)
        QgsProject.instance().readProject.connect(self.read_project)

        self.listWidget.setIconSize(self.iface.iconSize(False))
        self.listWidget.setMaximumWidth(int(self.listWidget.iconSize().width() * 1.18))

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

        # set the icon of QgspropertyOverrideButton not taken automatically
        self.size_defined_button.setIcon(GuiUtils.get_icon('mIconDataDefineExpression.svg'))
        self.in_color_defined_button.setIcon(GuiUtils.get_icon('mIconDataDefineExpression.svg'))

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

        # Populate PlotTypes combobox
        # we sort available types by translated name
        type_classes = [clazz for _, clazz in PlotFactory.PLOT_TYPES.items()]
        type_classes.sort(key=lambda x: x.name().lower())
        for clazz in type_classes:
            self.plot_combo.addItem(clazz.icon(), clazz.name(), clazz.type_name())

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
        self.marker_type_combo.currentIndexChanged.connect(self.refreshWidgets3)

        self.mGroupBox_2.collapsedStateChanged.connect(self.refreshWidgets)

        # fill the layer combobox with vector layers
        self.layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)

        self.setCheckState()
        try:
            self.layer_combo.currentIndexChanged.connect(self.refreshLayerSelected)
        except:  # pylint: disable=bare-except  # noqa: F401
            pass

        # fill combo boxes when launching the UI
        self.x_combo.setLayer(self.layer_combo.currentLayer())
        self.y_combo.setLayer(self.layer_combo.currentLayer())
        self.z_combo.setLayer(self.layer_combo.currentLayer())
        self.additional_info_combo.setLayer(self.layer_combo.currentLayer())

        # connect the combo boxes to the setLegend function
        self.x_combo.fieldChanged.connect(self.setLegend)
        self.y_combo.fieldChanged.connect(self.setLegend)
        self.z_combo.fieldChanged.connect(self.setLegend)

        self.draw_btn.clicked.connect(self.createPlot)
        self.update_btn.clicked.connect(self.UpdatePlot)
        self.clear_btn.clicked.connect(self.clearPlotView)
        self.save_plot_btn.clicked.connect(self.savePlotAsImage)
        self.save_plot_html_btn.clicked.connect(self.savePlotAsHtml)
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
        self.plot_view.page().setNetworkAccessManager(QgsNetworkAccessManager.instance())
        self.plot_view.statusBarMessage.connect(self.getJSmessage)
        plot_view_settings = self.plot_view.settings()
        plot_view_settings.setAttribute(QWebSettings.WebGLEnabled, True)
        plot_view_settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        plot_view_settings.setAttribute(QWebSettings.Accelerated2dCanvasEnabled, True)
        self.layoutw.addWidget(self.plot_view)

        # get the plot type from the combobox
        self.ptype = self.plot_combo.currentData()

        # load the layer fields in the init function for the datadefined buttons
        self.refreshDataDefinedButtonLayer()
        # connect the size defined button to the correct functions
        self.size_defined_button.changed.connect(self.refreshSizeDefined)
        # connect the color defined button to the correct function
        self.in_color_defined_button.changed.connect(self.resfreshColorDefined)

        # connect to refreshing function of listWidget and stackedWidgets
        self.listWidget.currentRowChanged.connect(self.updateStacked)

        # connect the plot changing to the color data defined buttons
        self.plot_combo.currentIndexChanged.connect(self.resfreshColorDefined)

        # better default colors
        self.in_color_combo.setColor(QColor('#8EBAD9'))
        self.out_color_combo.setColor(QColor('#1F77B4'))

        self.marker_size_value = None
        self.in_color = None
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

    def set_plot_type(self, plot_type: str):
        """
        Sets the current plot type shown in the dialog
        """
        self.plot_combo.setCurrentIndex(self.plot_combo.findData(plot_type))

    def refreshSizeDefined(self):
        """
        enable/disable the correct buttons depending on the choice
        """
        if self.size_defined_button.isActive():
            self.marker_size.setEnabled(False)
        else:
            self.marker_size.setEnabled(True)

    def resfreshColorDefined(self):
        """
        refreshing function for color data defined button

        checks is the datadefined button is active and check also the plot type
        in order to deactivate the color when not needed
        """
        # if data defined button is active
        if self.in_color_defined_button.isActive():
            # if plot is scatter or bar
            if self.ptype == 'scatter' or self.ptype == 'bar' or self.ptype == 'ternary':
                self.in_color_combo.setEnabled(False)
                self.color_scale_data_defined_in.setVisible(True)
                self.color_scale_data_defined_in.setEnabled(True)
                self.color_scale_data_defined_in_label.setVisible(True)
                self.color_scale_data_defined_in_label.setEnabled(True)
                self.color_scale_data_defined_in_check.setVisible(True)
                self.color_scale_data_defined_in_check.setEnabled(True)
                self.color_scale_data_defined_in_invert_check.setVisible(True)
                self.color_scale_data_defined_in_invert_check.setEnabled(True)
            # if plot is not scatter or bar
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

    def getMarkerSize(self):
        """
        get the marker size
        """

        if self.size_defined_button.isActive() and self.layer_combo.currentLayer():
            mark_size = self.size_defined_button.toProperty().expressionString()
            self.marker_size_value = QgsVectorLayerUtils.getValues(self.layer_combo.currentLayer(), mark_size,
                                                                   selectedOnly=self.selected_feature_check.isChecked())[
                0]
        else:
            # self.marker_size.setEnabled(True)
            self.marker_size_value = self.marker_size.value()

    def getColorDefined(self):
        """
        get the color code for plotly from the dataDefined button
        """

        if self.in_color_defined_button.isActive() and self.layer_combo.currentLayer():
            if self.ptype == 'scatter' or self.ptype == 'bar' or self.ptype == 'ternary':
                in_color = self.in_color_defined_button.toProperty().expressionString()
                self.in_color = QgsVectorLayerUtils.getValues(self.layer_combo.currentLayer(), in_color,
                                                              selectedOnly=self.selected_feature_check.isChecked())[0]
            else:
                self.in_color = hex_to_rgb(self.in_color_combo)
        else:
            self.in_color = hex_to_rgb(self.in_color_combo)

    def refreshLayerSelected(self):
        """
        Trigger actions after selected layer changes
        """
        self.refreshDataDefinedButtonLayer()
        self.setCheckState()

    def refreshDataDefinedButtonLayer(self):
        """
        load the layer fields for the data-defined buttons
        """
        self.size_defined_button.setVectorLayer(self.layer_combo.currentLayer())
        self.in_color_defined_button.setVectorLayer(self.layer_combo.currentLayer())

    def setCheckState(self):
        """
        change the selected_feature_check checkbox accordingly with the current
        layer selection state
        """
        try:
            if self.layer_combo.currentLayer().selectedFeatures():
                self.selected_feature_check.setEnabled(True)
            else:
                self.selected_feature_check.setEnabled(False)
                self.selected_feature_check.setChecked(False)
        except:  # pylint: disable=bare-except  # noqa: F401
            pass

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
                    exp = """ "{}" = '{}' """.format(dic['field'], dic['label'])
                    # set the iterator with the expression as filter in feature request
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds([f.id() for f in it])
                elif dic["type"] == 'histogram':
                    vmin = dic['id'] - dic['bin_step'] / 2
                    vmax = dic['id'] + dic['bin_step'] / 2
                    exp = """ "{}" <= {} AND "{}" > {} """.format(dic['field'], vmax, dic['field'], vmin)
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds([f.id() for f in it])
                elif dic["type"] == 'scatterternary':
                    self.layer_combo.currentLayer().selectByIds([dic['fid']])
                else:
                    # build the expression from the js dic (customdata)
                    exp = """ "{}" = '{}' """.format(dic['field'], dic['id'])
                    # set the iterator with the expression as filter in feature request
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds([f.id() for f in it])
                    # print(exp)
        except:  # pylint: disable=bare-except # noqa: F401
            pass

    def helpPage(self):
        """
        change the page of the manual according to the plot type selected and
        the language (looks for translations)
        """

        locale = QSettings().value('locale/userLocale', 'en_US')[0:2]

        self.help_view.load(QUrl(''))
        self.layouth.addWidget(self.help_view)
        help_link = os.path.join(os.path.dirname(__file__), 'help/build/html/{}/{}.html'.format(locale, self.ptype))
        # check if the file exists, else open the default home page
        if not os.path.exists(help_link):
            help_link = os.path.join(os.path.dirname(__file__), 'help/build/html/en/{}.html'.format(self.ptype))

        help_url = QUrl.fromLocalFile(help_link)
        self.help_view.load(help_url)

    def resizeEvent(self, event):
        """
        reimplemented event to detect the dialog resizing
        """
        self.resizeWindow.emit()
        return super(DataPlotlyPanelWidget, self).resizeEvent(event)

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
        self.outliers_combo.addItem(self.tr('Suspected Outliers'), 'suspectedoutliers')
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
        for k, v in self.line_types.items():
            self.line_combo.addItem(k, v)

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
        self.hist_norm_combo.addItem(self.tr('Prob Density'), 'probability density')

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
                            'RedOrangeYellow': 'YIOrRd',
                            'DeepblueBlueWhite': 'YIGnBu',
                            'BlueWhitePurple': 'Picnic'}

        self.color_scale_combo.clear()
        self.color_scale_data_defined_in.clear()

        for k, v in scale_color_dict.items():
            self.color_scale_combo.addItem(k, v)
            self.color_scale_data_defined_in.addItem(k, v)

        # according to the plot type, change the label names

        # BoxPlot
        if self.ptype == 'box' or self.ptype == 'violin':
            self.x_label.setText(self.tr('Grouping Field \n(Optional)'))
            # set the horizontal and vertical size of the label and reduce the label font size
            ff = QFont()
            ff.setPointSizeF(8)
            self.x_label.setFont(ff)
            self.x_label.setFixedWidth(100)
            self.orientation_label.setText(self.tr('Box Orientation'))
            self.in_color_lab.setText(self.tr('Box Color'))

        # ScatterPlot
        if self.ptype == 'scatter' or 'ternary':
            self.in_color_lab.setText(self.tr('Marker Color'))

        # BarPlot
        if self.ptype == 'bar':
            self.orientation_label.setText(self.tr('Bar Orientation'))
            self.in_color_lab.setText(self.tr('Bar Color'))

        # PiePlot
        if self.ptype == 'pie':
            self.x_label.setText(self.tr('Grouping Field'))
            ff = QFont()
            ff.setPointSizeF(8.5)
            self.x_label.setFont(ff)
            self.x_label.setFixedWidth(80)

        # info combo for data hovering
        self.info_combo.clear()
        self.info_combo.addItem(self.tr('All Values'), 'all')
        self.info_combo.addItem(self.tr('X Values'), 'x')
        self.info_combo.addItem(self.tr('Y Values'), 'y')
        self.info_combo.addItem(self.tr('No Data'), 'none')

        # Violin side
        self.violinSideCombo.clear()
        self.violinSideCombo.addItem(self.tr('Both Sides'), 'both')
        self.violinSideCombo.addItem(self.tr('Only Left'), 'negative')
        self.violinSideCombo.addItem(self.tr('Only right'), 'positive')

        # dictionary with all the widgets and the plot they belong to
        self.widgetType = {
            # plot properties
            self.layer_combo: ['all'],
            self.x_label: ['all'],
            self.x_combo: ['all'],
            self.y_label: ['scatter', 'bar', 'box', 'pie', '2dhistogram', 'polar', 'ternary', 'contour', 'violin'],
            self.y_combo: ['scatter', 'bar', 'box', 'pie', '2dhistogram', 'polar', 'ternary', 'contour', 'violin'],
            self.z_label: ['ternary'],
            self.z_combo: ['ternary'],
            self.info_label: ['scatter'],
            self.info_combo: ['scatter'],
            self.in_color_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.in_color_combo: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.in_color_defined_button: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in_label: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in_check: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in_invert_check: ['bar', 'ternary'],
            self.out_color_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.out_color_combo: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.marker_width_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.marker_width: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.marker_size_lab: ['scatter', 'polar', 'ternary'],
            self.marker_size: ['scatter', 'polar', 'ternary'],
            self.size_defined_button: ['scatter', 'ternary'],
            self.marker_type_lab: ['scatter', 'polar'],
            self.marker_type_combo: ['scatter', 'polar'],
            self.alpha_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.alpha_slid: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'violin'],
            self.alpha_num: ['scatter', 'bar', 'box', 'histogram', 'ternary', 'violin'],
            self.mGroupBox_2: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'contour', '2dhistogram',
                               'violin'],
            self.bar_mode_lab: ['bar', 'histogram'],
            self.bar_mode_combo: ['bar', 'histogram'],
            self.legend_label: ['all'],
            self.legend_title: ['all'],
            self.point_lab: ['scatter', 'ternary', 'polar'],
            self.point_combo: ['scatter', 'ternary', 'polar'],
            self.line_lab: ['scatter', 'polar'],
            self.line_combo: ['scatter', 'polar'],
            self.color_scale_label: ['contour', '2dhistogram'],
            self.color_scale_combo: ['contour', '2dhistogram'],
            self.contour_type_label: ['contour'],
            self.contour_type_combo: ['contour'],
            self.show_lines_check: ['contour'],

            # layout customization
            self.show_legend_check: ['all'],
            self.orientation_legend_check: ['scatter', 'bar', 'box', 'histogram', 'ternary', 'pie', 'violin'],
            self.plot_title_lab: ['all'],
            self.plot_title_line: ['all'],
            self.x_axis_label: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary', 'violin'],
            self.x_axis_title: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary', 'violin'],
            self.y_axis_label: ['scatter', 'bar', 'box', '2dhistogram', 'ternary', 'violin'],
            self.y_axis_title: ['scatter', 'bar', 'box', '2dhistogram', 'ternary', 'violin'],
            self.z_axis_label: ['ternary'],
            self.z_axis_title: ['ternary'],
            self.x_axis_mode_label: ['scatter', 'box'],
            self.y_axis_mode_label: ['scatter', 'box'],
            self.x_axis_mode_combo: ['scatter', 'box'],
            self.y_axis_mode_combo: ['scatter', 'box'],
            self.invert_x_check: ['scatter', 'bar', 'box', 'histogram', '2dhistogram'],
            self.invert_y_check: ['scatter', 'bar', 'box', 'histogram', '2dhistogram'],
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
            self.additional_info_label: ['scatter', 'ternary'],
            self.additional_info_combo: ['scatter', 'ternary'],
            self.cumulative_hist_check: ['histogram'],
            self.invert_hist_check: ['histogram'],
            self.bins_check: ['histogram'],
            self.bins_value: ['histogram'],
            self.bar_gap_label: ['histogram'],
            self.bar_gap: ['histogram'],
            self.violinSideLabel: ['violin'],
            self.violinSideCombo: ['violin'],
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
            legend_title_string = ('{} - {}'.format(self.x_combo.currentText(), self.y_combo.currentText()))
            self.legend_title.setText(legend_title_string)

    def get_settings(self) -> PlotSettings:  # pylint: disable=R0915
        """
        Returns the plot settings as currently defined in the dialog
        """
        # call the method to get the correct marker size
        self.getMarkerSize()
        self.getColorDefined()

        # get the plot type from the combo box
        self.ptype = self.plot_combo.currentData()

        # if colorscale should be visible or not
        color_scale_visible = self.color_scale_data_defined_in_check.isVisible() and self.color_scale_data_defined_in_check.isChecked()

        # dictionary of all the plot properties
        plot_properties = {'custom': [self.x_combo.currentText()],
                           'hover_text': self.info_combo.currentData(),
                           'x_name': self.x_combo.currentText(),
                           'y_name': self.y_combo.currentText(),
                           'z_name': self.z_combo.currentText(),
                           'in_color': self.in_color,
                           'show_colorscale_legend': color_scale_visible,
                           'invert_color_scale': self.color_scale_data_defined_in_invert_check.isChecked(),
                           'out_color': hex_to_rgb(self.out_color_combo),
                           'marker_width': self.marker_width.value(),
                           'marker_size': self.marker_size_value,
                           'marker_symbol': self.point_types2[self.point_combo.currentData()],
                           'line_dash': self.line_types2[self.line_combo.currentText()],
                           'box_orientation': self.orientation_combo.currentData(),
                           'marker': self.marker_types[self.marker_type_combo.currentText()],
                           'opacity': (100 - self.alpha_slid.value()) / 100.0,
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
                           'selected_features_only': self.selected_feature_check.isChecked(),
                           'in_color_value': QgsSymbolLayerUtils.encodeColor(self.in_color_combo.color()),
                           'in_color_property': self.in_color_defined_button.toProperty().toVariant(),
                           'size_property': self.size_defined_button.toProperty().toVariant(),
                           'color_scale_data_defined_in_check': False,
                           'color_scale_data_defined_in_invert_check': False,
                           'out_color_combo': QgsSymbolLayerUtils.encodeColor(self.out_color_combo.color()),
                           'marker_type_combo': self.marker_type_combo.currentText(),
                           'point_combo': self.point_combo.currentText(),
                           'line_combo': self.line_combo.currentText(),
                           'contour_type_combo': self.contour_type_combo.currentText(),
                           'show_lines_check': self.show_lines_check.isChecked(),
                           'alpha': self.alpha_slid.value()}

        if self.in_color_defined_button.isActive():
            plot_properties['color_scale_data_defined_in_check'] = self.color_scale_data_defined_in_check.isChecked()
            plot_properties['color_scale_data_defined_in_invert_check'] = self.color_scale_data_defined_in_invert_check.isChecked()
            if self.ptype in self.widgetType[self.color_scale_data_defined_in]:
                plot_properties['color_scale'] = self.color_scale_data_defined_in.currentData()
            else:
                plot_properties['color_scale'] = self.color_scale_combo.currentData()

        # add widgets properties to the dictionary

        # build the layout customizations
        layout_properties = {'legend': self.show_legend_check.isChecked(),
                             'legend_orientation': 'h' if self.orientation_legend_check.isChecked() else 'v',
                             'title': self.plot_title_line.text(),
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
                             'bargaps': self.bar_gap.value(),
                             'additional_info_expression': self.additional_info_combo.expression(),
                             'bins_check': self.bins_check.isChecked()}

        return PlotSettings(plot_type=self.ptype, properties=plot_properties, layout=layout_properties,
                            source_layer_id=self.layer_combo.currentLayer().id() if self.layer_combo.currentLayer() else None)

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
        self.selected_feature_check.setChecked(settings.properties.get('selected_features_only', False))
        self.x_combo.setExpression(settings.properties['x_name'])
        self.y_combo.setExpression(settings.properties['y_name'])
        self.z_combo.setExpression(settings.properties['z_name'])
        self.in_color_combo.setColor(QgsSymbolLayerUtils.decodeColor(settings.properties['in_color_value']))
        color_prop = QgsProperty()
        color_prop.loadVariant(settings.properties['in_color_property'])
        self.in_color_defined_button.setToProperty(color_prop)
        self.marker_size.setValue(settings.properties['marker_size'])

        size_prop = QgsProperty()
        size_prop.loadVariant(settings.properties['size_property'])
        self.size_defined_button.setToProperty(size_prop)

        self.color_scale_data_defined_in.setCurrentIndex(self.color_scale_data_defined_in.findData(settings.properties['color_scale']))
        self.color_scale_data_defined_in_check.setChecked(settings.properties['color_scale_data_defined_in_check'])
        self.color_scale_data_defined_in_invert_check.setChecked(
            settings.properties['color_scale_data_defined_in_invert_check'])
        self.out_color_combo.setColor(QgsSymbolLayerUtils.decodeColor(settings.properties['out_color_combo']))
        self.marker_width.setValue(settings.properties['marker_width'])
        self.marker_type_combo.setCurrentText(settings.properties['marker_type_combo'])
        self.point_combo.setCurrentText(settings.properties['point_combo'])
        self.line_combo.setCurrentText(settings.properties['line_combo'])
        self.contour_type_combo.setCurrentText(settings.properties['contour_type_combo'])
        self.show_lines_check.setChecked(settings.properties['show_lines_check'])
        self.color_scale_combo.setCurrentIndex(self.color_scale_combo.findData(settings.properties['color_scale']))
        self.alpha_slid.setValue(settings.properties['alpha'])
        self.alpha_num.setValue(settings.properties['alpha'])
        self.orientation_legend_check.setChecked(settings.layout['legend_orientation'] == 'h')
        self.range_slider_combo.setChecked(settings.layout['range_slider']['visible'])
        self.plot_title_line.setText(settings.layout['title'])
        self.legend_title.setText(settings.properties['name'])
        self.x_axis_title.setText(settings.layout['x_title'])
        self.y_axis_title.setText(settings.layout['y_title'])
        self.z_axis_title.setText(settings.layout['z_title'])
        self.info_combo.setCurrentIndex(self.info_combo.findData(settings.properties['hover_text']))
        self.additional_info_combo.setExpression(settings.layout['additional_info_expression'])
        self.invert_x_check.setChecked(settings.layout['x_inv'] == 'reversed')
        self.x_axis_mode_combo.setCurrentIndex(self.x_axis_mode_combo.findData(settings.layout['x_type']))
        self.invert_y_check.setChecked(settings.layout['y_inv'] == 'reversed')
        self.y_axis_mode_combo.setCurrentIndex(self.y_axis_mode_combo.findData(settings.layout['y_type']))
        self.orientation_combo.setCurrentIndex(self.orientation_combo.findData(settings.properties['box_orientation']))
        self.bar_mode_combo.setCurrentIndex(self.bar_mode_combo.findData(settings.layout['bar_mode']))
        self.hist_norm_combo.setCurrentIndex(self.hist_norm_combo.findData(settings.properties['normalization']))
        self.box_statistic_combo.setCurrentIndex(self.box_statistic_combo.findData(settings.properties['box_stat']))
        self.outliers_combo.setCurrentIndex(self.outliers_combo.findData(settings.properties['box_outliers']))
        self.violinSideCombo.setCurrentIndex(self.violinSideCombo.findData(settings.properties['violin_side']))
        self.showMeanCheck.setChecked(settings.properties['show_mean_line'])
        self.cumulative_hist_check.setChecked(settings.properties['cumulative'])
        self.invert_hist_check.setChecked(settings.properties['invert_hist'] == 'decreasing')
        self.bins_check.setChecked(settings.layout['bins_check'])
        self.bins_value.setValue(settings.properties['bins'])
        self.bar_gap.setValue(settings.layout['bargaps'])
        self.show_legend_check.setChecked(settings.layout['legend'])

    def create_plot_factory(self) -> PlotFactory:
        """
        Creates a PlotFactory based on the settings defined in the dialog
        """
        settings = self.get_settings()

        # plot instance
        plot_factory = PlotFactory(settings)

        # unique name for each plot trace (name is idx_plot, e.g. 1_scatter)
        self.pid = ('{}_{}'.format(str(self.idx), settings.plot_type))

        # create default dictionary that contains all the plot and properties
        self.plot_factories[self.pid] = plot_factory

        # just add 1 to the index
        self.idx += 1

        # enable the Update Plot button
        self.update_btn.setEnabled(True)

        return plot_factory

    def createPlot(self):
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
            if len(self.plot_factories) <= 1:
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

                    self.plot_path = plot_factory.build_sub_plots('row', 1, gr, pl)

                # plot in single column and many rows
                elif self.radio_columns.isChecked():

                    self.plot_path = plot_factory.build_sub_plots('col', gr, 1, pl)
            except:  # pylint: disable=bare-except  # noqa: F401
                self.iface.messageBar().pushMessage(
                    self.tr("{} plot is not compatible for subplotting\n see ".format(self.ptype)),
                    Qgis.MessageLevel(2), duration=5)
                return

        # connect to simple function that reloads the view
        self.refreshPlotView()

    def UpdatePlot(self):
        """
        updates only the LAST plot created
        get the key of the last plot created and delete it from the plot container
        and call the method to create the plot with the updated settings
        """
        if self.mode == DataPlotlyPanelWidget.MODE_CANVAS:
            plot_to_update = (sorted(self.plot_factories.keys())[-1])
            del self.plot_factories[plot_to_update]

            self.createPlot()
        else:
            self.widgetChanged.emit()

    def refreshPlotView(self):
        """
        just resfresh the view, if the reload method is called immediatly after
        the view creation it won't reload the page
        """

        self.plot_url = QUrl.fromLocalFile(self.plot_path)
        self.plot_view.load(self.plot_url)
        self.layoutw.addWidget(self.plot_view)

        self.raw_plot_text.clear()
        with open(self.plot_path, 'r') as myfile:
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

    def savePlotAsImage(self):
        """
        save the current plot view as png image.
        The user can choose the path and the file name
        """
        self.plot_file = QFileDialog.getSaveFileName(self, self.tr("Save plot"), "", "*.png")

        self.plot_file = self.plot_file[0]
        if self.plot_file:
            self.plot_file += '.png'

        try:
            frame = self.plot_view.page().mainFrame()
            self.plot_view.page().setViewportSize(frame.contentsSize())
            # render image
            image = QImage(self.plot_view.page().viewportSize(), QImage.Format_ARGB32)
            painter = QPainter(image)
            frame.render(painter)
            painter.end()
            if self.plot_file:
                image.save(self.plot_file)
                self.iface.messageBar().pushMessage(self.tr("Plot succesfully saved"), Qgis.MessageLevel(0), duration=2)
        except:  # pylint: disable=bare-except  # noqa: F401
            self.iface.messageBar().pushMessage(self.tr("Please select a directory to save the plot"),
                                                Qgis.MessageLevel(1),
                                                duration=4)

    def savePlotAsHtml(self, plot_file=None):
        """
        save the plot as html local file. Basically just let the user choose
        where to save the already existing html file created by plotly
        """

        try:
            self.plot_file = QFileDialog.getSaveFileName(self, self.tr("Save plot"), "", "*.html")
            self.plot_file = self.plot_file[0]
        except:  # pylint: disable=bare-except  # noqa: F401
            self.plot_file = plot_file

        if self.plot_file and not self.plot_file.endswith('.html'):
            self.plot_file += '.html'

        if self.plot_file:
            copyfile(self.plot_path, self.plot_file)
            self.iface.messageBar().pushMessage(self.tr("Plot succesfully saved"), Qgis.MessageLevel(0), duration=2)

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
        self.plot_combo.setCurrentIndex(self.plot_combo.findData(plot_input_dic["plot_type"]))

        try:
            self.layer_combo.setLayer(plot_input_dic["layer"])
            if 'x_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["x_name"]:
                self.x_combo.setField(plot_input_dic["plot_prop"]["x_name"])
            if 'y_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["y_name"]:
                self.y_combo.setField(plot_input_dic["plot_prop"]["y_name"])
            if 'z_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["z_name"]:
                self.z_combo.setField(plot_input_dic["plot_prop"]["z_name"])
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

        settings = PlotSettings()
        if settings.read_from_project(document):
            # TODO here we would call a method like self.set_settings, and update the dock
            # state to match the read settings
            pass
