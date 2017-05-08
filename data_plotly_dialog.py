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

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QUrl
from PyQt5.QtWebKit import QWebSettings
from qgis.gui import *
import plotly
import plotly.graph_objs as go

from .utils import *
from .data_plotly_plot import *
from .plot_web_view import plotWebView


from collections import OrderedDict
import tempfile

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/data_plotly_dialog_base.ui'))


class DataPlotlyDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DataPlotlyDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # add bar to the main (upper part) window
        self.bar = QgsMessageBar()
        self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setLayout(QGridLayout())
        self.layout().addWidget(self.bar, 0, 0, 1, 0)

        # PlotTypes combobox
        self.plot_types = OrderedDict([
            (self.tr('Scatter Plot'), 'scatter'),
            (self.tr('Box Plot'), 'box'),
            (self.tr('Bar Plot'), 'bar'),
            (self.tr('Histogram'), 'histogram')
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
        # self.fillTabProperties()
        self.refreshWidgets()
        self.refreshWidgets2()
        self.plot_combo.currentIndexChanged.connect(self.refreshWidgets)
        self.subcombo.currentIndexChanged.connect(self.refreshWidgets2)

        self.mGroupBox_2.collapsedStateChanged.connect(self.refreshWidgets)

        # fill filed combo box when launching the UI
        self.x_combo.setLayer(self.layer_combo.currentLayer())
        self.y_combo.setLayer(self.layer_combo.currentLayer())

        self.draw_btn.clicked.connect(self.plotProperties)
        self.addTrace_btn.clicked.connect(self.createPlot)
        self.clear_btn.clicked.connect(self.removeTrace)
        self.remove_button.clicked.connect(self.removeTraceFromTable)

        self.plot_traces = {}

        self.idx = 1

        # load the customized webview in the widget
        # w = plotWebView()
        # layout = QVBoxLayout()
        # layout.setContentsMargins(0,0,0,0)
        # layout.setSpacing(0)
        # layout.addWidget(w)
        # w.show()
        # self.webview = w
        # self.webViewPage.setLayout(layout)

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
        self.ptype = self.plot_types[self.plot_combo.currentText()]

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

        # ScatterPlot marker types
        self.marker_types = OrderedDict([
            (self.tr('Points'), 'markers'),
            (self.tr('Lines'), 'lines'),
            (self.tr('Points and Lines'), 'lines+markers')
        ])
        self.marker_type_combo.clear()
        for k, v in self.marker_types.items():
            self.marker_type_combo.addItem(k, v)

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

        # according to the plot type, change the label names

        # BoxPlot
        if self.ptype == 'box':
            self.x_label.setText('Grouping Field\n(Optional)')
            # set the horizontal and vertical size of the label
            # self.x_label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            # reduce the label font size
            ff = QFont()
            ff.setPointSizeF(8.5)
            self.x_label.setFont(ff)
            self.x_label.setFixedWidth(80)
            self.orientation_label.setText('Box Orientation')
            self.in_color_lab.setText('Box Color')

        # ScatterPlot
        if self.ptype == 'scatter':
            self.in_color_lab.setText('Marker Color')

        # BarPlot
        if self.ptype == 'bar':
            self.orientation_label.setText('Bar Orientation')
            self.in_color_lab.setText('Bar Color')

        # dictionary with all the widgets and the plot they belong to
        self.widgetType = {
            # plot properties
            self.layer_combo: ['all'],
            self.x_combo: ['all'],
            self.y_label: ['scatter', 'bar', 'box'],
            self.y_combo: ['scatter', 'bar', 'box'],
            self.in_color_lab: ['all'],
            self.in_color_combo: ['all'],
            self.out_color_lab: ['all'],
            self.out_color_combo: ['all'],
            self.marker_width_lab: ['all'],
            self.marker_width: ['all'],
            self.marker_size_lab: ['scatter'],
            self.marker_size: ['scatter'],
            self.marker_type_lab: ['scatter'],
            self.marker_type_combo: ['scatter'],
            self.alpha_lab: ['all'],
            self.alpha_slid: ['all'],
            self.alpha_num: ['all'],
            self.bar_mode_lab: ['bar', 'histogram'],
            self.bar_mode_combo: ['bar', 'histogram'],
            self.bar_legend_label: ['bar'],
            self.bar_legend_title: ['bar'],

            # layout customization
            self.show_legend_check: ['all'],
            self.plot_title_lab: ['all'],
            self.plot_title_line: ['all'],
            self.x_axis_label: ['all'],
            self.x_axis_title: ['all'],
            self.y_axis_label: ['all'],
            self.y_axis_title: ['all'],
            self.orientation_label: ['bar', 'box', 'histogram'],
            self.orientation_combo: ['bar', 'box', 'histogram'],
            self.box_statistic_label: ['box'],
            self.box_statistic_combo: ['box'],
            self.outliers_label: ['box'],
            self.outliers_combo: ['box'],
            self.range_slider_combo: ['scatter'],
            self.hist_norm_label: ['histogram'],
            self.hist_norm_combo: ['histogram']
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

    def plotProperties(self):
        '''
        call the class and make the object to define the generic plot properties
        '''

        # get the plot type from the combo box
        self.ptype = self.plot_types[self.plot_combo.currentText()]

        # plot object
        self.p = Plot()

        # plot method to have a dictionary of the properties
        self.p.buildProperties(
            x=getFields(self.layer_combo, self.x_combo),
            y=getFields(self.layer_combo, self.y_combo),
            x_name=self.x_combo.currentText(),
            y_name=self.y_combo.currentText(),
            in_color=hex_to_rgb(self.in_color_combo),
            out_color=hex_to_rgb(self.out_color_combo),
            marker_width=self.marker_width.value(),
            marker_size=self.marker_size.value(),
            box_orientation=self.orientation_box[self.orientation_combo.currentText()],
            marker=self.marker_types[self.marker_type_combo.currentText()],
            opacity=(100 - self.alpha_slid.value()) / 100.0,
            box_stat=self.statistic_type[self.box_statistic_combo.currentText()],
            box_outliers=self.outliers_dict[self.outliers_combo.currentText()],
            bar_name=self.bar_legend_title.text(),
            normalization=self.normalization[self.hist_norm_combo.currentText()]
        )

        # build the final trace that will be used
        self.p.buildTrace(self.ptype)

        # build the layout customizations
        self.p.layoutProperties(
            legend=self.show_legend_check.isChecked(),
            title=self.plot_title_line.text(),
            x_title=self.x_axis_title.text(),
            y_title=self.y_axis_title.text(),
            range_slider=dict(visible=self.range_slider_combo.isChecked(), borderwidth=1),
            bar_mode=self.bar_modes[self.bar_mode_combo.currentText()]
        )

        # call the method and build the final layout
        self.p.buildLayout(self.ptype)

        # unique name for each plot trace (name is idx_plot, e.g. 1_scatter)
        self.pid = ('{}_{}'.format(str(self.idx), self.p.plot_type))

        # create default dictionary that contains all the plot and properties
        self.plot_traces[self.pid] = self.p

        # call the function and fill the table
        self.addTraceToTable()

        # just add 1 to the index
        self.idx += 1

        self.bar.pushMessage("Plot added to the basket", level=QgsMessageBar.INFO, duration=2)

    def addTraceToTable(self):
        '''
        add the created trace to the table traceTable
        '''
        row = self.traceTable.rowCount()
        self.traceTable.insertRow(row)

        # fill the table with each paramter entered
        self.traceTable.setItem(row, 0, QTableWidgetItem(str(self.pid)))
        self.traceTable.setItem(row, 1, QTableWidgetItem(str(self.p.plot_type)))
        self.traceTable.setItem(row, 2, QTableWidgetItem(str(self.x_combo.currentText())))
        self.traceTable.setItem(row, 3, QTableWidgetItem(str(self.y_combo.currentText())))

    def removeTraceFromTable(self):

        if not self.plot_traces:
            self.bar.pushMessage("No traces in the basket to delete!",
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

        self.bar.pushMessage("Plot removed from the basket", level=QgsMessageBar.INFO, duration=2)

    def createPlot(self):
        '''
        call the method to effectively draw the final plot
        '''

        # html = self.p.buildWeb()
        #
        #
        # html = html.replace(
        #     '</script><div',
        #     '</script><table width="100%"><tr><td><div')
        # html+= '</td></tr></table>'
        #
        # tmpdir = tempfile.mkdtemp()
        # predictable_filename = 'dataplot.html'
        # tpath = os.path.join(tmpdir, predictable_filename)
        # print(tpath)
        # with open(tpath, 'w') as afile:
        #     afile.write(html)
        # tptp = 'http://www.earthworks-jobs.com/index.shtml'
        # dddd = '/home/matteo/Downloads/dio.html'
        # dddd = '/home/matteo/Downloads/plot3.html'
        # self.webview.load(QUrl.fromLocalFile(tpath))
        # self.webview.settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        # self.webview.setHtml(html, baseUrl=QUrl().fromLocalFile(tpath))

        if not self.plot_traces:
            self.bar.pushMessage("Basket is empty, add some plot!",
                                 level=QgsMessageBar.CRITICAL, duration=3)
            return

        if self.sub_dict[self.subcombo.currentText()] == 'single':

            # plot single plot, che the object dictionary lenght
            if len(self.plot_traces) <= 1:
                self.p.buildFigure()

            # to plot many graphs in the same figure
            else:
                # plot list ready to be called within go.Figure
                pl = []
                # layout list
                ll = None

                for k, v in self.plot_traces.items():
                    pl.append(v.trace[0])
                    ll = v.layout

                self.p.buildFigures(pl)

        # choice to draw subplots instead depending on the combobox
        elif self.sub_dict[self.subcombo.currentText()] == 'subplots':

            gr = len(self.plot_traces)
            pl = []
            tt = tuple([v.layout['title'] for v in self.plot_traces.values()])

            for k, v in self.plot_traces.items():
                pl.append(v.trace[0])

            # plot in single row and many columns
            if self.radio_rows.isChecked():

                self.p.buildSubPlots('row', 1, gr, pl, tt)

            # plot in single column and many rows
            elif self.radio_columns.isChecked():

                self.p.buildSubPlots('col', gr, 1, pl)

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
        self.bar.pushMessage("Plot removed from the basket", level=QgsMessageBar.INFO, duration=2)
