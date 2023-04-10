# -*- coding: utf-8 -*-
"""COre Utilities

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""


def safe_str_xml(s):
    """ replaces spaces by .
    """
    return s.replace(" ", ".")

def restore_safe_str_xml(s):
    """ replaces . by spaces
    """
    return s.replace(".", " ")