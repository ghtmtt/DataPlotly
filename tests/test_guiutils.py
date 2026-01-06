"""GUI Utils Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

__author__ = '(C) 2018 by Nyall Dawson'
__date__ = '20/04/2018'
__copyright__ = 'Copyright 2018, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

"""

from DataPlotly.gui.gui_utils import GuiUtils


def test_get_icon():
    """
    Tests get_icon
    """
    assert not GuiUtils.get_icon('dataplotly.svg').isNull()
    assert GuiUtils.get_icon('not_an_icon.svg').isNull()


def test_get_icon_svg():
    """
    Tests get_icon svg path
    """
    assert GuiUtils.get_icon_svg('dataplotly.svg')
    assert "dataplotly.svg" in GuiUtils.get_icon_svg('dataplotly.svg')
    assert not GuiUtils.get_icon_svg('not_an_icon.svg')
