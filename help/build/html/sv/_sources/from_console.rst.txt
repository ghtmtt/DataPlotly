.. _from_console:

Call the plugin from the python console (BETA!)
===============================================
DataPlotly comes with some simple API that can be used from the python console.

Actually the method accept a structured `dictionary` as input, calls and open the
dialog of the plugin populating each field with the dictionary values and creating
the final plot.

.. note:: not all the customization are (yet) available in this method, but you can easily update the plot with the `Update Plot` button. See :ref:`basic_usage`

Code example
------------
The following example is very simple and straightforward. Supposing you have
already a layer loaded in the QGIS legend we will access to is, take 2 fields
and building a simple scatter plot.

Open QGIS and the python console. The example considers the `PH` and `T` fields
of the layer (just look at the code and change the fields according to your
layer):

.. code-block:: python

  # create the VectorLayer object from with iface
  vl = iface.activeLayer()

  # import the plugins
  from qgis.utils import plugins

  # create the instace of the DataPlotly plugin
  my = plugins['DataPlotly']

  # initialize and empty dictionary
  dq = {}

  # create nested dictionaries for plot and layour properties
  dq['plot_prop'] = {}
  dq['layout_prop'] = {}

  # start to fill the dictionary with values you want

  # plot type
  dq['plot_type'] = 'scatter'
  # QgsVectorLayer object
  dq["layer"] = vl
  # choose the plot properties
  dq['plot_prop']['x'] = [i["O2"] for i in vl.getFeatures()]
  dq['plot_prop']['y'] = [i["EC"] for i in vl.getFeatures()]
  dq['plot_prop']['marker'] = 'markers'
  dq['plot_prop']['x_name'] = 'O2'
  dq['plot_prop']['y_name'] = 'EC'

  # choose the layout properties
  dq['layout_prop']['legend'] = True
  dq['layout_prop']["range_slider"] = {}
  dq['layout_prop']["range_slider"]["visible"] = False

  # call the method that opens the dialog
  my.loadPlot(dq)


Using the example code shown above should open the DataPlotly dialog, create the
plot and also popultate the dialog fields (comboboxes, checkboxes, etc.) with
the values chosen (where possible).

.. warning:: this method is still in **BETA** and there are several known issues.
