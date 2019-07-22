# -*- coding: utf-8 -*-
"""
Base class for trace factories

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""


class TraceFactory:
    """
    Base class for trace factories
    """

    @staticmethod
    def create_trace(settings):
        """
        Returns a new trace using the specified plot settings
        """
        return None
