"""
/***************************************************************************
 DataPlotly
                                 A QGIS plugin
 D3 Plots for QGIS
                              -------------------
        begin                : 2024-10-29
        git sha              : $Format:%H$
        copyright            : (C) 2024 by matteo ghetta
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

from collections import defaultdict

from qgis.core import (
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
    QgsProcessingParameterBoolean,
)

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

import pandas as pd
import plotly.express as px


class DataPlotlyProcessingPlot(QgsProcessingAlgorithm):
    """
    Create a generic plot framework for each plot in Processing
    """

    INPUT = "INPUT"
    XEXPRESSION = "XEXPRESSION"
    YEXPRESSION = "YEXPRESSION"
    OFFLINE = "OFFLINE"
    COLOR = "COLOR"
    SIZE = "SIZE"
    FACET_COL = "FACET_ROW"
    FACET_ROW = "FACET_COL"
    SHOW_LEGEND = 'SHOW_LEGEND'
    OUTPUT_HTML_FILE = "OUTPUT_HTML_FILE"
    OUTPUT_JSON_FILE = "OUTPUT_JSON_FILE"

    def __init__(self, plot_type):
        super().__init__()
        self.plot_type = plot_type

    def tr(self, string):
        return QCoreApplication.translate("DataPlotly", string)

    def createInstance(self):
        return DataPlotlyProcessingPlot()

    def name(self):
        return "dataplotly_plot_type"

    def displayName(self):
        return self.tr("Generic Plot Template")

    def group(self):
        return self.tr("Plots")

    def groupId(self):
        return "plots"

    def icon(self):
        return QIcon()

    def create_parameter_dictionary(self, plot_type):
        """
        Depending on the plot_type in input, returns a dictionary with a list as
        values of each parameter that will populate the Processing interface.

        This method is used in each subclasses in the initAlgorithm method

        Args:
            plot_type (str): string that describes the plot type (e.g. scatter)

        Returns:
            defaultdict(list): dictionary with keys = plot_type and values as a
            list of the parameters belonging to the plot type
        """
        # create the instance of the dictionary where key = 'scatter' and value = [param1, param2, etc]
        plot_types_dict = defaultdict(list)

        # common parameters between ALL plots
        input_layer = QgsProcessingParameterFeatureSource(
            self.INPUT, self.tr("Input layer")
        )
        x_field = QgsProcessingParameterExpression(
            self.XEXPRESSION,
            self.tr("X Field"),
            parentLayerParameterName=self.INPUT,
        )
        y_field = QgsProcessingParameterExpression(
            self.YEXPRESSION,
            self.tr("Y Field"),
            parentLayerParameterName=self.INPUT,
        )

        offline_param = QgsProcessingParameterBoolean(
            self.OFFLINE, self.tr("Complete offline usage"), defaultValue=False
        )
        offline_param.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)

        output_html = QgsProcessingParameterFileDestination(
            self.OUTPUT_HTML_FILE,
            self.tr("Scatter Plot"),
            self.tr("HTML files (*.html)"),
        )

        output_json = QgsProcessingParameterFileDestination(
            self.OUTPUT_JSON_FILE,
            self.tr("JSON file"),
            self.tr("JSON Files (*.json)"),
            createByDefault=False,
            optional=True,
        )

        # scatter
        size_param = QgsProcessingParameterNumber(
            self.SIZE, self.tr("Marker size"), defaultValue=10
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

        # scatter
        color_param = QgsProcessingParameterColor(
            self.COLOR, self.tr("Color"), optional=True, defaultValue="#8ebad9"
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

        # scatter
        facet_row = QgsProcessingParameterExpression(
            self.FACET_ROW, self.tr("Facet row"), parentLayerParameterName=self.INPUT
        )
        facet_row.setFlags(
            QgsProcessingParameterDefinition.FlagAdvanced
            | QgsProcessingParameterDefinition.FlagOptional
        )

        # scatter
        facet_col = QgsProcessingParameterExpression(
            self.FACET_COL,
            self.tr("Facet col"),
            optional=True,
            parentLayerParameterName=self.INPUT,
        )
        facet_col.setFlags(
            QgsProcessingParameterDefinition.FlagAdvanced
            | QgsProcessingParameterDefinition.FlagOptional
        )

        show_legend = QgsProcessingParameterBoolean(
            self.SHOW_LEGEND, self.tr("Show Legend"), True
        )


        # add to the dictionary the list of the common parameters
        plot_types_dict[plot_type].append(input_layer)
        plot_types_dict[plot_type].append(x_field)
        plot_types_dict[plot_type].append(y_field)
        plot_types_dict[plot_type].append(offline_param)
        plot_types_dict[plot_type].append(output_html)
        plot_types_dict[plot_type].append(output_json)
        plot_types_dict[plot_type].append(color_param)
        plot_types_dict[plot_type].append(facet_row)
        plot_types_dict[plot_type].append(facet_col)
        plot_types_dict[plot_type].append(show_legend)

        # add the parameter depending on the plot type
        if plot_type in ("scatter"):
            plot_types_dict[plot_type].append(size_param)

        return plot_types_dict[plot_type]

    def create_plot(self, plot_type, df, plot_parameters):
        """
        Creates the figure plotly object giving the plot_type, pandas dataframe
        and the plot_parameters dictionary

        Args:
            plot_type (str): plot type string (e.g. scatter)
            df (pandas Dataframe): pandas dataframe created in the processAlgorithm
            Processing method
            plot_parameters (dict): dictionary of the plot parameters built in the
            processAlgorithm method (e.g. plot_params = {"x": "x", "y": "y)

        Returns:
            plotly Figure: fig object created by plotly.express
        """

        # use the getattr method of pass to px the correct plot type (to have like px.scatter, px.bar, etc)
        plot_function = getattr(px, plot_type)

        # create the plotly object depending on the plot type and the plot parameters dictionary
        fig = plot_function(df, **plot_parameters)

        return fig

    def update_plot(self, fig, update_parameters):
        """
        Method needed to update the existing figure created by the create_plot
        method. This method is called AFTER the create_plot one and updates
        the figure object and returns the updated one

        Args:
            fig (plotly Figure): the existing and valid plotly Figure object to
            update
            update_parameters (defaultdict): dictionary with the parameters to update

        Returns:
            plotly Figure: the updated Figure object
        """

        # extract the sub dict of the plot_type
        update_params = update_parameters[self.plot_type]

        # update the figure object
        fig.update_traces(**update_params)

        return fig

    def processAlgorithm(self, parameters, context, feedback):

        source = self.parameterAsSource(parameters, self.INPUT, context)

        expressionContext = self.createExpressionContext(parameters, context, source)

        x_expression = self.parameterAsString(parameters, self.XEXPRESSION, context)
        x_expression = QgsExpression(x_expression)

        if x_expression.hasParserError():
            x_expression.prepare(expressionContext)
            raise QgsProcessingException(x_expression.parserErrorString())

        y_expression = self.parameterAsString(parameters, self.YEXPRESSION, context)
        y_expression = QgsExpression(y_expression)

        if y_expression.hasParserError():
            y_expression.prepare(expressionContext)
            raise QgsProcessingException(y_expression.parserErrorString())

        size = self.parameterAsDouble(parameters, self.SIZE, context)
        size_property = None
        if QgsProcessingParameters.isDynamic(parameters, "SIZE"):
            size_property = parameters["SIZE"]

        color = self.parameterAsColor(parameters, self.COLOR, context)
        color_property = None
        if QgsProcessingParameters.isDynamic(parameters, "COLOR"):
            color_property = parameters["COLOR"]

        facet_row = self.parameterAsString(parameters, self.FACET_ROW, context)
        facet_row_expression = QgsExpression(facet_row)

        if facet_row and facet_row_expression.hasParserError():
            facet_row_expression.prepare(expressionContext)
            raise QgsProcessingException(facet_row_expression.parserErrorString())

        facet_col = self.parameterAsString(parameters, self.FACET_COL, context)
        facet_col_expression = QgsExpression(facet_col)

        if facet_col and facet_col_expression.hasParserError():
            facet_col_expression.prepare(expressionContext)
            raise QgsProcessingException(facet_col_expression.parserErrorString())

        offline = self.parameterAsBool(parameters, self.OFFLINE, context)
        if offline is not True:
            offline = "cdn"

        show_legend = self.parameterAsBool(parameters, self.SHOW_LEGEND, context)
        feedback.pushDebugInfo(f"{show_legend}")

        output_html = self.parameterAsFileOutput(
            parameters, self.OUTPUT_HTML_FILE, context
        )

        output_json = self.parameterAsFileOutput(
            parameters, self.OUTPUT_JSON_FILE, context
        )

        # start building the object to create the pandas dataframe
        colnames = ["x", "y", "customdata"]
        data = []

        request = QgsFeatureRequest()
        request.setFlags(QgsFeatureRequest.NoGeometry)

        total = 100 / source.featureCount() if source else 0

        for current, f in enumerate(source.getFeatures(request)):

            # temporary list
            tl = []

            expressionContext.setFeature(f)

            x_val = x_expression.evaluate(expressionContext)
            y_val = y_expression.evaluate(expressionContext)
            ids = f.id()

            tl.append(x_val)
            tl.append(y_val)
            tl.append(ids)

            if facet_row:
                facet_row_val = facet_row_expression.evaluate(expressionContext)
                tl.append(facet_row_val)

            if facet_col:
                facet_col_val = facet_col_expression.evaluate(expressionContext)
                tl.append(facet_col_val)

            if size_property:
                the_size, _ = size_property.valueAsDouble(expressionContext, size)
                tl.append(the_size)

            if color_property:
                the_color, _ = color_property.value(expressionContext, color)
                tl.append(the_color)

            # list of list that we can convert immediately in a dataframe
            data.append(tl)

            feedback.setProgress(int(total * current))

        # if additional parameters are set, add them to as column names
        if facet_row:
            colnames.append("facet_row")

        if facet_col:
            colnames.append("facet_col")

        if size_property:
            colnames.append("size")

        if color_property:
            colnames.append("color")

        # create the dataframe
        df = pd.DataFrame(data=data, columns=colnames)

        # generic plot parameters (for all plot types)
        plot_params = {
            "x": "x",
            "y": "y",
            "color": "color" if color_property else None,
            "facet_row": "facet_row" if facet_row else None,
            "facet_col": "facet_col" if facet_col else None,
        }

        # initialize the updating dictionary (different depending on the plot parameters)
        fig_update_params = defaultdict(dict)

        # only if scatter
        if self.plot_type in ('scatter'):
            if size_property:
                plot_params["size"] = "size"
            else:
                fig_update_params[self.plot_type]["marker_size"] = size

        if color_property is None:
            fig_update_params[self.plot_type]["marker_color"] = color.name()

        # call the methods to create and update the figure
        fig = self.create_plot(self.plot_type, df, plot_params)
        fig = self.update_plot(fig, fig_update_params)

        # add the legend
        fig.update_layout(showlegend=show_legend)

        feedback.pushDebugInfo(f"{fig}")

        # result dictionary
        results = {}

        fig.write_html(output_html, include_plotlyjs=offline)
        results[self.OUTPUT_HTML_FILE] = output_html

        if output_json:
            fig.write_json(output_json, pretty=True)
            results[self.OUTPUT_JSON_FILE] = output_json

        return results
