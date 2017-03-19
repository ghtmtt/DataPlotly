import plotly
import plotly.graph_objs as go


class Plot(object):

    plot_type = ''

    plot_properties = {}

    plot_layout = {}


    def buildProperties(self, *args, **kwargs):
        '''
        dictionary with all the plot properties
        '''

        self.plot_properties = {}

        for k, v in kwargs.items():
            self.plot_properties[k] = v

        return self.plot_properties


    def buildTrace(self, plot_type):
        '''
        build the Trace that will be plotted depensing on the plot type
        '''

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
            self.trace = [go.Box(
            y = self.plot_properties['y']
            )]

        return self.trace


    def layoutProperties(self, * args, **kwargs):
        '''
        build the layout customizations
        '''

        self.plot_layout = {}

        for k, v in kwargs.items():
            self.plot_layout[k] = v

        return self.plot_layout


    def buildLayout(self):

        self.layout = go.Layout(
            showlegend = True,
            title = self.plot_layout['title']
        )

        return self.layout


    def buildFigure(self):
        '''
        draw the final plot
        '''

        fig = go.Figure(data = self.trace, layout = self.layout)
        plotly.offline.plot(fig)
