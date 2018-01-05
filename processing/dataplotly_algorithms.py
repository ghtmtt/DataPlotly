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

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from DataPlotly.data_plotly_plot import *

from qgis.utils import plugins
from qgis.core import (QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingUtils,
                       QgsProcessingParameterFileDestination,
                       QgsSettings,
                       QgsFeatureRequest)

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
    PLOT_TYPE_OPTIONS = ['bar', 'pie', 'scatter', 'histogram']
    XFIELD = 'XFIELD'
    YFIELD = 'YFIELD'
    OUTPUT_HTML_FILE = 'OUTPUT_HTML_FILE'
    OUTPUT_JSON_FILE = 'OUTPUT_JSON_FILE'

    def __init__(self):
        super().__init__()
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

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
                self.tr('Plot title')
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.XFIELD,
                self.tr('X attribute'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.YFIELD,
                self.tr('Y attribute'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT_HTML_FILE,
                self.tr('HTML File'),
                self.tr('HTML files (*.html)')
            )
        )
        # no need to add an output for it, it is made automatically

        # Add an file to return a response in JSON format
        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT_JSON_FILE,
                self.tr('JSON file'),
                self.tr('JSON Files (*.json)')
            )
        )


    def name(self):
        # Unique (non-user visible) name of algorithm
        return 'build_simple_plot'

    def displayName(self):
        # The name that the user will see in the toolbox
        return self.tr('Build simple plot')

    def group(self):
        return self.tr('Plots')

    def processAlgorithm(self, parameters, context, feedback):
        """
        :param parameters:
        :param context:
        """

        layer = self.parameterAsSource(parameters, self.INPUT, context)
        xfieldname = self.parameterAsString(parameters, self.XFIELD, context)
        yfieldname = self.parameterAsString(parameters, self.YFIELD, context)
        outputHtmlFile = self.parameterAsFileOutput(parameters, self.OUTPUT_HTML_FILE, context)
        outputJsonFile = self.parameterAsFileOutput(parameters, self.OUTPUT_JSON_FILE, context)
        plot_type = 'bar'
        plot_type_input = self.parameterAsInt(parameters, self.PLOT_TYPE, context)
        plot_type = self.PLOT_TYPE_OPTIONS[plot_type_input]
        plot_title = self.parameterAsString(parameters, self.PLOT_TITLE, context)
        fields = layer.fields()

        # get field index for x
        idxX = layer.fields().lookupField(xfieldname)
        # get list of values for x
        x_var = [i[xfieldname] for i in layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([idxX]))]
        fieldTypeX = fields[idxX].type()

        # get field index for y
        idxY = layer.fields().lookupField(yfieldname)
        # get list of values for y
        y_var = [i[yfieldname] for i in layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([idxY]))]

        # Build needed dictionary
        pdic = {}
        pdic['plot_type'] = plot_type
        pdic['plot_prop'] = {
            'x': x_var,
            'y': y_var
        }

        pdic['layout_prop'] = {
            'title': plot_title
        }
        pdic['layer'] = layer

        # create Plot instance
        plot_instance = Plot(
            pdic['plot_type'],
            pdic["plot_prop"],
            pdic["layout_prop"]
        )

        # initialize plot properties and build them
        trace = plot_instance.buildTrace()

        # initialize layout properties and build them
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

