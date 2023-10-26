bl_info = {
    "name": "Rhino to Blender",
    "author": "chenpaner",
    "version": (1, 0, 0),
    "blender": (2, 81, 0),
    "location": "View3D > Add > Add-Rhino&Export-Rhino",
    "description": "Rhino to Blender，Blender to Rhino",
    "warning": "",
    "doc_url": "https://github.com/chenpaner/Rhino-to-blender",
    "category": "Add Mesh",
}
import bpy
import bpy.utils.previews
import os
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
class OBJECT_OT_add_object_coll(Operator, AddObjectHelper):
    """导入Rhino Mesh对象"""
    bl_idname = "mesh.add_object_coll"
    bl_label = "Import obj from Rhino"
    bl_description = "Import obj from Rhino,Use collections instead of layers!"
    bl_options = {'REGISTER', 'UNDO'}
    scale_options = [
        ("1", "1.0(mm ⇉ m)", "Scale by 1.0"),
        ("0.1", "0.1(mm ⇉ cm)", "Scale by 0.1"),
        ("0.01", "0.01(mm ⇉ mm)", "Scale by 0.01"),
    ]
    scale_option: bpy.props.EnumProperty(
        items=scale_options,
        name="Scale",
        description="Select the scaling factor",
        default="0.01"  
    )
    apply_transform: bpy.props.BoolProperty(
        name="Apply Scale",
        description="Apply transform after scaling",
        default=True
    )
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True 
        layout.use_property_decorate = False  
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=True)
        col = flow.column(align=False)
        col.ui_units_x = 7
        row_30B0D = col.row(heading='', align=True)
        op = row_30B0D.prop(self, "apply_transform")
        row_40B0D = col.row(heading='', align=True)
        op = row_40B0D.prop(self, "scale_option")
    def execute(self, context): 
        bpy.context.scene.cycles.preview_pause = True
        scale_factor = float(self.scale_option)  
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj')
        if os.path.exists(file_path):
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
            scene_name = bpy.context.scene.name 
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection     
            bpy.ops.import_scene.obj(
                filepath=os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj'),
                axis_forward='-Z',
                axis_up='Y',
                filter_glob="*.obj;*.mtl"
            ) 
            bpy.ops.transform.resize(
                    value=(scale_factor, scale_factor, scale_factor),
                    orient_type='GLOBAL',
                    orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                    orient_matrix_type='GLOBAL'
                )
            if self.apply_transform:
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            imported_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
            common_name = None
            common_name1 = None
            if imported_objects:
                common_name1 = imported_objects[0].name.split('/')[0]
                common_name = f"{common_name1}+[{scene_name}]"
            root_collection = None
            root_collection = bpy.data.collections.get(common_name)
            if not root_collection:
                for collection in bpy.context.scene.collection.children:
                    if common_name1 in collection.name:
                        if collection.name != common_name:
                            collection.name = common_name
                        root_collection = collection
                        break
            if not root_collection:
                root_collection = bpy.data.collections.new(common_name)
                bpy.context.scene.collection.children.link(root_collection)
            for obj in imported_objects:
                obj_name = obj.name
                parts = obj_name.split("/")
                group_name = parts[-1].split("*")[0]
                nested_collection_names = group_name.split("::")
                current_parent_collection = root_collection
                for collection_name in nested_collection_names:
                    child_collection = None
                    for child in current_parent_collection.children:
                        if collection_name in child.name:
                            child_collection = child
                            break
                    if not child_collection:
                        child_collection = bpy.data.collections.new(collection_name)
                        current_parent_collection.children.link(child_collection)
                    current_parent_collection = child_collection
                bpy.context.scene.collection.objects.unlink(obj)
                current_parent_collection.objects.link(obj)
                bpy.context.view_layer.objects.active =obj
                new_name = obj_name.split("/")[-1]            
                if "::" in new_name:
                    new_name = new_name.split("::")[-1]
                newww_name= new_name.split(".")[0]
                obj.name = new_name
                last_matching_obj = None
                for existing_obj in current_parent_collection.objects:
                    if existing_obj == obj:
                        continue  
                    if newww_name in existing_obj.name:
                        last_matching_obj = existing_obj
                if last_matching_obj:
                    obj.data.materials.clear()  
                    has_materials = False
                    for slot in last_matching_obj.material_slots:
                        if slot.material:
                            new_material = slot.material
                            obj.data.materials.append(new_material)
                            has_materials = True
                    if not has_materials:
                        self.report({'INFO'}, "The last matching object has no materials.")
            self.report({'INFO'}, f"Successfully imported {len(imported_objects)} models from {common_name1}.3dm.")
        else:
            self.report({'ERROR'}, f"Fichier '{file_path}' does not exist. Please export it from Rhino first.")
        bpy.context.scene.cycles.preview_pause = False
        return {'FINISHED'}
class OBJECT_OT_add_object_empt(Operator, AddObjectHelper):
    """导入Rhino Mesh对象"""
    bl_idname = "mesh.add_object_empt"
    bl_label = "Import obj from Rhino!"
    bl_description = "Import obj from Rhino,Use emptys instead of layers!"
    bl_options = {'REGISTER', 'UNDO'}
    scale_options = [
        ("1", "1.0(mm ⇉ m)", "Scale by 1.0"),
        ("0.1", "0.1(mm ⇉ cm)", "Scale by 0.1"),
        ("0.01", "0.01(mm ⇉ mm)", "Scale by 0.01"),
    ]
    scale_option: bpy.props.EnumProperty(
        items=scale_options,
        name="Scale",
        description="Select the scaling factor",
        default="0.01"  
    )
    apply_transform: bpy.props.BoolProperty(
        name="Apply Scale",
        description="Apply transform after scaling",
        default=True
    )
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True 
        layout.use_property_decorate = False  
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=True)
        col = flow.column(align=False)
        col.ui_units_x = 7
        row_30B0D = col.row(heading='', align=True)
        op = row_30B0D.prop(self, "apply_transform")
        row_40B0D = col.row(heading='', align=True)
        op = row_40B0D.prop(self, "scale_option")
    def execute(self, context):
        bpy.context.scene.cycles.preview_pause = True
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection  
        scene_name = bpy.context.scene.name 
        scale_factor = float(self.scale_option)  
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj')
        if os.path.exists(file_path):
            object_names = []
            with open(file_path, 'r') as obj_file:
                for line in obj_file:
                    if line.startswith("o "):
                        object_name = line.split(" ")[1].strip()
                        object_names.append(object_name)
            common_name = None
            common_name1 = None
            if object_names:
                common_name1 = object_names[0].split('/')[0]
                common_name = f"{common_name1}+[{scene_name}]"
                root_empty = None
                for empty in [obj for obj in bpy.context.scene.collection.objects if obj.type == 'EMPTY']:
                    if empty.name == common_name:
                        root_empty = empty
                        break
                    elif common_name1 in empty.name and empty.name != common_name:
                        empty.name = common_name
                        root_empty = empty
                        break
                original_location =""
                original_rotation=""
                original_scale=""
                if root_empty is None:
                    bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                    bpy.context.object.show_in_front = True
                    bpy.context.object.show_name = True
                    root_empty = bpy.context.object
                    root_empty.name = common_name
                else:
                    original_location = root_empty.location.copy()
                    original_rotation = root_empty.rotation_euler.copy()
                    original_scale = root_empty.scale.copy()
                    root_empty.location = (0, 0, 0)
                    root_empty.rotation_euler = (0, 0, 0)
                    root_empty.scale = (1, 1, 1)  
                try:
                    bpy.context.view_layer.objects.active = None
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
                    bpy.ops.import_scene.obj(
                        filepath=os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj'),
                        axis_forward='-Z',
                        axis_up='Y',
                        filter_glob="*.obj;*.mtl"
                    )
                    bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL')
                    if self.apply_transform:
                        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                    imported_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
                    for obj in imported_objects:
                        obj_name = obj.name
                        parts = obj_name.split("/")
                        group_name = parts[-1].split("*")[0]
                        if "::" in group_name:
                            nested_collection_names = group_name.split("::")
                        else:
                            nested_collection_names = [group_name]
                        current_parent_empty = root_empty
                        for collection_name in nested_collection_names:
                            child_empty = None
                            for child in current_parent_empty.children:
                                if collection_name in child.name and child.type == 'EMPTY':
                                    child_empty = child
                                    break
                            if not child_empty:
                                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                                bpy.context.object.empty_display_size = 0.5
                                child_empty = bpy.context.object
                                child_empty.name = collection_name
                                child_empty.parent = current_parent_empty
                                child_empty.matrix_parent_inverse = current_parent_empty.matrix_world.inverted()                   
                            current_parent_empty = child_empty
                        obj.parent = current_parent_empty
                        obj.matrix_parent_inverse = current_parent_empty.matrix_world.inverted()
                        new_name = obj_name.split("/")[-1]
                        if "::" in new_name:
                            new_name = new_name.split("::")[-1]
                        newww_name= new_name.split(".")[0]
                        obj.name = new_name
                        last_matching_obj = None
                        for existing_obj in current_parent_empty.children:
                            if existing_obj == obj:
                                continue  
                            if newww_name in existing_obj.name:
                                last_matching_obj = existing_obj
                        if last_matching_obj:
                            obj.data.materials.clear()  
                            has_materials = False
                            for slot in last_matching_obj.material_slots:
                                if slot.material:
                                    new_material = slot.material
                                    obj.data.materials.append(new_material)
                                    has_materials = True
                            if not has_materials:
                                self.report({'INFO'}, "The last matching object has no materials.")
                except:
                    pass
            if original_location and original_rotation and original_scale:
                root_empty.location = original_location
                root_empty.rotation_euler = original_rotation
                root_empty.scale = original_scale
            try:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = current_parent_empty
                current_parent_empty.select_set(True)
                bpy.ops.machin3.groupify()
            except Exception as e:
                print("Only if the M3 plugin is installed will the root parent empty object be converted to an M3 empty object!")
            bpy.ops.object.select_all(action='DESELECT')
            for obj in imported_objects:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            self.report({'INFO'}, f"Imported {len(imported_objects)} models from {common_name1}.3dm.")
        else:
            self.report({'ERROR'}, f"Fichier '{file_path}' does not exist. Please export it from Rhino first.")
        bpy.context.scene.cycles.preview_pause = False
        return {'FINISHED'}
def sna_add_to_view3d_mt_add_7D1A0(self, context):
    if not (False):
        layout = self.layout
        op = layout.operator('mesh.add_object_coll', text='Import4Rhino(coll)', icon_value=_icons['SmallTile.png'].icon_id, emboss=True, depress=False)
        op = layout.operator('mesh.add_object_empt', text='Import4Rhino(empt)', icon_value=_icons['SmallTile.png'].icon_id, emboss=True, depress=False)
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
    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    if not (False):
        layout = self.layout
        if addon_prefs.sna_show_export2rhino_:
            op = layout.operator('mesh.add_objectexport', text='Export2Rhino', icon_value=_icons['MediumTile.png'].icon_id, emboss=True, depress=False)
class SNA_AddonPreferences_9F6AA(bpy.types.AddonPreferences):
    bl_idname = __name__
    sna_show_export2rhino_: bpy.props.BoolProperty(
        name='Show Export2Rhino',
        description='Whether to display the export button in the right-click menu',
        default=False
    )
    def draw(self, context):
        layout = self.layout
        layout.label(text='Please ensure that the root empty object or collection is under the scene root collection.If it is moved to another collection, a new collection or empty object will be automatically created.',icon='ERROR')
        layout.label(text='请确保根空物体或者集合在场景根集合下,如果移动到其它集合下后会自动新建一个集合或者空物体!',icon='ERROR')
        layout.prop(self, 'sna_show_export2rhino_')
def register():
    import bpy.utils.previews
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.utils.register_class(OBJECT_OT_add_object_coll)
    bpy.utils.register_class(OBJECT_OT_add_object_empt) 
    if not 'SmallTile.png' in _icons: _icons.load('SmallTile.png', os.path.join(os.path.dirname(__file__), 'icons', 'SmallTile.png'), "IMAGE")
    if not 'MediumTile.png' in _icons: _icons.load('MediumTile.png', os.path.join(os.path.dirname(__file__), 'icons', 'MediumTile.png'), "IMAGE")   
    bpy.utils.register_class(OBJECT_OT_add_objectexport)
    bpy.types.VIEW3D_MT_add.append(sna_add_to_view3d_mt_add_7D1A0)
    bpy.types.VIEW3D_MT_add.append(sna_add_to_view3d_mt_export_7D1A0)
    bpy.utils.register_class(SNA_AddonPreferences_9F6AA)
def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    bpy.utils.unregister_class(OBJECT_OT_add_object_coll) 
    bpy.utils.unregister_class(OBJECT_OT_add_object_empt)  
    bpy.utils.unregister_class(OBJECT_OT_add_objectexport)
    bpy.types.VIEW3D_MT_add.remove(sna_add_to_view3d_mt_add_7D1A0)
    bpy.types.VIEW3D_MT_add.remove(sna_add_to_view3d_mt_export_7D1A0)
    bpy.utils.unregister_class(SNA_AddonPreferences_9F6AA)
if __name__ == "__main__":
    register()
