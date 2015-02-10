"""PAM menus module"""

import bpy

from .. import mapping


class PAMMappingMenu(bpy.types.Menu):
    bl_idname = "pam.mapping_menu"
    bl_label = "Mapping"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()

        for (key, name, _, _, _) in mapping.LAYER_TYPES[1:]:
            pie.operator("pam.mapping_layer_set", "Add layer as %s" % name).type = key


def register():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'SPACE', 'PRESS', shift=True, ctrl=True)
    kmi.properties.name = "pam.mapping_menu"


def unregister():
    pass