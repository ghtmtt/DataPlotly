# DataPlotly

[![QGIS.org](https://img.shields.io/badge/QGIS.org-published-green)](https://plugins.qgis.org/plugins/DataPlotly/)
[![Test plugin](https://github.com/ghtmtt/DataPlotly/actions/workflows/test_plugin.yaml/badge.svg)](https://github.com/ghtmtt/DataPlotly/actions/workflows/test_plugin.yaml)
[![Transifex 🗺](https://github.com/ghtmtt/DataPlotly/actions/workflows/transifex.yml/badge.svg)](https://github.com/ghtmtt/DataPlotly/actions/workflows/transifex.yml)

The DataPlotly plugin allows creation of [D3](https://d3js.org/)-like
interactive plots directly within QGIS, thanks to the [Plotly](https://plot.ly/python/)
library and its Python API.

DataPlotly makes plot creation and customization easy for every needs.

Besides all the plot and customization available, the plot is **linked** with
the QGIS map canvas:

![Plot interactions](img/plot_interaction_scatter.gif)

![Plot interactions](img/plot_interaction_box.gif)

## Usage
DataPlotly works **only with QGIS 3**. No additional libraries are necessary.

## Gallery

### Single Plot

Some examples of single plot type with some options. The list is far away to show all the possibilities.

#### Scatter Plot
![Plot interactions](img/plot_scatter.png)

#### Box Plot with statistics
![Plot interactions](img/plot_box.png)

#### Violin Plot
![Plot interactions](img/plot_violin.png)

#### Stacked Bar Plot
![Plot interactions](img/plot_bar_stack.png)

#### Probability Histogram
![Plot interactions](img/plot_histogram.png)

#### Pie Chart
![Plot interactions](img/plot_pie.png)

#### 2D Histogram
![Plot interactions](img/plot_2dhistogram.png)

#### Polar Plot
![Plot interactions](img/plot_polar.png)

#### Ternary Plot
![Plot interactions](img/plot_ternary.png)

#### Contour Plot
![Plot interactions](img/plot_contour.png)

### Multi Plots
DataPloty allows creation of different plot type in the same *plot canvas* but also allows the chance to separate each plot in a different canvas.

<aside class="warning">
Some plot are not compatible with overlapping or subplotting. A message will warn you when this happens.
</aside>


## Overlapped Plots
![Plot interactions](img/plot_scatter_bar.png)

## Subplots in row
![Plot interactions](img/plot_histogram_violin.png)

## Subplots in column
![Plot interactions](img/plot_scatter_histogram.png)
