import plotly
import plotly.graph_objs as go
from plotly import tools
from .plot_web_view import plotWebView


class Plot(object):

    plot_type = ''

    plot_properties = {}

    plot_layout = {}


    def buildProperties(self, *args, **kwargs):
        '''
        dictionary with all the plot properties
        '''

        for k, v in kwargs.items():
            self.plot_properties[k] = v

        return self.plot_properties


    def buildTrace(self, plot_type):
        '''
        build the Trace that will be plotted depensing on the plot type
        this method here is the one performing the real job
        '''

        self.plot_type = plot_type

        if plot_type == 'scatter':
            self.trace = [go.Scatter(
            x = self.plot_properties['x'],
            y = self.plot_properties['y'],
            mode = self.plot_properties['marker'],
            name = self.plot_properties['y_name'],
            marker = dict(
                color = self.plot_properties['in_color'],
                size = self.plot_properties['marker_size'],
                line = dict(
                    color = self.plot_properties['out_color'],
                    width = self.plot_properties['marker_width']
                    )
                ),
            line = dict(
                color = self.plot_properties['in_color'],
                width = self.plot_properties['marker_width']
                ),
            opacity = self.plot_properties['opacity']
            )]

        elif plot_type == 'box':

            # NULL value in the Field is empty
            if not self.plot_properties['x']:
                self.plot_properties['x'] = None

            # flip the variables according to the box orientation
            if self.plot_properties['box_orientation'] == 'h':
                self.plot_properties['x'], self.plot_properties['y'] = self.plot_properties['y'], self.plot_properties['x']

            self.trace = [go.Box(
                x = self.plot_properties['x'],
                y = self.plot_properties['y'],
                name = self.plot_properties['y_name'],
                boxmean = self.plot_properties['box_stat'],
                orientation = self.plot_properties['box_orientation'],
                boxpoints = self.plot_properties['box_outliers'],
                fillcolor = self.plot_properties['in_color'],
                line = dict(
                    color = self.plot_properties['out_color'],
                    width = self.plot_properties['marker_width']
                    ),
                opacity = self.plot_properties['opacity']
            )]


        return self.trace


    def layoutProperties(self, *args, **kwargs):
        '''
        build the layout customizations
        '''

        for k, v in kwargs.items():
            self.plot_layout[k] = v

        return self.plot_layout


    def buildLayout(self):

        self.layout = go.Layout(
            showlegend = self.plot_layout['legend'],
            title = self.plot_layout['title']
        )

        return self.layout


    def buildFigure(self):
        '''
        draw the final plot (single plot)
        '''

        fig = go.Figure(data = self.trace, layout = self.layout)
        plotly.offline.plot(fig)


    def buildFigures(self, ptrace):
        '''
        draw the final plot (multi plot)
        '''

        figures = go.Figure(data = ptrace)
        plotly.offline.plot(figures)


    def buildSubPlots(self, grid, row, column, ptrace):
        '''
        draw subplots
        '''

        if grid == 'row':

            fig = tools.make_subplots(rows=row, cols=column)

            for i, itm in enumerate(ptrace):
                    fig.append_trace(itm, row, i+1)

        elif grid == 'col':

            fig = tools.make_subplots(rows=row, cols=column)

            for i, itm in enumerate(ptrace):
                    fig.append_trace(itm, i+1, column)

        plotly.offline.plot(fig)


    # webview failed attempt
    def buildWeb(self):
        '''
        draw the final plot (single plot)
        '''

        fig = go.Figure(data = self.trace, layout = self.layout)
        self.pp = plotly.offline.plot(fig, output_type='div')

        return self.pp
