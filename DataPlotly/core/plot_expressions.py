# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotly
                                 A QGIS plugin
 D3 Plots for QGIS
                              -------------------
        begin                : 2022-06-08
        git sha              : $Format:%H$
        copyright            : (C) 2020 by matteo ghetta
        email                : matteo.ghetta@faunalia.it
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

from qgis.utils import qgsfunction, iface

@qgsfunction(args='auto', group='DataPlotly')
def get_categories_colors(field, feature, parent):
    """
        Retrieve the color of each category as html code. You can use this function
        to set the plot items (pie slices, bars, points, etc) to the same color
        of the feature visible in the map.
        <h4>Syntax</h4>
        <p>
            get_categories_colors(categorization_field)
        </p>
        <h4>Arguments</h4>
        <p><strong>categorization_field</strong>: the name of the field used in the categorization</p>
        <h4>Example</h4>
        <p>
            get_categories_colors("CONTINENT") -> '#da1ddd'
        </p>
    """

    layer = iface.activeLayer()
    renderer = layer.renderer()
  
    if layer.renderer().type() == "categorizedSymbol":
        for category in renderer.categories():
            if field == category.value():
                category_color = category.symbol().color().name()
                break
                
    return category_color