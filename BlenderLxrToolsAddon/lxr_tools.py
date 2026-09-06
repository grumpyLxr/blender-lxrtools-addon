
import bpy

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


class OBJECT_OT_inverted_booltool(bpy.types.Operator):
    """Outward Normals -> BoolTool Auto Operation -> Inward Normals"""
    bl_idname = "object.inverted_booltool"
    bl_label = "Invert BoolTool"
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.StringProperty(name="Operation", default="DIFFERENCE")

    def execute(self, context):
        # 1. Verify BoolTool add-on is enabled
        if not hasattr(bpy.ops.object, "booltool_auto_difference"):
            self.report({'ERROR'}, "BoolTool is not enabled! Enable it in Edit > Preferences > Add-ons.")
            return {'CANCELLED'}

        # 2. Verify selection
        selected_meshes = [o for o in context.selected_objects if o.type == 'MESH']
        if len(selected_meshes) < 2:
            self.report({'WARNING'}, "Select at least 2 mesh objects.")
            return {'CANCELLED'}

        # 3. Recalculate Normals OUTWARD for all selected meshes
        for obj in selected_meshes:
            set_mesh_normals(obj, inside=False)

        # 4. Execute corresponding BoolTool Auto Operation
        try:
            if self.operation == "DIFFERENCE":
                bpy.ops.object.boolean_auto_difference()
            elif self.operation == "UNION":
                bpy.ops.object.boolean_auto_union()
            elif self.operation == "INTERSECT":
                bpy.ops.object.boolean_auto_intersect()
            elif self.operation == "SLICE":
                bpy.ops.object.boolean_auto_slice()
        except Exception as e:
            self.report({'ERROR'}, f"BoolTool Operation Failed: {str(e)}")
            return {'CANCELLED'}

        # 5. Recalculate Normals INWARD for remaining resulting meshes
        remaining_meshes = [o for o in context.selected_objects if o.type == 'MESH']
        for obj in remaining_meshes:
            set_mesh_normals(obj, inside=True)

        return {'FINISHED'}


class VIEW3D_PT_inverted_booltool_panel(bpy.types.Panel):
    """Sidebar Panel under the Edit Tab"""
    bl_label = "Boolean"
    bl_idname = "VIEW3D_PT_inverted_booltool_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Edit'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.label(text="Auto Boolean")
        
        op_diff = col.operator("object.inverted_booltool", text="Difference", icon='SELECT_DIFFERENCE')
        op_diff.operation = "DIFFERENCE"

        op_union = col.operator("object.inverted_booltool", text="Union", icon='SELECT_EXTEND')
        op_union.operation = "UNION"

        op_inter = col.operator("object.inverted_booltool", text="Intersect", icon='SELECT_INTERSECT')
        op_inter.operation = "INTERSECT"

        op_slice = col.operator("object.inverted_booltool", text="Slice", icon='SELECT_DIFFERENCE')
        op_slice.operation = "SLICE"


def register():
    bpy.utils.register_class(OBJECT_OT_inverted_booltool)
    bpy.utils.register_class(VIEW3D_PT_inverted_booltool_panel)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_inverted_booltool_panel)
    bpy.utils.unregister_class(OBJECT_OT_inverted_booltool)
