"""PAM Gui Module"""

import logging

import bpy

from . import utils

logger = logging.getLogger(__package__)


class PAMPreferencesPane(bpy.types.AddonPreferences):
    """Preferences pane displying all addon-wide properties.

    Located in
    `File > User Preferences > Addons > Object: PAM"
    """

    bl_idname = __package__
    log_level_items = [
        ("DEBUG", "(4) DEBUG", "", 4),
        ("INFO", "(3) INFO", "", 3),
        ("WARNING", "(2) WARNING", "", 2),
        ("ERROR", "(1) ERROR", "", 1),
        ]
    data_location = bpy.utils.user_resource(
        "DATAFILES",
        path=__package__,
        create=True
    )
    log_directory = bpy.props.StringProperty(
        name="Log Directory",
        default=data_location,
        subtype="DIR_PATH",
        update=utils.log_callback_properties_changed
    )
    log_filename = bpy.props.StringProperty(
        name="Log Filename",
        default="pam.log",
        update=utils.log_callback_properties_changed
    )
    log_level = bpy.props.EnumProperty(
        name="Log Level",
        default="ERROR",
        items=log_level_items,
        update=utils.log_callback_properties_changed
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Logging:")
        col.prop(self, "log_directory", text="Directory")
        col.prop(self, "log_filename", text="Filename")
        col.prop(self, "log_level", text="Level")


class PAMToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all neuronal modelling operations"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Base"
    bl_category = "PAM"

    def draw(self, context):
        layout = self.layout
        col = layout.column()


class PAMMeasureToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all measurment operations"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Measure"
    bl_category = "PAM"

    def draw(self, context):
        active_obj = context.active_object

        name = ""
        if active_obj is not None:
            if active_obj.type == "MESH":
                name = active_obj.name

        layout = self.layout
        layout.label("Active Object: %s" % name)

        row = layout.row()
        col = row.column()
        col.prop(context.scene.pam_measure, "quantity", text="Neurons")
        col.prop(context.scene.pam_measure, "area", text="Area")

        row = layout.row()
        col = row.column()
        op = col.operator("pam.measure_layer", "Calculate")
        col.label("Total number of neurons:")
        col.label("%d" % context.scene.pam_measure.neurons)


class PAMVisualizeKernelToolsPanel(bpy.types.Panel):
    """A tools panel for visualization of kernel function """

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Visualize kernel"
    bl_category = "PAM"

    def draw(self, context):
        active_obj = context.active_object


class PAMTestPanel(bpy.types.Panel):
    """Test Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Testing"
    bl_category = "PAM"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(
            "pam.test_operator",
        )
