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

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QIcon, QImage, QPainter
from PyQt5.QtCore import QUrl, QFileInfo, QSettings, pyqtSignal
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import *
from qgis.gui import *
from qgis.core import QgsNetworkAccessManager, QgsVectorLayerUtils
from qgis.utils import iface
import plotly
import plotly.graph_objs as go

from DataPlotly.utils import *
from DataPlotly.data_plotly_plot import *

from collections import OrderedDict
import tempfile
from shutil import copyfile


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/dataplotly_dockwidget_base.ui'))


class DataPlotlyDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    # emit signal when dialog is resized
    resizeWindow = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(DataPlotlyDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # connect signal to function to reload the plot view
        self.resizeWindow.connect(self.reloadPlotCanvas)

        # create the reload button with text and icon
        self.reload_btn.setText("Reload")
        self.reload_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/reload.svg')))
        self.clear_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/clean.svg')))
        self.update_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/refresh.svg')))
        self.draw_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/create_plot.svg')))
        # connect the button to the reload function
        self.reload_btn.clicked.connect(self.reloadPlotCanvas2)

        # set the icon of QgspropertyOverrideButton not taken automatically
        self.size_defined_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/mIconDataDefineExpression.svg')))
        self.in_color_defined_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/mIconDataDefineExpression.svg')))

        # ListWidget icons and themes
        self.listWidget_icons = [
            QListWidgetItem(QIcon(os.path.join(os.path.dirname(__file__), 'icons/list_properties.svg')), ""),
            QListWidgetItem(QIcon(os.path.join(os.path.dirname(__file__), 'icons/list_custom.svg')), ""),
            QListWidgetItem(QIcon(os.path.join(os.path.dirname(__file__), 'icons/list_plot.svg')), ""),
            QListWidgetItem(QIcon(os.path.join(os.path.dirname(__file__), 'icons/list_help.svg')), ""),
            QListWidgetItem(QIcon(os.path.join(os.path.dirname(__file__), 'icons/list_code.svg')), "")
        ]

        # fill the QListWidget with items and icons
        for i in self.listWidget_icons:
            self.listWidget.addItem(i)

        # highlight the first row when starting the first time
        self.listWidget.setCurrentRow(0)

        # PlotTypes combobox
        self.plot_types = OrderedDict([
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/scatterplot.svg')), self.tr('Scatter Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/boxplot.svg')), self.tr('Box Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/barplot.svg')), self.tr('Bar Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/histogram.svg')), self.tr('Histogram')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/pie.svg')), self.tr('Pie Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/2dhistogram.svg')), self.tr('2D Histogram')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/polar.svg')), self.tr('Polar Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/scatterternary.svg')), self.tr('Ternary Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/contour.svg')), self.tr('Contour Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/contour.svg')), self.tr('Violin Plot')),
        ])

        self.plot_types2 = OrderedDict([
            (self.tr('Scatter Plot'), 'scatter'),
            (self.tr('Box Plot'), 'box'),
            (self.tr('Bar Plot'), 'bar'),
            (self.tr('Histogram'), 'histogram'),
            (self.tr('Pie Plot'), 'pie'),
            (self.tr('2D Histogram'), '2dhistogram'),
            (self.tr('Polar Plot'), 'polar'),
            (self.tr('Ternary Plot'), 'ternary'),
            (self.tr('Contour Plot'), 'contour'),
            (self.tr('Violin Plot'), 'violin'),
        ])

        self.plot_combo.clear()
        for k, v in self.plot_types.items():
            self.plot_combo.addItem(k, v)

        # SubPlots combobox
        self.subcombo.clear()
        self.sub_dict = OrderedDict([
            (self.tr('SinglePlot'), 'single'),
            (self.tr('SubPlots'), 'subplots')
        ])
        for k, v in self.sub_dict.items():
            self.subcombo.addItem(k, v)

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
            self.layer_combo.currentIndexChanged.connect(self.setCheckState)
        except:
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
        self.save_plot_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/save_as_image.svg')))
        self.save_plot_html_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/save_as_html.svg')))

        # inizialize the empty dictionary of plots
        self.plot_traces = {}
        # start the index counter
        self.idx = 1

        # load the help hatml page into the help widget
        self.layouth = QVBoxLayout()
        self.help_widget.setLayout(self.layouth)
        self.help_view = QWebView()
        self.layouth.addWidget(self.help_view)
        self.helpPage()

        # load the webview of the plot a the first running of the plugin
        self.layoutw = QVBoxLayout()
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
        self.ptype = self.plot_types2[self.plot_combo.currentText()]

        # load the layer fields in the init function for the datadefined buttons
        self.size_defined_button.setVectorLayer(self.layer_combo.currentLayer())
        self.in_color_defined_button.setVectorLayer(self.layer_combo.currentLayer())
        # connect the size defined button to the correct functions
        self.size_defined_button.changed.connect(self.refreshSizeDefined)
        # connect the color defined button to the correct function
        self.in_color_defined_button.changed.connect(self.resfreshColorDefined)

        # connect to refreshing function of listWidget and stackedWidgets
        self.listWidget.currentRowChanged.connect(self.updateStacked)

        # connect the plot changing to the color data defined buttons
        self.plot_combo.currentIndexChanged.connect(self.resfreshColorDefined)

    def updateStacked(self, row):
        '''
        according to the listWdiget row change the stackedWidget and
        nestedStackedWidget
        '''

        # stackedWidget index = 1 and change just the nestedStackedWidgets
        if 0 <= row <= 1:
            self.stackedPlotWidget.setCurrentIndex(0)
            self.stackedNestedPlotWidget.setCurrentIndex(row)

        # change the stackedWidgets index
        elif row > 1:
            self.stackedPlotWidget.setCurrentIndex(row - 1)


    def refreshSizeDefined(self):
        '''
        enable/disable the correct buttons depending on the choice
        '''
        if self.size_defined_button.isActive():
            self.marker_size.setEnabled(False)
        else:
            self.marker_size.setEnabled(True)

    def resfreshColorDefined(self):
        '''
        refreshing function for color data defined button

        checks is the datadefined button is active and check also the plot type
        in order to deactivate the color when not needed
        '''
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
        '''
        get the marker size
        '''

        if self.size_defined_button.isActive():
            mark_size = self.size_defined_button.toProperty().expressionString()
            self.marker_size_value = QgsVectorLayerUtils.getValues(self.layer_combo.currentLayer(), mark_size, selectedOnly=self.selected_feature_check.isChecked())[0]
        else:
            # self.marker_size.setEnabled(True)
            self.marker_size_value = self.marker_size.value()

    def getColorDefined(self):
        '''
        get the color code for plotly from the dataDefined button
        '''

        if self.in_color_defined_button.isActive():
            if self.ptype == 'scatter' or self.ptype == 'bar' or self.ptype == 'ternary':
                in_color = self.in_color_defined_button.toProperty().expressionString()
                self.in_color = QgsVectorLayerUtils.getValues(self.layer_combo.currentLayer(), in_color, selectedOnly=self.selected_feature_check.isChecked())[0]
            else:
                self.in_color = hex_to_rgb(self.in_color_combo)
        else:
            self.in_color = hex_to_rgb(self.in_color_combo)

    def setCheckState(self):
        '''
        change the selected_feature_check checkbox accordingly with the current
        layer selection state
        '''
        try:
            if self.layer_combo.currentLayer().selectedFeatures():
                self.selected_feature_check.setEnabled(True)
            else:
                self.selected_feature_check.setEnabled(False)
                self.selected_feature_check.setChecked(False)
        except:
            pass

    def getJSmessage(self, status):
        '''
        landing method for statusBarMessage signal coming from PLOT.js_callback
        it decodes feature ids of clicked or selected plot elements,
        selects on map canvas and triggers a pan/zoom to them

        the method handles several exceptions:
            the first try/except is due to the connection to the init method

            second try/except looks into the decoded status, that is, it decodes
            the js dictionary and loop where it is necessary

            the dic js dictionary contains several information useful to handle
            correctly every operation
        '''

        try:
            dic = json.JSONDecoder().decode(status)
        except:
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
                    exp = ''' "{}" = '{}' '''.format(dic['field'], dic['label'])
                    # set the iterator with the expression as filter in feature request
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds([f.id() for f in it])
                elif dic["type"] == 'histogram':
                    vmin = dic['id'] - dic['bin_step'] / 2
                    vmax = dic['id'] + dic['bin_step'] / 2
                    exp = ''' "{}" <= {} AND "{}" > {} '''.format(dic['field'], vmax ,dic['field'], vmin)
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds([f.id() for f in it])
                elif dic["type"] == 'scatterternary':
                    self.layer_combo.currentLayer().selectByIds([dic['fid']])
                else:
                    # build the expression from the js dic (customdata)
                    exp = ''' "{}" = '{}' '''.format(dic['field'], dic['id'])
                    # set the iterator with the expression as filter in feature request
                    request = QgsFeatureRequest().setFilterExpression(exp)
                    it = self.layer_combo.currentLayer().getFeatures(request)
                    self.layer_combo.currentLayer().selectByIds([f.id() for f in it])
                    print(exp)
        except:
            pass


    def helpPage(self):
        '''
        change the page of the manual according to the plot type selected and
        the language (looks for translations)
        '''

        locale = QSettings().value('locale/userLocale')[0:2]

        self.help_view.load(QUrl(''))
        self.layouth.addWidget(self.help_view)
        help_link = os.path.join(os.path.dirname(__file__), 'help/build/html/{}/{}.html'.format(locale, self.ptype))
        # check if the file exists, else open the default home page
        if not os.path.exists(help_link):
            help_link = os.path.join(os.path.dirname(__file__), 'help/build/html/{}/index.html'.format(locale))

        help_url = QUrl.fromLocalFile(help_link)
        self.help_view.load(help_url)

    def resizeEvent(self, event):
        '''
        reimplemented event to detect the dialog resizing
        '''
        self.resizeWindow.emit()
        return super(DataPlotlyDockWidget, self).resizeEvent(event)

    def reloadPlotCanvas(self):
        '''
        just reload the plot view controlling the check state
        '''
        if self.live_update_check.isChecked():
            self.plot_view.reload()

    def reloadPlotCanvas2(self):
        '''
        just reload the plot view
        '''
        self.plot_view.reload()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def refreshListWidget(self):
        '''
        highlight the item in the QListWidget when the QStackWidget changes

        needed to highligh the correct icon when the plot is rendered
        '''
        self.listWidget.setCurrentRow(self.stackedPlotWidget.currentIndex())


    def refreshWidgets(self):
        '''
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
        '''

        # get the plot type from the combobox
        self.ptype = self.plot_types2[self.plot_combo.currentText()]

        # Widget general customizations

        self.x_label.setText(self.tr('X Field'))
        ff = QFont()
        ff.setPointSizeF(9)
        self.x_label.setFont(ff)
        self.x_label.setFixedWidth(70)

        # BoxPlot BarPlot and Histogram orientation (same values)
        self.orientation_combo.clear()
        self.orientation_box = OrderedDict([
            (self.tr('Vertical'), 'v'),
            (self.tr('Horizontal'), 'h')
        ])
        for k, v in self.orientation_box.items():
            self.orientation_combo.addItem(k, v)

        # BoxPlot outliers
        self.outliers_combo.clear()
        self.outliers_dict = OrderedDict([
            (self.tr('No Outliers'), False),
            (self.tr('Standard Outliers'), 'outliers'),
            (self.tr('Suspected Outliers'), 'suspectedoutliers'),
            (self.tr('All Points'), 'all')
        ])
        for k, v in self.outliers_dict.items():
            self.outliers_combo.addItem(k, v)

        # BoxPlot statistic types
        self.statistic_type = OrderedDict([
            (self.tr('None'), False),
            (self.tr('Mean'), True),
            (self.tr('Standard Deviation'), 'sd'),
        ])
        self.box_statistic_combo.clear()
        for k, v in self.statistic_type.items():
            self.box_statistic_combo.addItem(k, v)

        # BoxPlot and ScatterPlot X axis type
        self.x_axis_type = OrderedDict([
            (self.tr('Linear'), 'linear'),
            (self.tr('Logarithmic'), 'log'),
            (self.tr('Categorized'), 'category'),
        ])
        self.x_axis_mode_combo.clear()
        for k, v in self.x_axis_type.items():
            self.x_axis_mode_combo.addItem(k, v)

        # BoxPlot and ScatterPlot Y axis type
        self.y_axis_type = OrderedDict([
            (self.tr('Linear'), 'linear'),
            (self.tr('Logarithmic'), 'log'),
            (self.tr('Categorized'), 'category'),
        ])
        self.y_axis_mode_combo.clear()
        for k, v in self.y_axis_type.items():
            self.y_axis_mode_combo.addItem(k, v)

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
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/circle.svg')), 'circle'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/square.svg')), 'square'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/diamond.svg')), 'diamond'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/cross.svg')), 'cross'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/x.svg')), 'x'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/triangle.svg')), 'triangle'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/penta.svg')), 'penta'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/star.svg')), 'star'),
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
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/solid.png')), self.tr('Solid Line')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/dot.png')), self.tr('Dot Line')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/dash.png')), self.tr('Dash Line')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/longdash.png')), self.tr('Long Dash Line')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/dotdash.png')), self.tr('Dot Dash Line')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/longdashdot.png', )), self.tr('Long Dash Dot Line')),
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
        self.bar_modes = OrderedDict([
            (self.tr('Grouped'), 'group'),
            (self.tr('Stacked'), 'stack'),
            (self.tr('Overlay'), 'overlay')
        ])
        self.bar_mode_combo.clear()
        for k, v in self.bar_modes.items():
            self.bar_mode_combo.addItem(k, v)

        # Histogram normalization mode
        self.normalization = OrderedDict([
            (self.tr('Enumerated'), ''),
            (self.tr('Percents'), 'percent'),
            (self.tr('Probability'), 'probability'),
            (self.tr('Density'), 'density'),
            (self.tr('Prob Density'), 'probability density'),
        ])
        self.hist_norm_combo.clear()
        for k, v in self.normalization.items():
            self.hist_norm_combo.addItem(k, v)

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
        self.col_scale = OrderedDict([
            (self.tr('OrangeToRed'), 'pairs'),
            (self.tr('Grey Scale'), 'Greys'),
            (self.tr('Green Scale'), 'Greens'),
            (self.tr('Fire Scale'), 'Hot'),
            (self.tr('BlueYellowRed'), 'Portland'),
            (self.tr('BlueGreenRed'), 'Jet'),
            (self.tr('BlueToRed'), 'RdBu'),
            (self.tr('BlueToRed Soft'), 'Bluered'),
            (self.tr('BlackRedYellowBlue'), 'Blackbody'),
            (self.tr('Terrain'), 'Earth'),
            (self.tr('Electric Scale'), 'Electric'),
            (self.tr('RedOrangeYellow'), 'YIOrRd'),
            (self.tr('DeepblueBlueWhite'), 'YIGnBu'),
            (self.tr('BlueWhitePurple'), 'Picnic'),
        ])
        self.color_scale_combo.clear()
        self.color_scale_data_defined_in.clear()
        for k, v in self.col_scale.items():
            self.color_scale_combo.addItem(k, v)
            self.color_scale_data_defined_in.addItem(k, v)

        # according to the plot type, change the label names

        # BoxPlot
        if self.ptype == 'box':
            self.x_label.setText(self.tr('Grouping Field\n(Optional)'))
            # set the horizontal and vertical size of the label and reduce the label font size
            ff = QFont()
            ff.setPointSizeF(8.5)
            self.x_label.setFont(ff)
            self.x_label.setFixedWidth(80)
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
        self.info_hover = OrderedDict([
            (self.tr('All Values'), 'all'),
            (self.tr('X Values'), 'x'),
            (self.tr('Y Values'), 'y'),
            (self.tr('No Data'), 'none')
        ])
        self.info_combo.clear()
        for k, v in self.info_hover.items():
            self.info_combo.addItem(k, v)

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
            self.in_color_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.in_color_combo: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.in_color_defined_button: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in_label: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in_check: ['scatter', 'bar', 'ternary'],
            self.color_scale_data_defined_in_invert_check: ['bar', 'ternary'],
            self.out_color_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.out_color_combo: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.marker_width_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.marker_width: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.marker_size_lab: ['scatter', 'polar', 'ternary'],
            self.marker_size: ['scatter', 'polar', 'ternary'],
            self.size_defined_button: ['scatter', 'ternary'],
            self.marker_type_lab: ['scatter'],
            self.marker_type_combo: ['scatter'],
            self.alpha_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.alpha_slid: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.alpha_num: ['scatter', 'bar', 'box', 'histogram', 'ternary'],
            self.mGroupBox_2: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'contour', '2dhistogram'],
            self.bar_mode_lab: ['bar', 'histogram'],
            self.bar_mode_combo: ['bar', 'histogram'],
            self.legend_label: ['all'],
            self.legend_title: ['all'],
            self.point_lab: ['scatter', 'ternary'],
            self.point_combo: ['scatter', 'ternary'],
            self.line_lab: ['scatter'],
            self.line_combo: ['scatter'],
            self.color_scale_label: ['contour', '2dhistogram'],
            self.color_scale_combo: ['contour', '2dhistogram'],
            self.contour_type_label: ['contour'],
            self.contour_type_combo: ['contour'],
            self.show_lines_check: ['contour'],

            # layout customization
            self.show_legend_check: ['all'],
            self.orientation_legend_check: ['scatter', 'bar', 'box', 'histogram', 'ternary', 'pie'],
            self.plot_title_lab: ['all'],
            self.plot_title_line: ['all'],
            self.x_axis_label: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary'],
            self.x_axis_title: ['scatter', 'bar', 'box', 'histogram', '2dhistogram', 'ternary'],
            self.y_axis_label: ['scatter', 'bar', 'box', '2dhistogram', 'ternary'],
            self.y_axis_title: ['scatter', 'bar', 'box', '2dhistogram', 'ternary'],
            self.z_axis_label: ['ternary'],
            self.z_axis_title: ['ternary'],
            self.x_axis_mode_label: ['scatter', 'box'],
            self.y_axis_mode_label: ['scatter', 'box'],
            self.x_axis_mode_combo: ['scatter', 'box'],
            self.y_axis_mode_combo: ['scatter', 'box'],
            self.invert_x_check: ['scatter', 'bar', 'box', 'histogram', '2dhistogram'],
            self.invert_y_check: ['scatter', 'bar', 'box', 'histogram', '2dhistogram'],
            self.orientation_label: ['bar', 'box', 'histogram'],
            self.orientation_combo: ['bar', 'box', 'histogram'],
            self.box_statistic_label: ['box'],
            self.box_statistic_combo: ['box'],
            self.outliers_label: ['box'],
            self.outliers_combo: ['box'],
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
            self.bar_gap: ['histogram']
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

        # disable at firts run the color data defined buttons
        self.color_scale_data_defined_in.setVisible(False)
        self.color_scale_data_defined_in_label.setVisible(False)
        self.color_scale_data_defined_in_check.setVisible(False)
        self.color_scale_data_defined_in_invert_check.setVisible(False)

    def refreshWidgets2(self):
        '''
        just refresh the UI to make the radiobuttons visible when SubPlots
        '''

        # enable radio buttons for subplots
        if self.subcombo.currentText() == self.tr('SubPlots'):
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
        '''
        refresh the UI according to Point, Lines or both choosen for the symbols
        of scatterplot
        '''

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
        '''
        set the legend from the fields combo boxes
        '''
        self.legend_title_string = ''

        if self.ptype == 'box' or self.ptype == 'bar':
            self.legend_title.setText(self.y_combo.currentText())

        elif self.ptype == 'histogram':
            self.legend_title.setText(self.x_combo.currentText())

        else:
            self.legend_title_string = ('{} - {}'.format(self.x_combo.currentText(), self.y_combo.currentText()))
            self.legend_title.setText(self.legend_title_string)

    def plotProperties(self):
        '''
        call the class and make the object to define the generic plot properties
        '''

        # call the method to get the correct marker size
        self.getMarkerSize()
        self.getColorDefined()

        # set the variable to invert the x and y axis order
        self.x_invert = True
        if self.invert_x_check.isChecked():
            self.x_invert = "reversed"
        self.y_invert = True
        if self.invert_y_check.isChecked():
            self.y_invert = "reversed"

        # set the bin value and change if according to the checkbox
        self.bin_val = None
        if self.bins_check.isChecked():
            self.bin_val = self.bins_value.value()

        # set the chance to invert the histogram direction
        self.invert_hist = 'increasing'
        if self.invert_hist_check.isChecked():
            self.invert_hist = 'decreasing'

        # get the plot type from the combo box
        self.ptype = self.plot_types2[self.plot_combo.currentText()]

        # shortcut to shorten the code in the following dictionary
        xx = QgsVectorLayerUtils.getValues(self.layer_combo.currentLayer(), self.x_combo.currentText(), selectedOnly=self.selected_feature_check.isChecked())[0]
        yy = QgsVectorLayerUtils.getValues(self.layer_combo.currentLayer(), self.y_combo.currentText(), selectedOnly=self.selected_feature_check.isChecked())[0]
        zz = QgsVectorLayerUtils.getValues(self.layer_combo.currentLayer(), self.z_combo.currentText(), selectedOnly=self.selected_feature_check.isChecked())[0]

        # call the function that will clean the data from NULL values
        xx, yy, zz, = cleanData(xx, yy, zz)

        ## if colorscale should be visible or not
        if self.color_scale_data_defined_in_check.isVisible() and self.color_scale_data_defined_in_check.isChecked():
            color_scale_visible = True
        else:
            color_scale_visible = False

        # dictionary of all the plot properties
        plot_properties = {
            'x':xx,
            'y':yy,
            'z':zz,
            # featureIds are the ID of each feature needed for the selection and zooming method
            'featureIds':getIds(self.layer_combo.currentLayer(), self.selected_feature_check.isChecked()),
            'featureBox':getSortedId(self.layer_combo.currentLayer(), xx),
            'custom':self.x_combo.currentText(),
            'hover_text':self.info_hover[self.info_combo.currentText()],
            'additional_hover_text':QgsVectorLayerUtils.getValues(self.layer_combo.currentLayer(), self.additional_info_combo.currentText(), selectedOnly=self.selected_feature_check.isChecked())[0],
            'x_name':self.x_combo.currentText(),
            'y_name':self.y_combo.currentText(),
            'z_name':self.z_combo.currentText(),
            'in_color':self.in_color,
            'colorscale_in':self.col_scale[self.color_scale_data_defined_in.currentText()],
            'show_colorscale_legend':color_scale_visible,
            'invert_color_scale':self.color_scale_data_defined_in_invert_check.isChecked(),
            'out_color':hex_to_rgb(self.out_color_combo),
            'marker_width':self.marker_width.value(),
            'marker_size':self.marker_size_value,
            'marker_symbol':self.point_types2[self.point_combo.currentData()],
            'line_dash':self.line_types2[self.line_combo.currentText()],
            'box_orientation':self.orientation_box[self.orientation_combo.currentText()],
            'marker':self.marker_types[self.marker_type_combo.currentText()],
            'opacity':(100 - self.alpha_slid.value()) / 100.0,
            'box_stat':self.statistic_type[self.box_statistic_combo.currentText()],
            'box_outliers':self.outliers_dict[self.outliers_combo.currentText()],
            'name':self.legend_title.text(),
            'normalization':self.normalization[self.hist_norm_combo.currentText()],
            'cont_type':self.contour_type[self.contour_type_combo.currentText()],
            'color_scale':self.col_scale[self.color_scale_combo.currentText()],
            'show_lines':self.show_lines_check.isChecked(),
            'cumulative':self.cumulative_hist_check.isChecked(),
            'invert_hist':self.invert_hist,
            'bins':self.bin_val
        }

        # define the legend orientation
        if self.orientation_legend_check.isChecked():
            legend_or = 'h'
        else:
            legend_or = 'v'

        # build the layout customizations
        layout_properties = {
            'legend':self.show_legend_check.isChecked(),
            'legend_orientation':legend_or,
            'title':self.plot_title_line.text(),
            'x_title':self.x_axis_title.text(),
            'y_title':self.y_axis_title.text(),
            'z_title':self.z_axis_title.text(),
            'range_slider':dict(visible=self.range_slider_combo.isChecked(), borderwidth=1),
            'bar_mode':self.bar_modes[self.bar_mode_combo.currentText()],
            'x_type':self.x_axis_type[self.x_axis_mode_combo.currentText()],
            'y_type':self.y_axis_type[self.y_axis_mode_combo.currentText()],
            'x_inv':self.x_invert,
            'y_inv':self.y_invert,
            'bargaps':self.bar_gap.value()
        }


        # plot instance
        self.plotobject = Plot(self.ptype, plot_properties, layout_properties)

        # build the final trace that will be used
        self.plotobject.buildTrace()

        # call the method and build the final layout
        self.plotobject.buildLayout()

        # unique name for each plot trace (name is idx_plot, e.g. 1_scatter)
        self.pid = ('{}_{}'.format(str(self.idx), self.ptype))

        # create default dictionary that contains all the plot and properties
        self.plot_traces[self.pid] = self.plotobject

        # just add 1 to the index
        self.idx += 1

        # enable the Update Plot button
        self.update_btn.setEnabled(True)


    def createPlot(self):
        '''
        call the method to effectively draw the final plot

        before creating the plot, it calls the method plotProperties in order
        to create the plot instance with all the properties taken from the UI
        '''

        # call the method to build all the Plot plotProperties
        self.plotProperties()

        # set the correct index page of the widget
        self.stackedPlotWidget.setCurrentIndex(1)
        # highlight the correct plot row in the listwidget
        self.listWidget.setCurrentRow(2)


        if self.sub_dict[self.subcombo.currentText()] == 'single':

            # plot single plot, check the object dictionary lenght
            if len(self.plot_traces) <= 1:
                self.plot_path = self.plotobject.buildFigure()

            # to plot many plots in the same figure
            else:
                # plot list ready to be called within go.Figure
                pl = []
                # layout list
                ll = None

                for k, v in self.plot_traces.items():
                    pl.append(v.trace[0])
                    ll = v.layout

                self.plot_path = self.plotobject.buildFigures(self.ptype, pl)

        # choice to draw subplots instead depending on the combobox
        elif self.sub_dict[self.subcombo.currentText()] == 'subplots':
            try:
                gr = len(self.plot_traces)
                pl = []
                tt = tuple([v.layout['title'] for v in self.plot_traces.values()])

                for k, v in self.plot_traces.items():
                    pl.append(v.trace[0])

                # plot in single row and many columns
                if self.radio_rows.isChecked():

                    self.plot_path = self.plotobject.buildSubPlots('row', 1, gr, pl, tt)

                # plot in single column and many rows
                elif self.radio_columns.isChecked():

                    self.plot_path = self.plotobject.buildSubPlots('col', gr, 1, pl, tt)
            except:
                iface.messageBar().pushMessage(self.tr("Plot types are not comapatible for subplotting"),
                             Qgis.MessageLevel(2), duration=3)
                return

        # connect to simple function that reloads the view
        self.refreshPlotView()

    def UpdatePlot(self):
        '''
        updates only the LAST plot created
        get the key of the last plot created and delete it from the plot container
        and call the method to create the plot with the updated settings
        '''

        plot_to_update = (sorted(self.plot_traces.keys())[-1])
        del self.plot_traces[plot_to_update]

        self.createPlot()


    def refreshPlotView(self):
        '''
        just resfresh the view, if the reload method is called immediatly after
        the view creation it won't reload the page
        '''

        self.plot_url = QUrl.fromLocalFile(self.plot_path)
        self.plot_view.load(self.plot_url)
        self.layoutw.addWidget(self.plot_view)

        self.raw_plot_text.clear()
        with open(self.plot_path, 'r') as myfile:
            plot_text = myfile.read()

        self.raw_plot_text.setPlainText(plot_text)

    def clearPlotView(self):
        '''
        clear the content of the QWebView by loading an empty url and clear the
        raw text of the QPlainTextEdit
        '''

        self.plot_traces = {}

        try:
            self.plot_view.load(QUrl(''))
            self.layoutw.addWidget(self.plot_view)
            self.raw_plot_text.clear()
            # disable the Update Plot Button
            self.update_btn.setEnabled(False)
        except:
            pass

    def savePlotAsImage(self):
        '''
        save the current plot view as png image.
        The user can choose the path and the file name
        '''
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
                iface.messageBar().pushMessage(self.tr("Plot succesfully saved"), Qgis.MessageLevel(0), duration=2)
        except:
            iface.messageBar().pushMessage(self.tr("Please select a directory to save the plot"), Qgis.MessageLevel(1), duration=4)

    def savePlotAsHtml(self, plot_file=None):
        '''
        save the plot as html local file. Basically just let the user choose
        where to save the already existing html file created by plotly
        '''

        try:
            self.plot_file = QFileDialog.getSaveFileName(self, self.tr("Save plot"), "", "*.html")
            self.plot_file = self.plot_file[0]
        except:
            self.plot_file = plot_file

        if self.plot_file and not self.plot_file.endswith('.html'):
            self.plot_file += '.html'

        if self.plot_file:
            copyfile(self.plot_path, self.plot_file)
            iface.messageBar().pushMessage(self.tr("Plot succesfully saved"), Qgis.MessageLevel(0), duration=2)


    def showPlotFromDic(self, plot_input_dic):
        '''
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
        '''
        # keys of the nested plot_prop and layout_prop have to be the SAME of
        # those created in buildProperties and buildLayout method

        # set some dialog widget from the input dictionary
        # plot type in the plot_combo combobox
        for k, v in self.plot_types2.items():
            if self.plot_types2[k] == plot_input_dic["plot_type"]:
                for ii, kk in enumerate(self.plot_types.keys()):
                    if self.plot_types[kk] == k:
                        self.plot_combo.setItemIcon(ii, kk)
                        self.plot_combo.setItemText(ii, k)
                        self.plot_combo.setCurrentIndex(ii)

        try:
            self.layer_combo.setLayer(plot_input_dic["layer"])
            if 'x_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["x_name"]:
                self.x_combo.setField(plot_input_dic["plot_prop"]["x_name"])
            if 'y_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["y_name"]:
                self.y_combo.setField(plot_input_dic["plot_prop"]["y_name"])
            if 'z_name' in plot_input_dic["plot_prop"] and plot_input_dic["plot_prop"]["z_name"]:
                self.z_combo.setField(plot_input_dic["plot_prop"]["z_name"])
        except:
            pass

        # create Plot instance
        plot_standalone = Plot(
            plot_input_dic['plot_type'],
            plot_input_dic["plot_prop"],
            plot_input_dic["layout_prop"]
        )

        # initialize plot properties and build them
        plot_standalone.buildTrace()
        plot_standalone.buildTrace()

        # initialize layout properties and build them
        plot_standalone.buildLayout()

        standalone_plot_path = plot_standalone.buildFigure()
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
        self.plot_traces[self.pid] = plot_standalone

        # just add 1 to the index
        self.idx += 1
