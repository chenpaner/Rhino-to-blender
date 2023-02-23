bl_info = {
    "name": "Rhino to Blender",
    "author": "Alan Mattano,CP设计",
    "version": (0, 2),
    "blender": (2, 81, 0),
    "location": "View3D > Add > Add-Rhino&Export-Rhino",
    "description": "Rhino to Blender，Blender to Rhino",
    "warning": "",
    "doc_url": "https://space.bilibili.com/2711518?spm_id_from=333.1007.0.0",
    "category": "Add Mesh",
}

import bpy
import bpy.utils.previews
import os
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """导入Rhino Mesh对象"""
    bl_idname = "mesh.add_object"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):        
        bpy.ops.import_scene.obj(filepath=os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj'), axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl")
        #导入后缩放0.1
        bpy.ops.transform.resize(value=(0.1, 0.1, 0.1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
        return {'FINISHED'}
def sna_add_to_view3d_mt_add_7D1A0(self, context):
    if not (False):
        layout = self.layout
        op = layout.operator('mesh.add_object', text='Add-Rhino', icon_value=_icons['SmallTile.png'].icon_id, emboss=True, depress=False)
        
#----------------------------------------------------------------------------

class OBJECT_OT_add_objectexport(Operator, AddObjectHelper):
    """导出到Rhino Mesh对象"""
    bl_idname = "mesh.add_objectexport"
    bl_label = "Save Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):        

        print("Exporting...")
        bpy.ops.export_scene.obj(filepath=os.path.join(os.path.dirname(__file__), 'assets', 'Blender to Rhino-mesh.obj'), use_selection=True,axis_forward='Y',axis_up='Z')

        return {'FINISHED'}

def sna_add_to_view3d_mt_export_7D1A0(self, context):
    if not (False):
        layout = self.layout
        op = layout.operator('mesh.add_objectexport', text='Export-Rhino', icon_value=_icons['MediumTile.png'].icon_id, emboss=True, depress=False)


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.utils.register_class(OBJECT_OT_add_object) 
    if not 'SmallTile.png' in _icons: _icons.load('SmallTile.png', os.path.join(os.path.dirname(__file__), 'icons', 'SmallTile.png'), "IMAGE")
    if not 'MediumTile.png' in _icons: _icons.load('MediumTile.png', os.path.join(os.path.dirname(__file__), 'icons', 'MediumTile.png'), "IMAGE")   
    bpy.utils.register_class(OBJECT_OT_add_objectexport)
    bpy.types.VIEW3D_MT_add.append(sna_add_to_view3d_mt_add_7D1A0)#此行是添加到添加菜单里
    # bpy.types.VIEW3D_MT_mesh_add.append(sna_add_to_view3d_mt_add_7D1A0)#此行是添加到网格添加2级菜单里
    bpy.types.VIEW3D_MT_add.append(sna_add_to_view3d_mt_export_7D1A0)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)   
    bpy.utils.unregister_class(OBJECT_OT_add_objectexport)
    bpy.types.VIEW3D_MT_add.remove(sna_add_to_view3d_mt_add_7D1A0)
    bpy.types.VIEW3D_MT_add.remove(sna_add_to_view3d_mt_export_7D1A0)

if __name__ == "__main__":
    register()
