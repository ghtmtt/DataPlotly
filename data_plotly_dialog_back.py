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
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont
from qgis.gui import *
import plotly
import plotly.graph_objs as go

from .utils import *

from collections import OrderedDict

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




        # ordered dictionary of plot types
        self.plot_types = OrderedDict([
        (self.tr('Bar Plot'), 'bar'),
        (self.tr('Scatter Plot'), 'scatter'),
        (self.tr('Box Plot'), 'box')
        ])

        # fill the combo box with the dictionary value
        self.plot_combo.clear()
        for k, v in self.plot_types.items():
            self.plot_combo.addItem(k, v)


        # connect to the functions to clean the UI and fill with the correct widgets
        # self.fillTabProperties()
        self.refreshWidgets()
        self.plot_combo.currentIndexChanged.connect(self.refreshWidgets)

        self.draw_btn.clicked.connect(self.drawPlot)
        self.addTrace_btn.clicked.connect(self.addTrace)
        self.remove_button.clicked.connect(self.removeTrace)

        # initialize the traceTable index
        self.idx = 1

        self.plot_dict = {}
        self.lay_dict = {}

    def refreshWidgets(self):
        '''
        refresh UI widgets depending on the plot type in the combobox

        self.widgetType is a dict of widget depending on the plot type chosen
        'all': is for all the plot type, else the name of the plot is
        explicitated
        '''

        # get the plot type from the combobox
        self.ptype = self.plot_types[self.plot_combo.currentText()]

        # widget general customizations
        self.x_label.setText('X Field')
        ff = QFont()
        ff.setPointSizeF(9)
        self.x_label.setFont(ff)

        # same for Box and Bar
        self.orientation_combo.clear()
        self.orientation_box = OrderedDict([
        (self.tr('Vertical'), 'v'),
        (self.tr('Horizontal'), 'h')
        ])
        for k, v in self.orientation_box.items():
            self.orientation_combo.addItem(k, v)


        # according to the plot type, change the label names

        # Box Plot
        if self.ptype == 'box':
            self.x_label.setText('Grouping Field\n(Optional)')
            # set the horizontal and vertical size of the label
            self.x_label.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred))
            # reduce the label font size
            ff = QFont()
            ff.setPointSizeF(8.5)
            self.x_label.setFont(ff)
            self.orientation_label.setText('Box Orientation')

            self.statistic_type = OrderedDict([
            (self.tr('None'), 'None'),
            (self.tr('Mean'), 'mean'),
            (self.tr('Standard Deviation'), 'sd'),
            ])

            self.box_statistic_combo.clear()
            for k, v in self.statistic_type.items():
                self.box_statistic_combo.addItem(k, v)

            self.in_color_lab.setText('Box Color')



        # some custom for plot widget and other UI stuff
        if self.ptype == 'scatter':
            # ordered dictionary of marker types for Scatter Plot
            self.marker_types = OrderedDict([
            (self.tr('Points'), 'markers'),
            (self.tr('Lines'), 'lines'),
            (self.tr('Points and Lines'), 'lines+markers')
            ])

            # fill the combo box with the dictionary value
            self.marker_type_combo.clear()
            for k, v in self.marker_types.items():
                self.marker_type_combo.addItem(k, v)

            self.in_color_lab.setText('Marker Color')


        # Bar Plot
        if self.ptype == 'bar':
            # ordered dictionary of bar modes for Bar Plot
            self.bar_modes = OrderedDict([
            (self.tr('Grouped'), 'group'),
            (self.tr('Stacked'), 'stack'),
            ])
            self.bar_mode_combo.clear()
            for k, v in self.bar_modes.items():
                self.bar_mode_combo.addItem(k, v)

            self.orientation_label.setText('Bar Orientation')
            self.in_color_lab.setText('Bar Color')



        self.widgetType = {
        # plot widgets
            self.layer_combo: ['all'],
            self.x_combo: ['all'],
            self.y_combo: ['all'],
            self.in_color_lab: ['all'],
            self.in_color_combo: ['all'],
            self.out_color_lab: ['all'],
            self.out_color_combo: ['all'],
            self.marker_width_lab: ['all'],
            self.marker_width: ['all'],
            self.marker_size_lab: ['scatter', 'box'],
            self.marker_size: ['scatter', 'box'],
            self.marker_type_lab: ['scatter'],
            self.marker_type_combo: ['scatter'],
            self.alpha_lab: ['all'],
            self.alpha_slid: ['all'],
            self.alpha_num: ['all'],
            self.bar_mode_lab: ['bar'],
            self.bar_mode_combo: ['bar'],
        # layout customization
            self.show_legend_check: ['all'],
            self.plot_title_lab: ['all'],
            self.plot_title_line: ['all'],
            self.x_axis_label: ['all'],
            self.x_axis_title: ['all'],
            self.y_axis_label: ['all'],
            self.y_axis_title: ['all'],
            self.orientation_label: ['bar', 'box'],
            self.orientation_combo: ['bar', 'box'],
            self.box_statistic_label: ['box'],
            self.box_statistic_combo: ['box']
        }



        # get only the widget specific for the plot type
        for k, v in self.widgetType.items():
            if 'all' in v or self.ptype in v:
                k.setEnabled(True)
                k.setVisible(True)
            else:
                k.setEnabled(False)
                k.setVisible(False)


    def plotProperties(self, plot_type):
        '''
        defines the generic plot properties
        '''

        # empty dictionary with all the properties

        prop = {}


        # generic properties for all plots
        prop['x'] = getFields(self.layer_combo, self.x_combo)
        prop['y'] = getFields(self.layer_combo, self.y_combo)
        prop['x_name'] = self.x_combo.currentText()
        prop['y_name'] = self.y_combo.currentText()
        prop['in_color'] = hex_to_rgb(self.in_color_combo)
        prop['out_color'] = hex_to_rgb(self.out_color_combo)



        # append additional keys specific for each plot type (if plot_type == 'box')
        if plot_type == 'box':
            prop['marker_width'] = self.marker_width.value()
            prop['box_orientation'] = self.orientation_box[self.orientation_combo.currentText()]

        if plot_type == 'scatter':
            prop['marker'] = self.marker_types[self.marker_type_combo.currentText()]



        return prop


    def removeTrace(self):
        '''
        remove the selected rows in the table and delete the plot parameters
        from the dictionary
        '''
        selection = self.traceTable.selectionModel()
        rows = selection.selectedRows()

        for row in reversed(rows):
            index = row.row()
            self.traceTable.removeRow(row.row())
            del self.plot_dict[row.row() + 1]


    def addTrace(self):
        '''
        add single traces to the table so that the user can draw many different
        plot in the same graph
        '''

        # get the plot type from the combobox
        self.ptype = self.plot_types[self.plot_combo.currentText()]

        # start adding the row to the trace table
        row = self.traceTable.rowCount()
        self.traceTable.insertRow(row)

        # fill the table with custom ID and the plot type
        self.traceTable.setItem(row, 0, QTableWidgetItem(str(self.idx)))
        self.traceTable.setItem(row, 1, QTableWidgetItem(self.ptype))



        self.ptype = self.plot_types[self.plot_combo.currentText()]

        p = self.plotProperties(self.ptype)


        # Traces with the data
        trace = None

        # create plot instances

        if self.ptype == 'box':
            trace = go.Box(
            y = p['y']
            )

        elif self.ptype == 'scatter':
            trace = go.Scatter(
            x = p['x'],
            y = p['y'],
            mode = p['marker'],
            name = p['y_name'],
            marker = dict(
                color = p['in_color'],
                size = self.marker_size.value(),
                line = dict(
                    color = p['out_color'],
                    width = self.marker_width.value()
                    )
                ),
            line = dict(
                color = p['in_color'],
                width = self.marker_width.value()
                ),
            opacity = (100 - self.alpha_slid.value()) / 100.0
            )

        # Layout customization

        layout = go.Layout(
        showlegend = self.show_legend_check.isChecked(),
        title = self.plot_title_line.text()
        )


        # fill the dictionary with key = unique key, values = plot traces
        self.plot_dict[row + 1] = {'trace': trace, 'layout': layout}

        # be sure to have incremental idx
        self.idx += 1


    def drawPlot(self):

        d = []

        for k, v in self.plot_dict.items():
            d.append(v['trace'])

        # if there iis only a single plot, consider also the customizations
        i = next(iter(self.plot_dict))
        if len(self.plot_dict) < 2:
            fig = go.Figure(data = d, layout = self.plot_dict[i]['layout'])
            plotly.offline.plot(fig)

        # if many different plot are set, don't consider the customizations
        # and let plotly draw the single legend for each trace
        else:
            fig = go.Figure(data = d)
            plotly.offline.plot(fig)
