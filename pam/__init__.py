"""Parametrical Anatomical Mapping for Blender"""

import logging

import bpy

from . import gui
from . import utils
from . import tools
from . import mapping

logger = logging.getLogger(__name__)

bl_info = {
    "name": "PAM",
    "author": "Sebastian Klatt, Martin Pyka",
    "version": (0, 2, 0),
    "blender": (2, 7, 0),
    "license": "GPL v2",
    "description": "Parametric Anatomical Modeling is a method to translate "
                   "large-scale anatomical data into spiking neural networks.",
    "category": "Object"
}

__author__ = bl_info['author']
__license__ = bl_info['license']
__version__ = ".".join([str(s) for s in bl_info['version']])


def register():
    """Called on enabling this addon"""
    bpy.utils.register_class(gui.PAMPreferencesPane)
    utils.log.initialize()

    tools.measure.register()
    tools.visual.register()
    mapping.register()

    bpy.utils.register_module(__name__)
    logger.debug("Registering addon")


def unregister():
    """Called on disabling this addon"""
    tools.measure.unregister()
    tools.visual.unregister()
    mapping.unregister()

    bpy.utils.unregister_module(__name__)
    logger.debug("Unregistering addon")


if __name__ == "__main__":
    register()
