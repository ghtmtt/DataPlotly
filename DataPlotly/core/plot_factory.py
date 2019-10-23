# -*- coding: utf-8 -*-
"""
Plot creation

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import tempfile
import os
import re
import plotly
import plotly.graph_objs as go
from plotly import tools

from qgis.core import (
    QgsProject,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsFeatureRequest,
    NULL,
    QgsReferencedRectangle,
    QgsCoordinateTransform,
    QgsExpressionContextGenerator,
    QgsProperty
)
from qgis.PyQt.QtCore import (
    QUrl,
    QObject,
    pyqtSignal
)
from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.core.plot_types.plot_type import PlotType
from DataPlotly.core.plot_types import *  # pylint: disable=W0401,W0614


class PlotFactory(QObject):  # pylint:disable=too-many-instance-attributes
    """
    Plot factory which creates Plotly Plot objects

    Console usage:

    .. code-block:: python
        # create (and customize) plot settings, where
        # plot_type (string): 'scatter'
        # plot_properties (dictionary): {'x':[1,2,3], 'marker_width': 10}
        # layout_properties (dictionary): {'legend'; True, 'title': 'Plot Title'}
        settings = PlotSettings(plot_type, plot_properties, layout_properties)
        # create the factory, which will create plots using the specified settings
        factory = PlotFactory(settings)
        # Use the factory to build a plot
        output_file_path = factory.build_figure()
    """

    # create fixed class variables as paths for local javascript files
    POLY_FILL_PATH = QUrl.fromLocalFile(
        os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'jsscripts/polyfill.min.js'))).toString()
    PLOTLY_PATH = QUrl.fromLocalFile(
        os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'jsscripts/plotly-1.34.0.min.js'))).toString()

    PLOT_TYPES = {
        t.type_name(): t for t in PlotType.__subclasses__()
    }

    plot_built = pyqtSignal()

    def __init__(self, settings: PlotSettings = None, context_generator: QgsExpressionContextGenerator = None,
                 visible_region: QgsReferencedRectangle = None):
        super().__init__()
        if settings is None:
            settings = PlotSettings('scatter')

        self.settings = settings
        self.context_generator = context_generator
        self.raw_plot = None
        self.plot_path = None
        self.selected_features_only = self.settings.properties['selected_features_only']
        self.visible_features_only = self.settings.properties.get('visible_features_only', False)
        self.visible_region = visible_region
        self.trace = None
        self.layout = None
        self.source_layer = QgsProject.instance().mapLayer(
            self.settings.source_layer_id) if self.settings.source_layer_id else None

        self.rebuild()

        if self.source_layer:
            self.source_layer.layerModified.connect(self.rebuild)
            if self.selected_features_only:
                self.source_layer.selectionChanged.connect(self.rebuild)

    def fetch_values_from_layer(self):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """
        (Re)fetches plot values from the source layer.
        """

        # Note: we keep things nice and efficient and only iterate a single time over the layer!

        if not self.context_generator:
            context = QgsExpressionContext()
            context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(self.source_layer))
        else:
            context = self.context_generator.createExpressionContext()

        def add_source_field_or_expression(field_or_expression):
            field_index = self.source_layer.fields().lookupField(field_or_expression)
            if field_index == -1:
                expression = QgsExpression(field_or_expression)
                if not expression.hasParserError():
                    expression.prepare(context)
                return expression, expression.needsGeometry(), expression.referencedColumns()

            return None, False, {field_or_expression}

        x_expression, x_needs_geom, x_attrs = add_source_field_or_expression(self.settings.properties['x_name']) if \
            self.settings.properties[
            'x_name'] else (None, False, set())
        y_expression, y_needs_geom, y_attrs = add_source_field_or_expression(self.settings.properties['y_name']) if \
            self.settings.properties[
            'y_name'] else (None, False, set())
        z_expression, z_needs_geom, z_attrs = add_source_field_or_expression(self.settings.properties['z_name']) if \
            self.settings.properties[
            'z_name'] else (None, False, set())
        additional_info_expression, additional_needs_geom, additional_attrs = add_source_field_or_expression(
            self.settings.layout['additional_info_expression']) if self.settings.layout[
            'additional_info_expression'] else (None, False, set())

        attrs = set().union(x_attrs, y_attrs, z_attrs, additional_attrs)

        request = QgsFeatureRequest()

        if self.settings.filter_property.isActive():
            expression = self.settings.filter_property.asExpression()
            request.setFilterExpression(expression)
            request.setExpressionContext(context)

        request.setSubsetOfAttributes(attrs, self.source_layer.fields())

        if not x_needs_geom and not y_needs_geom and not z_needs_geom and not additional_needs_geom:
            request.setFlags(QgsFeatureRequest.NoGeometry)

        if self.visible_features_only and self.visible_region is not None:
            ct = QgsCoordinateTransform(self.visible_region.crs(), self.source_layer.crs(),
                                        QgsProject.instance().transformContext())
            rect = ct.transformBoundingBox(self.visible_region)
            request.setFilterRect(rect)

        if self.selected_features_only:
            it = self.source_layer.getSelectedFeatures(request)
        else:
            it = self.source_layer.getFeatures(request)

        xx = []
        yy = []
        zz = []
        additional_hover_text = []
        for f in it:
            self.settings.feature_ids.append(f.id())
            context.setFeature(f)

            x = None
            if x_expression:
                x = x_expression.evaluate(context)
                if x == NULL or x is None:
                    continue
            elif self.settings.properties['x_name']:
                x = f[self.settings.properties['x_name']]
                if x == NULL or x is None:
                    continue

            y = None
            if y_expression:
                y = y_expression.evaluate(context)
                if y == NULL or y is None:
                    continue
            elif self.settings.properties['y_name']:
                y = f[self.settings.properties['y_name']]
                if y == NULL or y is None:
                    continue

            z = None
            if z_expression:
                z = z_expression.evaluate(context)
                if z == NULL or z is None:
                    continue
            elif self.settings.properties['z_name']:
                z = f[self.settings.properties['z_name']]
                if z == NULL or z is None:
                    continue

            if additional_info_expression:
                additional_hover_text.append(additional_info_expression.evaluate(context))
            elif self.settings.layout['additional_info_expression']:
                additional_hover_text.append(f[self.settings.layout['additional_info_expression']])

            if x is not None:
                xx.append(x)
            if y is not None:
                yy.append(y)
            if z is not None:
                zz.append(z)

        self.settings.additional_hover_text = additional_hover_text
        self.settings.x = xx
        self.settings.y = yy
        self.settings.z = zz

    def set_visible_region(self, region: QgsReferencedRectangle):
        """
        Sets the visible region associated with the factory, possibly triggering a rebuild
        of a filtered plot
        """
        if self.visible_features_only:
            self.visible_region = region
            self.rebuild()

    def rebuild(self):
        """
        Rebuilds the plot, re-fetching current values from the layer
        """
        if self.source_layer:
            self.fetch_values_from_layer()

        self.trace = self._build_trace()
        self.layout = self._build_layout()
        self.plot_built.emit()

    def _build_trace(self):
        """
        Builds the final trace calling the go.xxx plotly method
        this method here is the one performing the real job

        From the initial object created (e.g. p = Plot(plot_type, plot_properties,
        layout_properties)) this methods checks the plot_type and elaborates the
        plot_properties dictionary passed

        :return: the final Plot Trace (final Plot object, AKA go.xxx plot type)
        """
        assert self.settings.plot_type in PlotFactory.PLOT_TYPES

        return PlotFactory.PLOT_TYPES[self.settings.plot_type].create_trace(self.settings)

    def _build_layout(self):
        """
        Builds the final layout calling the go.Layout plotly method

        From the initial object created (e.g. p = Plot(plot_type, plot_properties,
        layout_properties)) this methods checks the plot_type and elaborates the
        layout_properties dictionary passed

        :return: the final Plot Layout (final Layout object, AKA go.Layout)
        """
        assert self.settings.plot_type in PlotFactory.PLOT_TYPES

        return PlotFactory.PLOT_TYPES[self.settings.plot_type].create_layout(self.settings)

    @staticmethod
    def js_callback(_):
        """
        Returns a string that is added to the end of the plot. This string is
        necessary for the interaction between plot and map objects

        WARNING! The string ReplaceTheDiv is a default string that will be
        replaced in a second moment
        """

        js_str = '''
        <script>
        // additional js function to select and click on the data
        // returns the ids of the selected/clicked feature

        var plotly_div = document.getElementById('ReplaceTheDiv')
        var plotly_data = plotly_div.data

        // selecting function
        plotly_div.on('plotly_selected', function(data){
        var dds = {};
        dds["mode"] = 'selection'
        dds["type"] = data.points[0].data.type

        featureIds = [];
        featureIdsTernary = [];

        data.points.forEach(function(pt){
        featureIds.push(parseInt(pt.id))
        featureIdsTernary.push(parseInt(pt.pointNumber))
        dds["id"] = featureIds
        dds["tid"] = featureIdsTernary
            })
        //console.log(dds)
        window.status = JSON.stringify(dds)
        })

        // clicking function
        plotly_div.on('plotly_click', function(data){
        var featureIds = [];
        var dd = {};
        dd["fidd"] = data.points[0].id
        dd["mode"] = 'clicking'

        // loop and create dictionary depending on plot type
        for(var i=0; i < data.points.length; i++){

        // scatter plot
        if(data.points[i].data.type == 'scatter'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type

            data.points.forEach(function(pt){
            dd["fid"] = pt.id
            })
        }

        // pie

        else if(data.points[i].data.type == 'pie'){
          dd["type"] = data.points[i].data.type
          dd["label"] = data.points[i].label
          dd["field"] = data.points[i].data.name
          console.log(data.points[i].label)
          console.log(data.points[i])
        }

        // histogram
        else if(data.points[i].data.type == 'histogram'){
            dd["type"] = data.points[i].data.type
            dd["uid"] = data.points[i].data.uid
            dd["field"] = data.points[i].data.name

            // correct axis orientation
            if(data.points[i].data.orientation == 'v'){
                dd["id"] = data.points[i].x
                dd["bin_step"] = data.points[i].data.xbins.size
            }
            else {
                dd["id"] = data.points[i].y
                dd["bin_step"] = data.points[i].data.ybins.size
            }
        }

        // box plot
        else if(data.points[i].data.type == 'box'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type
            dd["field"] = data.points[i].data.customdata[0]

                // correct axis orientation
                if(data.points[i].data.orientation == 'v'){
                    dd["id"] = data.points[i].x
                }
                else {
                    dd["id"] = data.points[i].y
                }
            }

        // violin plot
        else if(data.points[i].data.type == 'violin'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type
            dd["field"] = data.points[i].data.customdata[0]

                // correct axis orientation (for violin is viceversa)
                if(data.points[i].data.orientation == 'v'){
                    dd["id"] = data.points[i].x
                }
                else {
                    dd["id"] = data.points[i].y
                }
            }

        // bar plot
        else if(data.points[i].data.type == 'bar'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type
            dd["field"] = data.points[i].data.customdata[0]

                // correct axis orientation
                if(data.points[i].data.orientation == 'v'){
                    dd["id"] = data.points[i].x
                }
                else {
                    dd["id"] = data.points[i].y
                }
            }

        // ternary
        else if(data.points[i].data.type == 'scatterternary'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type
            dd["field"] = data.points[i].data.customdata
            dd["fid"] = data.points[i].pointNumber
            }

            }
        window.status = JSON.stringify(dd)
        });
        </script>'''

        return js_str

    def build_html(self, config) -> str:
        """
        Creates the HTML for the plot

        Calls the go.Figure plotly method and builds the figure object adjust the
        html file and add some line (including the js_string for the interaction)
        save the html plot file in a temporary directory and return the path
        that can be loaded in the QWebView

        This method is directly usable after the plot object has been created and
        the 2 methods (buildTrace and buildLayout) have been called

        params:
            config (dict): config = {'scrollZoom': True, 'editable': False}

        config argument is necessary to specify which buttons should appear in
        the plotly toolbar, if the user can edit the plot inline, etc.
        With this parameter is possible to hide the toolbar only in print layouts
        and not in the normal plot canvas.

        :return: the final html content representing the plot

        Console usage:
        .. code-block:: python
            # create the initial object
            settings = PlotSettings(plot_type, plot_properties, layout_properties)
            factory = PlotFactory(settings)
            # finally create the Figure
            html_content  = factory.build_html()
        """
        fig = go.Figure(data=self.trace, layout=self.layout)

        # first lines of additional html with the link to the local javascript
        raw_plot = '<head><meta charset="utf-8" /><script src="{}">' \
                   '</script><script src="{}"></script></head>'.format(
            self.POLY_FILL_PATH, self.PLOTLY_PATH)
        # set some configurations
        # call the plot method without all the javascript code
        raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False, show_link=False,
                                        config=config)
        # insert callback for javascript events
        raw_plot += self.js_callback(raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search(r'Plotly.newPlot\(\s*[\'"](.+?)[\'"]', raw_plot)
        substr = match.group(1)
        raw_plot = raw_plot.replace('ReplaceTheDiv', substr)
        return raw_plot

    def build_figure(self) -> str:
        """
        Creates the final plot (single plot)

        Calls the go.Figure plotly method and builds the figure object adjust the
        html file and add some line (including the js_string for the interaction)
        save the html plot file in a temporary directory and return the path
        that can be loaded in the QWebView

        This method is directly usable after the plot object has been created and
        the 2 methods (buildTrace and buildLayout) have been called

        :return: the final html path containing the plot

        Console usage:
        .. code-block:: python
            # create the initial object
            settings = PlotSettings(plot_type, plot_properties, layout_properties)
            factory = PlotFactory(settings)
            # finally create the Figure
            path_to_output = factory.build_figure()
        """

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        config = {
            'scrollZoom': True,
            'editable': True,
            'modeBarButtonsToRemove': ['toImage', 'sendDataToCloud', 'editInChartStudio']
        }

        with open(self.plot_path, "w") as f:
            f.write(self.build_html(config))

        return self.plot_path

    def build_figures(self, plot_type, ptrace) -> str:
        """
        Overlaps plots on the same map canvas

        params:
            plot_type (string): 'scatter'
            ptrace (list of Plot Traces): list of all the different Plot Traces

        plot_type argument in necessary for Bar and Histogram plots when the
        options stack is chosen.
        In this case the layouts of the firsts plot are deleted and only the last
        one is taken into account (so to have the stack option).

        self.layout is DELETED, so the final layout is taken from the LAST plot
        configuration added

        :return: the final html path containing the plot with the js_string for
        the interaction

        Console usage:
        .. code-block:: python
            # create the initial object
            settings = PlotSettings(plot_type, plot_properties, layout_properties)
            factory = PlotFactory(settings)
            # finally create the Figures
            path_to_output = factory.build_figures(plot_type, ptrace)
        """

        # assign the variables from the kwargs arguments
        # plot_type = kwargs['plot_type']
        # ptrace = kwargs['pl']

        # check if the plot type and render the correct figure
        if plot_type == 'bar' or 'histogram':
            del self.layout
            self.layout = go.Layout(
                barmode=self.settings.layout['bar_mode']
            )
            figures = go.Figure(data=ptrace, layout=self.layout)

        else:
            figures = go.Figure(data=ptrace, layout=self.layout)

        # set some configurations
        config = {'scrollZoom': True, 'editable': True}
        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}">' \
                        '</script><script src="{}"></script></head>'.format(
            self.POLY_FILL_PATH, self.PLOTLY_PATH)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(figures, output_type='div', include_plotlyjs=False, show_link=False,
                                             config=config)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search(r'Plotly.newPlot\(\s*[\'"](.+?)[\'"]', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path

    def build_sub_plots(self, grid, row, column, ptrace):  # pylint:disable=too-many-arguments
        """
        Draws plot in different plot canvases (not overlapping)

        params:
            grid (string): 'row' or 'col'. Plot are created in rows or columns
            row (int): number of rows (if row is selected)
            column (int): number of columns (if column is selected)
            ptrace (list of Plot Traces): list of all the different Plot Traces

        :return: the final html path containing the plot with the js_string for
        the interaction

        Console usage:
        .. code-block:: python
            # create the initial object
            settings = PlotSettings(plot_type, plot_properties, layout_properties)
            factory = PlotFactory(settings)
            # finally create the Figures
            path_to_output = factory.build_sub_plots('row', 1, gr, pl, tt)
        """

        if grid == 'row':

            fig = tools.make_subplots(rows=row, cols=column)

            for i, itm in enumerate(ptrace):
                fig.append_trace(itm, row, i + 1)

        elif grid == 'col':

            fig = tools.make_subplots(rows=row, cols=column)

            for i, itm in enumerate(ptrace):
                fig.append_trace(itm, i + 1, column)

        # set some configurations
        config = {'scrollZoom': True, 'editable': True}
        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}"></script>' \
                        '<script src="{}"></script></head>'.format(
            self.POLY_FILL_PATH, self.PLOTLY_PATH)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False, show_link=False,
                                             config=config)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search(r'Plotly.newPlot\("([^"]+)', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path
