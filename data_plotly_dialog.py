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

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QIcon, QImage, QPainter
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import *
from qgis.gui import *
from qgis.core import QgsNetworkAccessManager
import plotly
import plotly.graph_objs as go

from .utils import *
from .data_plotly_plot import *

from collections import OrderedDict
import tempfile
from shutil import copyfile

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/data_plotly_dialog_base.ui'))


class DataPlotlyDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, module, parent=None):
        """Constructor."""
        super(DataPlotlyDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.module = module

        # add bar to the main (upper part) window
        self.bar = QgsMessageBar()
        self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setLayout(QGridLayout())
        self.layout().insertWidget(0, self.bar)
        # self.layout().addWidget(self.bar, 0, 0, 2, 0)

        # PlotTypes combobox
        self.plot_types = OrderedDict([
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/scatterplot.png')), self.tr('Scatter Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/boxplot.png')), self.tr('Box Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/barplot.png')), self.tr('Bar Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/histogram.png')), self.tr('Histogram')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/pie.png')), self.tr('Pie Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/2dhistogram.png')), self.tr('2D Histogram')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/polar.png')), self.tr('Polar Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/scatterternary.png')), self.tr('Ternary Plot')),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/contour.png')), self.tr('Contour Plot')),
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
        self.subcombo.currentIndexChanged.connect(self.refreshWidgets2)
        self.marker_type_combo.currentIndexChanged.connect(self.refreshWidgets3)

        self.mGroupBox_2.collapsedStateChanged.connect(self.refreshWidgets)

        # fill the layer combobox with vector layers
        self.layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)

        # fill filed combo box when launching the UI
        self.x_combo.setLayer(self.layer_combo.currentLayer())
        self.y_combo.setLayer(self.layer_combo.currentLayer())

        self.draw_btn.clicked.connect(self.createPlot)
        self.addTrace_btn.clicked.connect(self.plotProperties)
        self.clear_btn.clicked.connect(self.removeTrace)
        self.remove_button.clicked.connect(self.removeTraceFromTable)
        self.save_plot_btn.clicked.connect(self.savePlotAsImage)
        self.save_plot_html_btn.clicked.connect(self.savePlotAsHtml)
        self.save_plot_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/save_as_image.png')))
        self.save_plot_html_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons/save_as_html.png')))

        self.plot_traces = {}

        self.idx = 1

        # load the help hatml page into the help widget
        layout = QVBoxLayout()
        self.help_widget.setLayout(layout)
        # temporary url to repository
        help_url = QUrl('http://dataplotly.readthedocs.io/en/latest/index.html')
        help_view = QWebView()
        help_view.load(help_url)
        layout.addWidget(help_view)

        # load the webview of the plot a the first running of the plugin
        self.layoutw = QVBoxLayout()
        self.plot_qview.setLayout(self.layoutw)
        self.plot_view = QWebView()
        self.plot_view.page().setNetworkAccessManager(QgsNetworkAccessManager.instance())
        # self.plot_view.statusBarMessage.connect(self.getJSmessage)
        plot_view_settings = self.plot_view.settings()
        plot_view_settings.setAttribute(QWebSettings.WebGLEnabled, True)
        plot_view_settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        plot_view_settings.setAttribute(QWebSettings.Accelerated2dCanvasEnabled, True)
        self.layoutw.addWidget(self.plot_view)

    # def getJSmessage(self, status):
    #     '''
    #     landing method for statusBarMessage signal coming from PLOT.js_callback
    #     it decodes feature ids of clicked or selected plot elements,
    #     selects on map canvas and triggers a pan/zoom to them
    #     '''
    #     try:
    #         ids = json.JSONDecoder().decode(status)
    #     except:
    #         ids = None
    #     if ids:
    #         self.layer_combo.currentLayer().selectByIds(ids)
    #         if len(ids) > 1:
    #             self.module.iface.actionZoomToSelected().trigger()
    #         else:
    #             self.module.iface.actionPanToSelected().trigger()


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

        self.x_label.setText('X Field')
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
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/circle.png')), 'circle'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/square.png')), 'square'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/diamond.png')), 'diamond'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/cross.png')), 'cross'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/x.png')), 'x'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/triangle.png')), 'triangle'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/penta.png')), 'penta'),
            (QIcon(os.path.join(os.path.dirname(__file__), 'icons/star.png')), 'star'),
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
            ('Solid Line', 'solid'),
            ('Dot Line', 'dot'),
            ('Dash Line', 'dash'),
            ('Long Dash Line', 'longdash'),
            ('Dot Dash Line', 'dashdot'),
            ('Long Dash Dot Line', 'longdashdot'),
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

        # Contour Plot color scale
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
        for k, v in self.col_scale.items():
            self.color_scale_combo.addItem(k, v)

        # according to the plot type, change the label names

        # BoxPlot
        if self.ptype == 'box':
            self.x_label.setText('Grouping Field\n(Optional)')
            # set the horizontal and vertical size of the label and reduce the label font size
            ff = QFont()
            ff.setPointSizeF(8.5)
            self.x_label.setFont(ff)
            self.x_label.setFixedWidth(80)
            self.orientation_label.setText('Box Orientation')
            self.in_color_lab.setText('Box Color')

        # ScatterPlot
        if self.ptype == 'scatter' or 'ternary':
            self.in_color_lab.setText('Marker Color')

        # BarPlot
        if self.ptype == 'bar':
            self.orientation_label.setText('Bar Orientation')
            self.in_color_lab.setText('Bar Color')

        # PiePlot
        if self.ptype == 'pie':
            self.x_label.setText('Grouping Field')
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
            self.y_label: ['scatter', 'bar', 'box', 'pie', '2dhistogram', 'polar', 'ternary', 'contour'],
            self.y_combo: ['scatter', 'bar', 'box', 'pie', '2dhistogram', 'polar', 'ternary', 'contour'],
            self.z_label: ['ternary'],
            self.z_combo: ['ternary'],
            self.info_label: ['scatter'],
            self.info_combo: ['scatter'],
            self.in_color_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.in_color_combo: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.out_color_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.out_color_combo: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.marker_width_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.marker_width: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.marker_size_lab: ['scatter', 'polar', 'ternary'],
            self.marker_size: ['scatter', 'polar', 'ternary'],
            self.marker_type_lab: ['scatter'],
            self.marker_type_combo: ['scatter'],
            self.alpha_lab: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.alpha_slid: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary'],
            self.alpha_num: ['scatter', 'bar', 'box', 'histogram', 'ternary'],
            self.mGroupBox_2: ['scatter', 'bar', 'box', 'histogram', 'polar', 'ternary', 'contour', '2dhistogram'],
            self.bar_mode_lab: ['bar', 'histogram'],
            self.bar_mode_combo: ['bar', 'histogram'],
            self.bar_legend_label: ['bar'],
            self.bar_legend_title: ['bar'],
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
            self.plot_title_lab: ['all'],
            self.plot_title_line: ['all'],
            self.x_axis_label: ['scatter', 'bar', 'box', 'histogram', 'ternary'],
            self.x_axis_title: ['scatter', 'bar', 'box', 'histogram', 'ternary'],
            self.y_axis_label: ['scatter', 'bar', 'box', 'histogram', 'ternary'],
            self.y_axis_title: ['scatter', 'bar', 'box', 'histogram', 'ternary'],
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
        }

        # enable the widget according to the plot type
        for k, v in self.widgetType.items():
            if 'all' in v or self.ptype in v:
                k.setEnabled(True)
                k.setVisible(True)
            else:
                k.setEnabled(False)
                k.setVisible(False)

    def refreshWidgets2(self):
        '''
        just refresh the UI to make the radiobuttons visible when SubPlots
        '''

        # enable radio buttons for subplots
        if self.subcombo.currentText() == 'SubPlots':
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

        if self.marker_type_combo.currentText() == 'Points':
            self.point_lab.setEnabled(True)
            self.point_lab.setVisible(True)
            self.point_combo.setEnabled(True)
            self.point_combo.setVisible(True)
            self.line_lab.setEnabled(False)
            self.line_lab.setVisible(False)
            self.line_combo.setEnabled(False)
            self.line_combo.setVisible(False)
        elif self.marker_type_combo.currentText() == 'Lines':
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

    def plotProperties(self):
        '''
        call the class and make the object to define the generic plot properties
        '''

        # set the variable to invert the x and y axis order
        self.x_invert = True
        if self.invert_x_check.isChecked():
            self.x_invert = "reversed"
        self.y_invert = True
        if self.invert_y_check.isChecked():
            self.y_invert = "reversed"

        # get the plot type from the combo box
        self.ptype = self.plot_types2[self.plot_combo.currentText()]
        # plot object
        self.plotobject = Plot()

        # plot method to have a dictionary of the properties
        self.plotobject.buildProperties(
            # x=getFields(self.layer_combo, self.x_combo),
            x=self.layer_combo.currentLayer().getValues(self.x_combo.currentText(), selectedOnly=self.selected_feature_check.isChecked())[0],
            y=self.layer_combo.currentLayer().getValues(self.y_combo.currentText(), selectedOnly=self.selected_feature_check.isChecked())[0],
            z=self.layer_combo.currentLayer().getValues(self.z_combo.currentText(), selectedOnly=self.selected_feature_check.isChecked())[0],
            # featureIds=getFields(self.layer_combo, None),
            hover_text=self.info_hover[self.info_combo.currentText()],
            additional_hover_text=self.layer_combo.currentLayer().getValues(self.additional_info_combo.currentText(), selectedOnly=self.selected_feature_check.isChecked())[0],
            x_name=self.x_combo.currentText(),
            y_name=self.y_combo.currentText(),
            z_name=self.z_combo.currentText(),
            in_color=hex_to_rgb(self.in_color_combo),
            out_color=hex_to_rgb(self.out_color_combo),
            marker_width=self.marker_width.value(),
            marker_size=self.marker_size.value(),
            marker_symbol=self.point_types2[self.point_combo.currentData()],
            line_dash=self.line_types2[self.line_combo.currentText()],
            box_orientation=self.orientation_box[self.orientation_combo.currentText()],
            marker=self.marker_types[self.marker_type_combo.currentText()],
            opacity=(100 - self.alpha_slid.value()) / 100.0,
            box_stat=self.statistic_type[self.box_statistic_combo.currentText()],
            box_outliers=self.outliers_dict[self.outliers_combo.currentText()],
            bar_name=self.bar_legend_title.text(),
            normalization=self.normalization[self.hist_norm_combo.currentText()],
            cont_type=self.contour_type[self.contour_type_combo.currentText()],
            color_scale=self.col_scale[self.color_scale_combo.currentText()],
            show_lines=self.show_lines_check.isChecked()
        )

        # a = getFields2(self.layer_combo, self.x_combo)

        # build the final trace that will be used
        self.plotobject.buildTrace(
            plot_type=self.ptype
        )

        # build the layout customizations
        self.plotobject.layoutProperties(
            legend=self.show_legend_check.isChecked(),
            title=self.plot_title_line.text(),
            x_title=self.x_axis_title.text(),
            y_title=self.y_axis_title.text(),
            z_title=self.z_axis_title.text(),
            range_slider=dict(visible=self.range_slider_combo.isChecked(), borderwidth=1),
            bar_mode=self.bar_modes[self.bar_mode_combo.currentText()],
            x_type=self.x_axis_type[self.x_axis_mode_combo.currentText()],
            y_type=self.y_axis_type[self.y_axis_mode_combo.currentText()],
            x_inv=self.x_invert,
            y_inv=self.y_invert,
        )

        # call the method and build the final layout
        self.plotobject.buildLayout(
            plot_type=self.ptype
        )

        # unique name for each plot trace (name is idx_plot, e.g. 1_scatter)
        self.pid = ('{}_{}'.format(str(self.idx), self.ptype))

        # create default dictionary that contains all the plot and properties
        self.plot_traces[self.pid] = self.plotobject

        # call the function and fill the table
        self.addTraceToTable()

        # just add 1 to the index
        self.idx += 1

        self.bar.pushMessage(self.tr("Plot added to the basket"), level=QgsMessageBar.INFO, duration=2)

    def addTraceToTable(self):
        '''
        add the created trace to the table traceTable
        '''
        row = self.traceTable.rowCount()
        self.traceTable.insertRow(row)

        # fill the table with each paramter entered
        self.traceTable.setItem(row, 0, QTableWidgetItem(str(self.pid)))
        self.traceTable.setItem(row, 1, QTableWidgetItem(str(self.ptype)))
        self.traceTable.setItem(row, 2, QTableWidgetItem(str(self.x_combo.currentText())))
        self.traceTable.setItem(row, 3, QTableWidgetItem(str(self.y_combo.currentText())))

    def removeTraceFromTable(self):

        if not self.plot_traces:
            self.bar.pushMessage(self.tr("No traces in the basket to delete!"),
                                 level=QgsMessageBar.CRITICAL, duration=2)
            return

        selection = self.traceTable.selectionModel()
        rows = selection.selectedRows()

        plot_list = []

        for row in reversed(rows):
            index = row.row()
            plot_list.append(self.traceTable.item(index, 0).text())
            self.traceTable.removeRow(row.row())

        # remove also the selected row from the plot dictionary
        for p in plot_list:
            del self.plot_traces[p]

            # refresh the plot view by removing the selected plot
            self.createPlot()
            self.bar.pushMessage(self.tr("Plot removed from the basket"), level=QgsMessageBar.INFO, duration=2)

    def createPlot(self):
        '''
        call the method to effectively draw the final plot
        '''

        if not self.plot_traces:
            self.bar.pushMessage(self.tr("Basket is empty, add some plot!"),
                                 level=QgsMessageBar.CRITICAL, duration=3)
            return

        if self.sub_dict[self.subcombo.currentText()] == 'single':

            # plot single plot, check the object dictionary lenght
            if len(self.plot_traces) <= 1:
                self.plot_path = self.plotobject.buildFigure(plot_type=self.ptype)

            # to plot many plots in the same figure
            else:
                # plot list ready to be called within go.Figure
                pl = []
                # layout list
                ll = None

                for k, v in self.plot_traces.items():
                    pl.append(v.trace[0])
                    ll = v.layout

                self.plot_path = self.plotobject.buildFigures(pl=pl, plot_type=self.ptype)

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
                self.bar.pushMessage(self.tr("Plot types are not comapatible for subplotting. Please remove the plot from the Plot Basket"),
                             level=QgsMessageBar.CRITICAL, duration=3)
                return

        # connect to simple function that reloads the view
        self.refreshPlotView()

    def removeTrace(self):
        '''
        remove the selected rows in the table and delete the plot parameters
        from the dictionary
        '''

        self.traceTable.setRowCount(0)

        # delete the entire dictionary
        del self.plot_traces
        self.plot_traces = {}
        self.idx = 1
        self.bar.pushMessage(self.tr("Plot removed from the basket"), level=QgsMessageBar.INFO, duration=2)

        # call the method to completely clean the plot view and the QWebWidget
        self.clearPlotView()

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
        try:
            self.plot_view.load(QUrl(''))
            self.layoutw.addWidget(self.plot_view)
            self.raw_plot_text.clear()
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
                self.bar.pushMessage(self.tr("Plot succesfully saved"), level=QgsMessageBar.INFO, duration=2)
        except:
            self.bar.pushMessage(self.tr("Please select a directory to save the plot"), level=QgsMessageBar.WARNING, duration=4)

    def savePlotAsHtml(self):
        '''
        save the plot as html local file. Basically just let the user choose
        where to save the already existing html file created by plotly
        '''

        self.plot_file = QFileDialog.getSaveFileName(self, self.tr("Save plot"), "", "*.html")

        self.plot_file = self.plot_file[0]
        if self.plot_file:
            self.plot_file += '.html'

        if self.plot_file:
            copyfile(self.plot_path, self.plot_file)
            self.bar.pushMessage(self.tr("Plot succesfully saved"), level=QgsMessageBar.INFO, duration=2)
