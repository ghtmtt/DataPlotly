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


from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterExpression,
    QgsProcessingParameterNumber,
    QgsExpression,
    QgsProcessingParameters,
    QgsProcessingException,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterColor,
    QgsProcessingAlgorithm,
    QgsFeatureRequest,
    QgsPropertyDefinition,
    QgsProcessingParameterBoolean
)

from qgis.PyQt.QtCore import QCoreApplication

import pandas as pd
import plotly.express as px


class DataPlotlyProcessingScatterPlot(QgsProcessingAlgorithm):
    """
    Create a scatter with DataPlotly plugin
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    XEXPRESSION = 'XEXPRESSION'
    YEXPRESSION = 'YEXPRESSION'
    OFFLINE = 'OFFLINE'
    COLOR = 'COLOR'
    SIZE = 'SIZE'
    OUTPUT_HTML_FILE = 'OUTPUT_HTML_FILE'
    OUTPUT_JSON_FILE = 'OUTPUT_JSON_FILE'

    def tr(self, string):
        return QCoreApplication.translate('DataPlotly', string)

    def createInstance(self):
        return DataPlotlyProcessingScatterPlot()

    def initAlgorithm(self, config=None):

        # layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer')
            )
        )

        # x fields (or expression)
        self.addParameter(
            QgsProcessingParameterExpression(
                self.XEXPRESSION,
                self.tr('X Field'),
                parentLayerParameterName=self.INPUT
            )
        )

        # y field (or expression)
        self.addParameter(
            QgsProcessingParameterExpression(
                self.YEXPRESSION,
                self.tr('Y Field'),
                parentLayerParameterName=self.INPUT
            )
        )

        # size
        size_param = QgsProcessingParameterNumber(
            self.SIZE,
            self.tr('Marker size'),
            defaultValue=10
        )
        size_param.setIsDynamic(True)
        size_param.setDynamicLayerParameterName(self.INPUT)
        size_param.setDynamicPropertyDefinition(
            QgsPropertyDefinition(
                "SIZE",
                self.tr("Size"),
                QgsPropertyDefinition.Double,
            )
        )
        self.addParameter(size_param)

        # color
        color_param = QgsProcessingParameterColor(
            self.COLOR,
            self.tr('Color'),
            optional=True,
            defaultValue='#8ebad9'
        )
        color_param.setIsDynamic(True)
        color_param.setDynamicLayerParameterName(self.INPUT)
        color_param.setDynamicPropertyDefinition(
            QgsPropertyDefinition(
                "COLOR",
                self.tr("Color"),
                QgsPropertyDefinition.Double,
            )
        )
        self.addParameter(color_param)


        # offline parameter
        offline_param = QgsProcessingParameterBoolean(
            self.OFFLINE,
            self.tr('Complete offline usage'),
            defaultValue=False
        )
        offline_param.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(offline_param)


        # html file output
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_HTML_FILE, 
                self.tr('Scatter Plot'),
                self.tr('HTML files (*.html)')
            )
        )

        # json file output
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_JSON_FILE,
                self.tr('JSON file'),
                self.tr('JSON Files (*.json)'),
                createByDefault=False
            )
        )

    def name(self):
        # Unique (non-user visible) name of algorithm
        return 'dataplotly_scatterplot'

    def displayName(self):
        # The name that the user will see in the toolbox
        return self.tr('Scatter Plot')

    def group(self):
        return self.tr('Plots')

    def groupId(self):
        return 'plots'

    def type_name(self):
        return 'scatter'

    def processAlgorithm(self, parameters, context, feedback):

        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        expressionContext = self.createExpressionContext(
            parameters,
            context,
            source
        )

        x_expression = self.parameterAsString(
            parameters,
            self.XEXPRESSION, 
            context
        )
        x_expression = QgsExpression(x_expression)

        if x_expression.hasParserError():
            x_expression.prepare(expressionContext)
            raise QgsProcessingException(x_expression.parserErrorString())
        
        y_expression = self.parameterAsString(
            parameters,
            self.YEXPRESSION, 
            context
        )
        y_expression = QgsExpression(y_expression)

        if y_expression.hasParserError():
            y_expression.prepare(expressionContext)
            raise QgsProcessingException(y_expression.parserErrorString())


        size = self.parameterAsDouble(
            parameters,
            self.SIZE,
            context
        )
        size_property = None
        if QgsProcessingParameters.isDynamic(parameters, "SIZE"):
            size_property = parameters["SIZE"]

        color = self.parameterAsColor(
            parameters,
            self.COLOR,
            context
        )
        color_property = None
        if QgsProcessingParameters.isDynamic(parameters, "COLOR"):
            color_property = parameters["COLOR"]
        
        offline = self.parameterAsBool(
            parameters,
            self.OFFLINE,
            context
        )
        if offline is not True:
            offline='cdn'

        output_html = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT_HTML_FILE,
            context
        )

        output_json = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT_JSON_FILE,
            context
        )


        colnames = ['x', 'y', 'customdata']
        data = []

        request = QgsFeatureRequest()
        request.setFlags(QgsFeatureRequest.NoGeometry)

        for current, f in enumerate(source.getFeatures(request)):

            tl = []

            expressionContext.setFeature(f)

            x_val = x_expression.evaluate(expressionContext)
            y_val = y_expression.evaluate(expressionContext)
            ids = f.id()

            tl.append(x_val)
            tl.append(y_val)
            tl.append(ids)

            if size_property:
                the_size, _ = size_property.valueAsDouble(expressionContext, size)
                tl.append(the_size)

            if color_property:
                the_color, _ = color_property.value(expressionContext, color)
                tl.append(the_color)

            data.append(tl)


        if size_property:
            colnames.append('size')
        
        if color_property:
            colnames.append('color')
        
        df = pd.DataFrame(data=data, columns=colnames)

        feedback.pushDebugInfo(f'{df}')

        # print(df)
        fig = px.scatter(
            df,
            x='x',
            y='y',
            size='size' if size_property else None,
            color='color' if color_property else None
        )

        if size_property is None:
            fig.update_traces(marker_size=size)

        if color_property is None:
            fig.update_traces(marker_color=color.name())
        
        fig.update_layout(showlegend=True)

        fig.write_html(output_html, include_plotlyjs=offline)
        fig.write_json(output_json, pretty=True)

        results = {}

        results[self.OUTPUT_HTML_FILE] =  output_html
        results[self.OUTPUT_JSON_FILE] = output_json

        return results
