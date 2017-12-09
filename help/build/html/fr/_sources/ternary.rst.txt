.. _ternary:

Ternary Plot
============
Here you will find the guide to every parameter of the ternary plot. If you
need more generic information please see :ref:`basic_usage`.

.. image:: /img/ternary/ternary.png
  :scale: 50%

Plot Properties
---------------
``Layer``: the combobox will display all the vector layers loaded in QGIS

``X Field``: the X field

``Y Field``: the Y field

``Z Field``: the Z field

``Marker Color``: marker color

``Data Defined Override``: you can add an Expression to define the size of the marker.
If activated other options are available: ``Color Scale``, ``Visible`` and ``Invert Color``.

``Marker Size``: the size of the marker

``Data Defined Override``: you can add an Expression to define the size of the marker

``Stroke Color``: border color

``Stroke Width``: the width of the border

``Point Type``: marker type

``Transparency``: transparency level of the marker/line

Plot Customizations
-------------------
``Show Legend``: show the legend of the current plot

``Horizontal Legend``: check if you want to have an horizontal legend

``Plot Title``: the plot title

``Legend Title``: the title of the legend

``X Label``: X label text

``Y Label``: Y Label text

``Z Label``: Z Label text

``Additional Hover Label``: choose another field of the plot (or other values)
that will be shown together with the other informations. This field supports
expressions: e.g. ``'The ID of this point is ' || ID``:

  .. image:: /img/ternary/ternary2.png
    :scale: 50%
