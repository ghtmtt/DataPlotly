# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotDialog
                                 A QGIS plugin
 High level charts
                             -------------------
        begin                : 2016-04-27
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Matteo Ghetta
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

import PyQt5
from PyQt5 import QtGui, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.gui import *
from qgis.core import QgsExpression, QgsVectorLayer
import plotly
import plotly.graph_objs as go
import tempfile
from .utils import hex_to_rgb




FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/Bar.ui'))

class BarPlotDialog(PyQt5.QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(BarPlotDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.Bar)

        # connect button to choose the file for local saving
        self.browseButton.clicked.connect(self.saveFile)

        # filter only vector layers in the QgsMapLayerComboBox
        self.LayerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)

        # connect button to signals
        self.addTrace.clicked.connect(self.addNewTrace)
        self.deleteTrace.clicked.connect(self.removeTrace)

        # get the initial index value for future iterations
        self.index = 1

        # initialize the dictionary that will store all the plot values
        self.superdict = dict()



    # function to store the path of the opened folder when saving the plot
    def saveFile(self):
        self.filePath.setText(QFileDialog.getOpenFileName())



    def addNewTrace(self):
        '''
        fill the table with the parameters added in the dialog
        '''
        row = self.traceTable.rowCount()
        self.traceTable.insertRow(row)

        # fill the table with each paramter entered
        self.traceTable.setItem(row, 0, QTableWidgetItem(str(self.index)))
        self.traceTable.setItem(row, 1, QTableWidgetItem(str(self.LayerCombo.currentText())))
        self.traceTable.setItem(row, 2, QTableWidgetItem(str(self.expField1.currentText())))
        self.traceTable.setItem(row, 3, QTableWidgetItem(str(self.expField2.currentText())))
        self.traceTable.setItem(row, 4, QTableWidgetItem(str(self.colorButton.color().name())))
        self.traceTable.setItem(row, 5, QTableWidgetItem(str(self.alpha.value())))

        self.index += 1


        # get layer and the selected fields (signals and update directly in the UI)


        # QgsVectorLayer
        lay1 = self.expField1.layer()
        # name of the field of the QgsVectorLayer
        lay1_f = self.expField1.currentText()
        # QgsVectorLayer
        lay2 = self.expField2.layer()
        # name of the field of the QgsVectorLayer
        lay2_f = self.expField2.currentText()


        # build the lists from the selected fields
        f1 = []
        f2 = []

        # loop to use normal field or selected expression for first layer
        if self.expField1.currentField()[1] == False:
            for i in lay1.getFeatures():
                f1.append(i[lay1_f])
        else:
            filter1 = self.expField1.currentField()[0]
            exp1 = QgsExpression(filter1)
            for i in lay1.getFeatures():
                f1.append(exp1.evaluate(i, lay1.pendingFields()))

        # loop to use normal field or selected expression for second layer
        if self.expField2.currentField()[1] == False:
            for i in lay2.getFeatures():
                f2.append(i[lay2_f])
        else:
            filter2 = self.expField2.currentField()[0]
            exp2 = QgsExpression(filter2)
            for i in lay2.getFeatures():
                f2.append(exp2.evaluate(i, lay2.pendingFields()))


        # get the hex code from the button
        colorhex = self.colorButton.color().name()

        # convert the hex code to a rgb tuple
        colorrgb = hex_to_rgb(colorhex)


        # value of the slider for the alpha channel
        alphavalue = self.alpha.value()


        # create dictionary with all the plot parameters (each time the button is clicked a ner dictionary is added as VALUE to the initial dictionary)

        self.plot_param = dict()
        self.plot_param["index"] = self.index
        self.plot_param["layer"] = self.LayerCombo.currentLayer()
        self.plot_param["X"]= f1
        self.plot_param["Y"] = f2
        self.plot_param["Color"] = colorrgb
        self.plot_param["Transparency"] = alphavalue
        self.plot_param["Name"] = self.expField2.currentText()


        # add the dictionary with plot values to the initial dictionary
        self.superdict[row] = self.plot_param


    def removeTrace(self):
        '''
        remove the selected rows in the table and delete the plot parameters from the dictionary
        '''
        selection = self.traceTable.selectionModel()
        rows = selection.selectedRows()

        for row in reversed(rows):
            index = row.row()
            self.traceTable.removeRow(row.row())
            del self.superdict[row.row()]



    def Bar(self):

        # Layout settings, these are the same for all the plots

        # legend checkbox (default is checked = True)
        if self.legendCheck.isChecked():
            legend = True
        else:
            legend = False

        # plot title
        plotTitle = self.pltTitle.text()

        # bar modes (grouped or stacked)
        bar = self.barCombo.currentText()

        orientation = self.orientationCombo.currentText()


        # initialize the scatter plot with the first trace
        trace = []

        # loop over the dictionary keys and add it to the list
        for key in self.superdict:
            x = self.superdict[key].get('X')
            y = self.superdict[key].get('Y')
            mark = self.superdict[key].get('Marker')
            color = self.superdict[key].get('Color')
            transparency = self.superdict[key].get('Transparency')
            name = self.superdict[key].get('Name')

            trace.append(go.Bar(
            x = x,
            y = y,
            marker = dict(color = 'rgb' + str(color)),
            name = name,
            opacity = (100 - transparency) / 100.0,
            orientation = orientation
            ))


        # build the data object with all the traces added
        data = trace


        # Axis Label Options
        xaxis = dict()
        yaxis = dict()

        if self.xAxisCheck.isChecked():
            xaxis = dict(title = self.xAxisText.text())

        if self.yAxisCheck.isChecked():
            yaxis = dict(title = self.yAxisText.text())




        # build the layout object
        layout = go.Layout(
        showlegend = legend,
        barmode = bar,
        xaxis = xaxis,
        yaxis = yaxis,
        title = plotTitle
        )

        # build the final figure
        fig = go.Figure(data=data, layout=layout)


        # name of the local temporary file (cross platform)
        t = tempfile.gettempdir()

        if self.filePath.text() == 'Temporary file':
            name = t + u'/temp_plotly_plot.html'
            name = str(name)
        else:
            name = self.filePath.text() + '.html'
            name = str(name)

        # print self.filePath.text()

        # final function that draws the plot
        plotly.offline.plot(fig, filename=name)
