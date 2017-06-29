.. intro:

Data Plotly
===========
Data Plotly is a python plugin for QGIS that allows the creation of `D3 <https://d3js.org/>`_
like plots thanks to the `Plotly library <https://plot.ly/>`_ and the python API.

Plots are not static so the user can easily get some information of the object
in the plot view while many other customizations are possible.

.. figure:: /img/intro/example.png
  :scale: 50%
  :align: center

  plot example


DataPlotly is intended to be a **plot container** so the user can create different
plot types in the same or in different plot canvas.

Each plot type has its own configurations and customizations so it is easy for
the user to choose the best solution that fits the needs.

Besides the interactive plot canvas, plots can be exported as `png` images or as
pure `html` files that can be opened with an external browser keeping in that way
the plot *interactivity* (e.g. zooming in or out).

Finally, plot raw html code can be copied and pasted somewhere else, for example
in html frame of the QGIS map composer or in an external website.

`Plotly library <https://plot.ly/>`_ javascript code is saved in the local plugin
folder so the plugin is usable also without any Internet connection.
