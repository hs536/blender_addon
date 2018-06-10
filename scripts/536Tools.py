import bpy
import bmesh
from bpy.props import BoolProperty, PointerProperty

bl_info = {
    "name": "536Tools",
    "author": "hibari536",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "View 3D > Tool Shelf > 536Tools",
    "description": "add-on tools for blender 3D which H.S.536 use.",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "https://twitter.com/hibari536",
    "category": "User Interface"
}


class adjustCursor(bpy.types.Operator):
    bl_idname = "object.adjust_cursor"
    bl_label = "Adjust 3D Cursor"
    bl_description = "Adjust 3D Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if isOperatable():
            adjust(context)
        return {'FINISHED'}


def adjust(context):
    bpy.context.area.spaces[0].pivot_point = 'ACTIVE_ELEMENT'
    target_object_name = bpy.context.object.name
    for mod in bpy.context.object.modifiers:
        if mod.type == 'ARMATURE':
            mod.show_in_editmode = False
        if mod.type == 'MIRROR':
            mod.show_viewport = False
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    for mod in bpy.context.object.modifiers:
        if mod.type == 'ARMATURE' or mod.type == 'MIRROR':
            mod.show_viewport = False
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1.0, view_align=False)
    dummy_empty_name=bpy.context.object.name
    bpy.context.scene.objects.active = bpy.data.objects[dummy_empty_name]
    bpy.context.scene.objects.active = bpy.data.objects[target_object_name]
    bpy.ops.object.parent_set(type='VERTEX',xmirror=False)
    bpy.ops.view3d.snap_selected_to_cursor()
    for mod in bpy.context.object.modifiers:
        if mod.type == 'ARMATURE':
            mod.show_viewport = True
    bpy.context.scene.objects.active = bpy.data.objects[dummy_empty_name]
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.context.scene.objects.unlink(bpy.data.objects[dummy_empty_name])
    bpy.data.objects.remove(bpy.data.objects[dummy_empty_name])
    bpy.context.scene.objects.active = bpy.data.objects[target_object_name]
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    for mod in bpy.context.object.modifiers:
        if mod.type == 'ARMATURE':
            mod.show_in_editmode = True
    bpy.context.area.spaces[0].pivot_point='CURSOR'
    for mod in bpy.context.object.modifiers:
        if mod.type == 'MIRROR':
            mod.show_viewport = True


def isOperatable():
    obj = bpy.context.active_object
    bm = bmesh.from_edit_mesh(obj.data)
    for e in bm.select_history:
        if e.select:
            return True
    return False


class UpdateCursor(bpy.types.Operator):
    bl_idname = "mesh.update_cursor"
    bl_label = "Auto Adjust 3D Cursor"
    bl_description = "Auto Adjust 3D Cursor"

    def invoke(self, context, event):
        props = context.scene.dfrc_props
        if context.area.type == 'VIEW_3D':
            if props.auto_update is False:
                props.auto_update = True
                props.left_mouse_down = False
                props.is_operatable = False
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                props.auto_update = False
                return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def modal(self, context, event):
        props = context.scene.dfrc_props

        if context.area:
            context.area.tag_redraw()

        if props.auto_update is False:
            return {'FINISHED'}
        
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                props.left_mouse_down = True
            elif event.value == 'RELEASE':
                props.left_mouse_down = False
                
        if props.left_mouse_down is True and props.is_operatable is False:
            props.is_operatable = True 
        
        if props.left_mouse_down is False and props.is_operatable is True:
            adjust(context)
            props.is_operatable = False

        return {'PASS_THROUGH'}


class VIEW3D_PT_CustomMenu(bpy.types.Panel):
    bl_label = "536Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "536Tools"
    bl_context = "mesh_edit"

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        props = context.scene.dfrc_props

        layout.label(text="Adjust 3D Cursor:")
        layout.operator(adjustCursor.bl_idname, text="Adjust")

        layout.separator()
        layout.label(text="Auto Adjust (needs 2 clicks):")
        if props.auto_update is False:
            layout.operator(UpdateCursor.bl_idname, text="Start", icon="PLAY")
        else:
            layout.operator(UpdateCursor.bl_idname, text="Stop", icon="PAUSE")


class DFRC_Properties(bpy.types.PropertyGroup):
    auto_update = BoolProperty(
        name="Auto Update Enabled",
        description="Auto Update Enabled",
        default=False
    )
    left_mouse_down = BoolProperty(
        name="StateOfLClick",
        description="State Mouse Left Button Pressed",
        default=False
    )
    is_operatable = BoolProperty(
        name="system flag",
        description="system flag",
        default=False
    )


def register():
    bpy.utils.register_module(__name__)
    sc = bpy.types.Scene
    sc.dfrc_props = PointerProperty(
        name="Properties",
        description="Properties to use with this addon.",
        type=DFRC_Properties
    )


def unregister():
    del bpy.types.Scene.dfrc_props
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
