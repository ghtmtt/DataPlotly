# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotlyDialog
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


def getSortedId(_, field_list):
    '''
    return a list with values needed for js interaction

    the function creates the list so that the final order of the items is the
    same of that visible in the Plot Canvas and so the clicked element returns
    the correct id

    layer: a valid QgsVectorLayer, useful with self.layer_combo.currentLayer()
    field_list: a list of values (e.g. taken from the attribute table)
    '''

    res = []

    # create an empty variable if field_list is empty
    # case is when in the Box Plot the optional X group is empty (not chosen)
    if not field_list:
        res = None

    # don't sort the list if the item is integer or float (check the first item)
    elif isinstance(field_list[0], (int, float)):
        res = list(set(field_list))

    # sort the list if items are strings
    else:
        res = sorted(set(field_list), key=field_list.index)

    return res
