# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Carborama
                                 A QGIS plugin
 Compute Forest CO2 equivalent emissions, due to degradation and deforestation
                             -------------------
        begin                : 2017-08-09
        copyright            : (C) 2017 by Bruno Combal
        email                : bruno.combal@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Carborama class from file Carborama.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .carborama import Carborama
    return Carborama(iface)
