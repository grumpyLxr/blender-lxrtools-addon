from typing import Iterable, Self
import addon_utils
import bpy
from bpy.types import (
    Context,
    Menu
)
from bpy.props import BoolProperty, EnumProperty, IntProperty, StringProperty

from . import log

def set_mesh_normals(obj, inside=False):
    """Switches to Edit Mode and recalculates normals for a given mesh object."""
    if obj and obj.type == 'MESH':
        prev_active = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = obj
        
        # Recalculate normals in Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=inside)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.context.view_layer.objects.active = prev_active


OPERATION_DIFF = "Difference"
OPERATION_UNION = "Union"
OPERATION_INTERSECT = "Intersect"
OPERATION_SLICE = "Slice"

BOOL_OPERATIONS: Iterable[tuple[str, str, str]] = [
    (OPERATION_DIFF, "Difference", "Boolean difference operation"),
    (OPERATION_UNION, "Union", "Boolean union operation"),
    (OPERATION_INTERSECT, "Intersect", "Boolean intersect operation"),
    (OPERATION_SLICE, "Slice", "Boolean slice operation"),
]

BOOL_OPERATION_ICONS: dict[str, str] = {
    OPERATION_DIFF: "SELECT_SUBTRACT",
    OPERATION_UNION: "SELECT_EXTEND",
    OPERATION_INTERSECT: "SELECT_INTERSECT",
    OPERATION_SLICE: "SELECT_DIFFERENCE",
}

class OBJECT_OT_inverted_booltool(bpy.types.Operator):
    """Outward Normals -> BoolTool Auto Operation -> Inward Normals"""
    bl_idname = "object.inverted_booltool"
    bl_label = "Invert BoolTool"
    bl_options = {'REGISTER', 'UNDO'}

    # operation: bpy.props.StringProperty(name="Operation", default="DIFFERENCE")
    operation: EnumProperty(name="Operation", items=BOOL_OPERATIONS, default=0) # type: ignore

    def execute(self, context):
        # 1. Verify BoolTool add-on is enabled -----
        # enabled_addons = bpy.context.preferences.addons.keys()
        # for addon_id in enabled_addons:
        #     log.log(addon_id)
        booltool_is_enabled, booltool_is_loaded = addon_utils.check("bl_ext.blender_org.bool_tool")
        if not booltool_is_enabled:
            log.error(self, "BoolTool is not enabled! Enable it in Edit > Preferences > Add-ons.")
            return {'CANCELLED'}

        # 2. Verify selection
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if len(selected_meshes) < 2:
            self.report({'WARNING'}, "Select at least 2 mesh objects.")
            return {'CANCELLED'}

        # 3. Recalculate Normals OUTWARD for all selected meshes
        for obj in selected_meshes:
            set_mesh_normals(obj, inside=False)

        # 4. Execute corresponding BoolTool Auto Operation
        try:
            if self.operation == OPERATION_DIFF:
                bpy.ops.object.boolean_auto_difference()
            elif self.operation == OPERATION_UNION:
                bpy.ops.object.boolean_auto_union()
            elif self.operation == OPERATION_INTERSECT:
                bpy.ops.object.boolean_auto_intersect()
            elif self.operation == OPERATION_SLICE:
                bpy.ops.object.boolean_auto_slice()
        except Exception as e:
            log.error(self, "BoolTool Operation Failed: {}", str(e))
            return {'CANCELLED'}

        # 5. Recalculate Normals INWARD for remaining resulting meshes
        remaining_meshes = [o for o in context.selected_objects if o.type == 'MESH']
        for obj in remaining_meshes:
            set_mesh_normals(obj, inside=True)

        return {'FINISHED'}


class VIEW3D_PT_inverted_booltool_panel(bpy.types.Panel):
    """Sidebar Panel under the Edit Tab"""
    bl_label = "Inverted Boolean"
    bl_idname = "VIEW3D_PT_inverted_booltool_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Edit'

    def draw(self, context: Context):
        layout = self.layout
        col = layout.column(align=True)

        col.label(text="Auto Boolean")
        
        for bool_op_def in BOOL_OPERATIONS:
            op = col.operator(
                OBJECT_OT_inverted_booltool.bl_idname, text=bool_op_def[1], icon=BOOL_OPERATION_ICONS[bool_op_def[0]]
            )
            op.operation = bool_op_def[0]


# --- UI: Object Submenu ---
class VIEW3D_MT_normal_booltool_menu(bpy.types.Menu):
    """Submenu placed inside View3D > Object Menu"""

    bl_label = "Inverted Boolean"
    bl_idname = "VIEW3D_MT_normal_booltool_menu"

    def draw(self, context: Context):
        layout = self.layout
        
        for bool_op_def in BOOL_OPERATIONS:
            op = layout.operator(
                OBJECT_OT_inverted_booltool.bl_idname, text=bool_op_def[1], icon=BOOL_OPERATION_ICONS[bool_op_def[0]]
            )
            op.operation = bool_op_def[0]


def object_menu_func(self: Menu, context: Context):
    """Appends the submenu entry into the Object menu"""
    self.layout.separator()
    self.layout.menu(VIEW3D_MT_normal_booltool_menu.bl_idname, icon="MOD_BOOLEAN")


def register():
    bpy.utils.register_class(OBJECT_OT_inverted_booltool)
    bpy.utils.register_class(VIEW3D_PT_inverted_booltool_panel)
    bpy.utils.register_class(VIEW3D_MT_normal_booltool_menu)
    
    # Append entry into Object menu
    bpy.types.VIEW3D_MT_object.append(object_menu_func)


def unregister():
    # Remove entry from Object menu
    bpy.types.VIEW3D_MT_object.remove(object_menu_func)
    
    bpy.utils.unregister_class(VIEW3D_MT_normal_booltool_menu)
    bpy.utils.unregister_class(VIEW3D_PT_inverted_booltool_panel)
    bpy.utils.unregister_class(OBJECT_OT_inverted_booltool)
