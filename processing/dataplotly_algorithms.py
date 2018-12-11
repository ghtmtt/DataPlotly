# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotly
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
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from DataPlotly.data_plotly_plot import *

from qgis.utils import plugins
from qgis.core import (
    QgsProcessingUtils,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterString,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputHtml,
    QgsProcessingOutputFile,
    QgsSettings,
    QgsFeatureRequest

)

from qgis.PyQt.QtCore import Qt, QCoreApplication

from processing.tools import vector

from shutil import copyfile
import json, codecs
class DataPlotlyProcessingPlot(QgisAlgorithm):

    """
    Create a simple plot with DataPlotly plugin
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    PLOT_TYPE = 'PLOT_TYPE'
    PLOT_TITLE = 'PLOT_TITLE'
    PLOT_TYPE_OPTIONS = ['scatter', 'box', 'bar', 'histogram', 'pie', '2dhistogram', 'polar', 'contour']
    X_MANDATORY = ['scatter', 'bar', 'histogram', '2dhistogram', 'polar', 'contour']
    Y_MANDATORY = ['scatter', 'box', 'bar', 'pie', '2dhistogram', 'polar', 'contour']
    XFIELD = 'XFIELD'
    YFIELD = 'YFIELD'
    IN_COLOR = 'IN_COLOR'
    IN_COLOR_OPTIONS = ['Black', 'Blue', 'Brown', 'Cyan', 'DarkBlue', 'Grey', 'Green', 'LightBlue', 'Lime', 'Magenta', 'Maroon', 'Olive', 'Orange', 'Purple', 'Red', 'Silver', 'White', 'Yellow']
    IN_COLOR_HTML = 'IN_COLOR_HTML'
    OUTPUT_HTML_FILE = 'OUTPUT_HTML_FILE'
    OUTPUT_JSON_FILE = 'OUTPUT_JSON_FILE'

    def __init__(self):
        super().__init__()
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

    @staticmethod
    def tr(string, context=''):
        if context == '':
            context = 'Processing'
        return QCoreApplication.translate(context, string)

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.PLOT_TYPE,
                self.tr('Plot type'),
                options=self.PLOT_TYPE_OPTIONS
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PLOT_TITLE,
                self.tr('Plot title'),
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.XFIELD,
                self.tr('X Field'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.YFIELD,
                self.tr('Y Field'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.IN_COLOR,
                self.tr('Color'),
                optional=True,
                options=self.IN_COLOR_OPTIONS
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.IN_COLOR_HTML,
                self.tr('Color (any valid HTML color) If set, this is used instead of the color set in the previous input.'),
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT_HTML_FILE,
                self.tr('HTML File'),
                self.tr('HTML files (*.html)')
            )
        )
        # need to add an output for it to allow to see it in Processus results viewer
        self.addOutput(QgsProcessingOutputHtml(self.OUTPUT_HTML_FILE, self.tr('Dataplotly - Generic plot HTML output')))

        # Add an file to return a response in JSON format
        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT_JSON_FILE,
                self.tr('JSON file'),
                self.tr('JSON Files (*.json)')
            )
        )
        # need to add an output for it to allow to see it in Processus results viewer
        self.addOutput(QgsProcessingOutputFile(self.OUTPUT_JSON_FILE, self.tr('Dataplotly - Generic plot JSON output')))


    def name(self):
        # Unique (non-user visible) name of algorithm
        return 'build_generic_plot'

    def displayName(self):
        # The name that the user will see in the toolbox
        return self.tr('Build a generic plot')

    def group(self):
        return self.tr('Plots')

    def groupId(self):
        return self.tr('plots')

    def processAlgorithm(self, parameters, context, feedback):
        """
        :param parameters:
        :param context:
        """

        layer = self.parameterAsSource(parameters, self.INPUT, context)
        fields = layer.fields()

        xfieldname = self.parameterAsString(parameters, self.XFIELD, context)
        yfieldname = self.parameterAsString(parameters, self.YFIELD, context)

        outputHtmlFile = self.parameterAsFileOutput(parameters, self.OUTPUT_HTML_FILE, context)
        outputJsonFile = self.parameterAsFileOutput(parameters, self.OUTPUT_JSON_FILE, context)

        plot_type = 'bar'
        plot_type_input = self.parameterAsInt(parameters, self.PLOT_TYPE, context)
        plot_type = self.PLOT_TYPE_OPTIONS[plot_type_input]

        plot_title = self.parameterAsString(parameters, self.PLOT_TITLE, context)

        in_color_input = self.parameterAsInt(parameters, self.IN_COLOR, context)
        in_color_hex = self.IN_COLOR_OPTIONS[in_color_input]
        in_color_html = self.parameterAsString(parameters, self.IN_COLOR_HTML, context)

        # Some controls
        msg = []
        if plot_type in self.X_MANDATORY and not xfieldname:
            msg.append(self.tr("The chosen plot type needs a X field !"))
        if plot_type in self.Y_MANDATORY and not yfieldname:
            msg.append(self.tr("The chosen plot type needs a Y field !"))
        if msg:
            feedback.reportError(' '.join(msg))
            raise QgsProcessingException(msg)

        # Build needed dictionary
        pdic = {}
        pdic['plot_type'] = plot_type
        pdic['plot_prop'] = {}

        # Add X dimension
        if xfieldname:
            # get field index for x
            idxX = layer.fields().lookupField(xfieldname)
            # get list of values for x
            x_var = [i[xfieldname] for i in layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([idxX]))]
            fieldTypeX = fields[idxX].type()
            x_title = fields[idxX].alias() or xfieldname
            pdic['plot_prop']['x'] = x_var

        # Add Y dimension
        if yfieldname:
            # get field index for y
            idxY = layer.fields().lookupField(yfieldname)
            # get list of values for y
            y_var = [i[yfieldname] for i in layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([idxY]))]
            y_title = fields[idxY].alias() or yfieldname
            pdic['plot_prop']['y'] = y_var


        # Draw only markers for scatter plot
        if plot_type in ['scatter', 'polar']:
            pdic['plot_prop']['marker'] = 'markers'

        # Colours
        pdic['plot_prop']['in_color'] = in_color_html or in_color_hex or 'DodgerBlue'

        # Add layout
        pdic['layout_prop'] = {
            'title': plot_title or layer.sourceName()
        }
        if plot_type in self.X_MANDATORY:
            pdic['layout_prop']['x_title'] = x_title
        if plot_type in self.Y_MANDATORY:
            pdic['layout_prop']['y_title'] = y_title

        # Add layer
        pdic['layer'] = layer

        # Create plot instance
        plot_instance = Plot(
            pdic['plot_type'],
            pdic["plot_prop"],
            pdic["layout_prop"]
        )

        # Initialize plot properties and build them
        trace = plot_instance.buildTrace()

        # Initialize layout properties and build them
        layout = plot_instance.buildLayout()

        # Prepare results
        results = {
            self.OUTPUT_HTML_FILE: None,
            self.OUTPUT_JSON_FILE: None
        }

        # Save plot as HTML
        if outputHtmlFile:
            standalone_plot_path = plot_instance.buildFigure()
            if os.path.isfile(standalone_plot_path):
                # html file output
                copyfile(standalone_plot_path, outputHtmlFile)
                results[self.OUTPUT_HTML_FILE] = outputHtmlFile


        # Save plot as JSON
        if outputJsonFile:
            ojson = {
                'data': trace,
                'layout': layout
            }
            with codecs.open(outputJsonFile, 'w', encoding='utf-8') as f:
                f.write(json.dumps(ojson))
                results[self.OUTPUT_JSON_FILE] = outputJsonFile

        return results

