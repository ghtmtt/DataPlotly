from qgis.core import *

def getFields(lay, exp):
    '''
    from a QgsFieldExpressionWidget to a list of data
    '''

    vl = lay.currentLayer()
    if exp:
        field = exp.currentText()
    else:
        field = None

    data = []

    # get the data from the layer
    # no expression
    if not field:
        for i in vl.getFeatures():
            data.append(i.id())
    elif not exp.currentField()[1]:
        for i in vl.getFeatures():
            data.append(i[field])
    # if expression is selected
    else:
        # expression name
        fil = exp.currentField()[0]
        # expr = QgsExpression(fil)
        # for i in vl.getFeatures():
            # data.append(expr.evaluate(i, vl.pendingFields()))


    return data



def hex_to_rgb(value):
    '''
    convert hex string to rgb tuple directly from a QgsColorButton
    '''
    name = value.color().name()
    value = name.lstrip('#')
    lv = len(value)
    col = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    final = 'rgb' + str(col)
    return final
