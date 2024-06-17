
bl_info = {
    "name": "Rhino to Blender",
    "author": "CP-Design",
    "version": (2, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Add > Add-Rhino&Export-Rhino",
    "description": "Rhino to Blender,Blender to Rhino",
    "warning": "",
    "doc_url": "https://github.com/chenpaner",
    "category": "Add Mesh",
}

import bpy
import bpy.utils.previews
import os
from bpy.types import Operator
from bpy.props import (BoolProperty,
                       EnumProperty,
                       FloatProperty)
from bpy_extras.object_utils import AddObjectHelper
from datetime import datetime
from bpy.app.handlers import persistent
if bpy.app.version >= (4, 1):
    from bpy.app.translations import pgettext_rpt as rpt_
else:
    from bpy.app.translations import pgettext_tip as rpt_

_icons = None

def get_preferences():
    return bpy.context.preferences.addons[__name__].preferences

@persistent
def disable_collection_for_render(scene, depsgraph):
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    backupname = "Rhino_backup["+bpy.context.scene.name+"]"  
    if addon_prefs.sna_autohide_render:
        for collection in bpy.data.collections:
            if backupname in collection.name:
                collection.hide_render = True
                collection.hide_viewport = True
                collection.hide_select = True
def find_collection_by_name(collection, target_name, common_name1):
    if collection.name == target_name:
        return collection
    if common_name1 in collection.name:
        if collection.name != target_name:
            collection.name = target_name
        return collection
    for child_collection in collection.children:
        result = find_collection_by_name(child_collection, target_name, common_name1)
        if result:
            return result
def find_and_unexclude_collection(collection, target_name):
    if collection.name == target_name:

        return True
    for child_collection in collection.children:
        if find_and_unexclude_collection(child_collection, target_name):
            return True
    return False
def all_layer_collections(view_layer):
    stack = [view_layer.layer_collection]
    while stack:
        lc = stack.pop()
        yield lc
        stack.extend(lc.children)
def unexclude_subcollections(collection, exclude=False):
    view_layer = bpy.context.view_layer
    if view_layer:
        for lc in all_layer_collections(view_layer):
            if lc.collection.name == collection.name:
                lc.exclude = exclude

    for child_collection in collection.children:
        unexclude_subcollections(child_collection, exclude)

class RHINO_OT_add_object_coll(Operator, AddObjectHelper):
    bl_idname = "rhino.add_object_coll"
    bl_label = "Import obj from Rhino by collection!"
    bl_description = "Import obj from Rhino,Use collections instead of layers!"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        self.start_time = 0
        wm = context.window_manager
        addon_prefs = context.preferences.addons[__name__].preferences
        if addon_prefs.show_import_plane:
            return wm.invoke_props_dialog(self, width=300)
        else:
            return self.execute(context)

    def draw(self, context):
        layout = self.layout
        addon_prefs = context.preferences.addons[__name__].preferences

        box_750F6 = layout.box()
        box_750F6=box_750F6.column(heading='', align=True)
        box_750F6.scale_y = 1.35
        box_750F6.prop(addon_prefs, "scale_option", text='', icon="SMALL_CAPS", emboss=True)
        box_750F6.prop(addon_prefs, "apply_transform", emboss=True)

        layout.prop(addon_prefs, "sna_use_rhinobackup", emboss=True)
        layout.prop(addon_prefs, "sna_autohide_render", emboss=True)

        layout.prop(addon_prefs, "show_import_plane",text='Show panel before import(Turn on again in preferences)', emboss=True)
        layout.separator()

    def execute(self, context):
        now = datetime.now()
        date_time = now.strftime("%m/%d/%H:%M:%S")
        self.start_time = datetime.now()
        addon_prefs = get_preferences()
        scene_name = bpy.context.scene.name

        bpy.context.scene.cycles.preview_pause = True
        scale_factor = float(addon_prefs.scale_option)
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj')

        imported_objects = None
        mesh_objects = None
        curve_objects = None

        coll_include = False
        if os.path.exists(file_path):
            common_name = None
            common_name1 = None
            root_collection = None
            object_names = []          
            with open(file_path, 'r') as obj_file:
                for line in obj_file:
                    if line.startswith("o "):
                        object_name = line[2:].strip()  
                        object_names.append(object_name)

            if object_names:
                longest_exceeding_name = ""
                for name in object_names:
                    name_byte_length = len(name.encode('utf-8'))
                    if name_byte_length > 64:
                        if len(name) > len(longest_exceeding_name):
                            longest_exceeding_name = name       
                if longest_exceeding_name:
                    self.report({'WARNING'},rpt_("The name length exceeds the maximum length allowed by blender, you can shorten the Rhino filename or layer name! (%s)") % (longest_exceeding_name))
                    print(rpt_("The name length exceeds the maximum length allowed by blender, you can shorten the Rhino filename or layer name! (%s)") % (longest_exceeding_name))
                    return {'FINISHED'}
                common_name1 = object_names[0].split('/')[0]

                common_name = f"{common_name1}+[{scene_name}]"
                for collection in bpy.context.scene.collection.children:
                    if collection.name == common_name:
                        root_collection = collection
                    elif common_name1 in collection.name:
                        if collection.name != common_name:
                            collection.name = common_name
                        root_collection = collection
                        self.report({'WARNING'}, "自动改名根集合 Rename coll name")
                        break
                    if root_collection is None:
                        result = find_collection_by_name(collection, common_name, common_name1)
                        if result:
                            root_collection = result
                            break
                if root_collection:
                    top_collections = bpy.context.view_layer.layer_collection.children
                    found_collection_a = False
                    for collection in top_collections:
                        if collection.name == root_collection.name:
                            collection.exclude = False
                            found_collection_a = True
                        else :
                            if find_and_unexclude_collection(collection,root_collection.name):
                                found_collection_a = True
                    if found_collection_a:
                        unexclude_subcollections(root_collection, exclude=False)
                if not root_collection:
                    root_collection = bpy.data.collections.new(common_name)
                    root_collection.color_tag = 'COLOR_04'
                    bpy.context.scene.collection.children.link(root_collection)
                if addon_prefs.sna_use_rhinobackup:
                    backupname = "Rhino_backup"
                    backupcolname = f"{backupname}[{scene_name}]"
                    backup_collection = None
                    backup_collection = context.scene.collection.children.get(backupcolname)
                    if not backup_collection:
                        for collection in bpy.context.scene.collection.children:
                            if backupname in collection.name:
                                if collection.name != backupcolname:
                                    collection.name = backupcolname
                                backup_collection = collection
                                break         
                    if not backup_collection:
                        backup_collection = bpy.data.collections.new(backupcolname)
                        backup_collection.color_tag = 'COLOR_01'
                        bpy.context.scene.collection.children.link(backup_collection)

                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection     
                bpy.ops.wm.obj_import(
                    filepath=os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj'),
                    forward_axis='NEGATIVE_Z',
                    up_axis='Y',
                    global_scale=scale_factor,
                    filter_glob="*.obj;*.mtl"
                )
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                if addon_prefs.apply_transform:
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
                for obj in bpy.context.selected_objects:
                    if obj.type == 'CURVE':
                        if addon_prefs.sna_import_curves==False:
                            bpy.data.objects.remove(obj, do_unlink=True)
                for obj in bpy.context.selected_objects:
                    if obj.type == 'MESH' and not obj.data.polygons:
                        bpy.data.objects.remove(obj, do_unlink=True)
                imported_objects = [obj for obj in bpy.context.selected_objects]
                mesh_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
                curve_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'CURVE']

                if imported_objects:
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
                        newww_name= new_name
                        last_matching_obj = None
                        for existing_obj in current_parent_collection.objects:
                            if existing_obj == obj:
                                continue  
                            if "@" in existing_obj.data.name:
                                chackdate_name = existing_obj.data.name.split("@")[0]
                            else:
                                chackdate_name = existing_obj.data.name
                            if newww_name == chackdate_name and existing_obj != obj:
                                last_matching_obj = existing_obj
                        if last_matching_obj:

                            oldname=last_matching_obj.name
                            last_matching_data = bpy.data.objects[last_matching_obj.name].data
                            try:
                                materials_copy = obj.data.materials[:]
                                obj.data.materials.clear()  

                                for material in materials_copy:
                                    if material.users == 0:
                                        bpy.data.materials.remove(material)
                                for slot in last_matching_obj.material_slots:
                                    if slot.material:
                                        new_material = slot.material
                                        obj.data.materials.append(new_material)
                            except:
                                pass
                            last_matching_obj.name =last_matching_obj.name+"(backup)"
                            last_matching_obj.data.name = new_name+"@"+date_time
                            obj.name =oldname
                            obj.data.name = new_name+"@"+date_time
                            if last_matching_obj.name in bpy.context.scene.objects and  last_matching_obj.name in current_parent_collection.objects:
                                for collection in bpy.data.collections:
                                    if last_matching_obj.name in collection.objects:
                                        collection.objects.unlink(last_matching_obj)
                                if addon_prefs.sna_use_rhinobackup:
                                    backup_collection.objects.link(last_matching_obj)

                        else:
                            obj.name = new_name
                            obj.data.name = new_name+"@"+date_time
                    end_time = datetime.now()
                    elapsed_time = round((end_time - self.start_time).total_seconds(), 3)                
                    static_string = "Imported {} meshs and {} curves from {}.3dm,took {} s"
                    translated_string = bpy.app.translations.pgettext(static_string)
                    formatted_string = translated_string.format(len(mesh_objects),len(curve_objects), common_name1,elapsed_time)
                    self.report({'INFO'}, formatted_string)

                else:
                    self.report({'INFO'}, "No mesh or curves in Rhino to Blender-mesh.obj！")  
        else:
            static_string = "Fichier {} does not exist. Please export it from Rhino first."
            translated_string = bpy.app.translations.pgettext(static_string)
            formatted_string = translated_string.format(file_path)
            self.report({'INFO'}, formatted_string)
        bpy.context.scene.cycles.preview_pause = False

        scene = bpy.context.scene
        depsgraph = bpy.context.evaluated_depsgraph_get()
        disable_collection_for_render(scene, depsgraph)
        clean_objbak()
        return {'FINISHED'}

def clean_objbak():
    folder_path = os.path.join(os.path.dirname(__file__), 'assets')
    for filename in os.listdir(folder_path):
        if filename.endswith('.objbak'):
            file_path = os.path.join(folder_path, filename)
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"删除文件 {file_path} 失败：{e}")
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

class RHINO_OT_add_object_empt(Operator, AddObjectHelper):
    bl_idname = "rhino.add_object_empt"
    bl_label = "Import obj from Rhino by emptys!"
    bl_description = "Import obj from Rhino,Use emptys instead of layers!"
    bl_options = {'UNDO'}

    def __init__(self):
        self.root_empty = False

    def invoke(self, context, event):
        self.start_time = 0
        wm = context.window_manager
        addon_prefs = context.preferences.addons[__name__].preferences
        if addon_prefs.show_import_plane:
            return wm.invoke_props_dialog(self, width=300)
        else:
            return self.execute(context)

    def draw(self, context):
        layout = self.layout
        addon_prefs = context.preferences.addons[__name__].preferences
        box_750F6 = layout.box()
        box_750F6=box_750F6.column(heading='', align=True)
        box_750F6.scale_y = 1.35
        box_750F6.prop(addon_prefs, "scale_option", text='', icon="SMALL_CAPS", emboss=True)
        box_750F6.prop(addon_prefs, "apply_transform", emboss=True)

        layout.prop(addon_prefs, "sna_use_rhinobackup", emboss=True)
        layout.prop(addon_prefs, "sna_autohide_render", emboss=True)
        layout.prop(addon_prefs, "show_import_plane",text='Show panel before import(Turn on again in preferences)', emboss=True)
        layout.separator()

    def execute(self, context):
        now = datetime.now()
        date_time = now.strftime("%m/%d/%H:%M:%S")
        self.start_time = datetime.now()
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        bpy.context.scene.cycles.preview_pause = True
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection  
        scene_name = bpy.context.scene.name 
        scale_factor = float(addon_prefs.scale_option)
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj')
        if os.path.exists(file_path):
            object_names = []
            with open(file_path, 'r') as obj_file:
                for line in obj_file:
                    if line.startswith("o "):
                        object_name = line[2:].strip()  
                        object_names.append(object_name)
            common_name = None
            common_name1 = None

            original_location = None
            original_rotation = None
            original_scale = None

            imported_objects = None
            mesh_objects = None
            curve_objects = None

            current_parent_empty = None

            if object_names:
                longest_exceeding_name = ""
                for name in object_names:
                    name_byte_length = len(name.encode('utf-8'))
                    if name_byte_length > 64:
                        if len(name) > len(longest_exceeding_name):
                            longest_exceeding_name = name       
                if longest_exceeding_name:
                    self.report({'WARNING'},rpt_("The name length exceeds the maximum length allowed by blender, you can shorten the Rhino filename or layer name! (%s)") % (longest_exceeding_name))
                    print(rpt_("The name length exceeds the maximum length allowed by blender, you can shorten the Rhino filename or layer name! (%s)") % (longest_exceeding_name))
                    return {'FINISHED'}

                common_name1 = object_names[0].split('/')[0]
                common_name = f"{common_name1}+[{scene_name}]"
                root_empty = None
                root_coll = None
                for empty in [obj for obj in bpy.context.scene.objects if obj.type == 'EMPTY']:
                    if empty.name == common_name:
                        root_empty = empty
                        break
                    elif common_name1 in empty.name and empty.name != common_name:
                        empty.name = common_name
                        root_empty = empty
                        break

                if root_empty:
                    for collection in bpy.data.collections:
                        if root_empty.name in collection.objects:
                            root_coll = collection
                            break

                    if root_coll:
                        top_collections = bpy.context.view_layer.layer_collection.children
                        found_collection_a = False
                        for collection in top_collections:
                            if collection.name == root_coll.name:
                                collection.exclude = False
                                found_collection_a = True
                            else :
                                if find_and_unexclude_collection(collection,root_coll.name):
                                    found_collection_a = True
                        if found_collection_a:
                            unexclude_subcollections(root_coll, exclude=False)
                if root_empty is None:
                    self.root_empty = True
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
                root_empty.hide_viewport = False
                root_empty.hide_select = False
                parent_names=turn_collection_hierarchy_into_path(root_empty)
                for coll in parent_names:
                    fathercoll = bpy.data.collections.get(coll)
                    if fathercoll:
                        fathercoll.hide_viewport = False
                        fathercoll.hide_select = False
                if addon_prefs.sna_use_rhinobackup:
                    backupname = "Rhino_backup"
                    backupcolname = f"{backupname}[{scene_name}]"
                    backup_collection = None
                    backup_collection = context.scene.collection.children.get(backupcolname)
                    if not backup_collection:
                        for collection in bpy.context.scene.collection.children:
                            if backupname in collection.name:
                                if collection.name != backupcolname:
                                    collection.name = backupcolname
                                backup_collection = collection
                                break         
                    if not backup_collection:
                        backup_collection = bpy.data.collections.new(backupcolname)
                        backup_collection.color_tag = 'COLOR_01'
                        bpy.context.scene.collection.children.link(backup_collection)
                bpy.context.view_layer.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')

                if root_coll is not None: 
                    layer_collection = bpy.context.view_layer.layer_collection
                    layerColl = recurLayerCollection(layer_collection, root_coll.name)
                    bpy.context.view_layer.active_layer_collection = layerColl       
                else :
                    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
                bpy.ops.wm.obj_import(
                    filepath=os.path.join(os.path.dirname(__file__), 'assets', 'Rhino to Blender-mesh.obj'),
                    forward_axis='NEGATIVE_Z',
                    up_axis='Y',
                    global_scale=scale_factor,
                    filter_glob="*.obj;*.mtl"
                )
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                if addon_prefs.apply_transform:
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
                for obj in bpy.context.selected_objects:
                    if obj.type == 'CURVE':
                        if addon_prefs.sna_import_curves==False:
                            bpy.data.objects.remove(obj, do_unlink=True)
                for obj in bpy.context.selected_objects:
                    if obj.type == 'MESH' and not obj.data.polygons:
                        bpy.data.objects.remove(obj, do_unlink=True)
                imported_objects = [obj for obj in bpy.context.selected_objects]
                mesh_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
                curve_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'CURVE']

                if imported_objects:
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
                        newww_name= new_name
                        last_matching_obj = None
                        for existing_obj in current_parent_empty.children:
                            if existing_obj == obj:
                                continue  
                            if "@" in existing_obj.data.name:
                                chackdate_name = existing_obj.data.name.split("@")[0]
                            else:
                                chackdate_name = existing_obj.data.name
                            if newww_name == chackdate_name and existing_obj != obj:
                                last_matching_obj = existing_obj
                        if last_matching_obj:
                            last_matching_data = bpy.data.objects[last_matching_obj.name].data
                            oldname=last_matching_obj.name
                            try:
                                materials_copy = obj.data.materials[:]
                                obj.data.materials.clear()  
                                for material in materials_copy:
                                    if material.users == 0:
                                        bpy.data.materials.remove(material)
                                for slot in last_matching_obj.material_slots:
                                    if slot.material:
                                        new_material = slot.material
                                        obj.data.materials.append(new_material)
                            except:
                                pass
                            last_matching_obj.name =last_matching_obj.name+"(backup)"
                            last_matching_obj.data.name = new_name+"@"+date_time
                            obj.name =oldname
                            obj.data.name = new_name+"@"+date_time

                            all_coll = bpy.data.collections[:]
                            all_coll.append(bpy.context.scene.collection)
                            for collection in all_coll:
                                obj=last_matching_obj
                                if obj.name in collection.objects:
                                    bpy.ops.object.select_all(action='DESELECT')  
                                    obj.select_set(True)
                                    bpy.context.view_layer.objects.active = obj
                                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                                    collection.objects.unlink(obj)

                            if addon_prefs.sna_use_rhinobackup:
                                backup_collection.objects.link(last_matching_obj)

                        else :
                            obj.name = new_name
                            obj.data.name = new_name+"@"+date_time
                    end_time = datetime.now()
                    elapsed_time = round((end_time - self.start_time).total_seconds(), 3)                
                    static_string = "Imported {} meshs and {} curves from {}.3dm,took {} s"
                    translated_string = bpy.app.translations.pgettext(static_string)
                    formatted_string = translated_string.format(len(mesh_objects),len(curve_objects), common_name1,elapsed_time)
                    self.report({'INFO'}, formatted_string)

                else:
                    self.report({'INFO'}, "No mesh or curves in Rhino to Blender-mesh.obj！")

                try:
                    if original_location and original_rotation and original_scale:
                        root_empty.location = original_location
                        root_empty.rotation_euler = original_rotation
                        root_empty.scale = original_scale

                    if current_parent_empty:
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.context.view_layer.objects.active = current_parent_empty
                        current_parent_empty.select_set(True)
                except Exception as e:
                    pass
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = root_empty
                root_empty.select_set(True)
                if self.root_empty == True:
                    try:
                        bpy.ops.object.emptytocoll_70dbd('INVOKE_DEFAULT')
                        bpy.ops.object.colltoempty_70dbd('INVOKE_DEFAULT')
                    except:
                        pass

            else:
                self.report({'INFO'}, "No object in Rhino to Blender-mesh.obj !")
        else:
            static_string = "Fichier {} does not exist. Please export it from Rhino first."
            translated_string = bpy.app.translations.pgettext(static_string)
            formatted_string = translated_string.format(file_path)
            self.report({'INFO'}, formatted_string)
        scene = bpy.context.scene
        depsgraph = bpy.context.evaluated_depsgraph_get()
        disable_collection_for_render(scene, depsgraph)
        bpy.context.scene.cycles.preview_pause = False
        clean_objbak()
        return {'FINISHED'}
def get_parent_collection_names(collection, parent_names):
    for parent_collection in bpy.data.collections:
        if collection.name in parent_collection.children.keys():
          parent_names.append(parent_collection.name)
          get_parent_collection_names(parent_collection, parent_names)
          return
def turn_collection_hierarchy_into_path(obj):
    parent_collection = obj.users_collection[0]
    parent_names      = []
    parent_names.append(parent_collection.name)
    get_parent_collection_names(parent_collection, parent_names)
    parent_names.reverse()
    return parent_names

def sna_add_to_view3d_mt_add_7D1A0(self, context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    if not (False):
        layout = self.layout
        layout.separator()
        op = layout.operator_context = "INVOKE_DEFAULT"
        op = layout.operator('rhino.add_object_coll', text='Import4Rhino(coll)', icon_value=_icons['SmallTile.png'].icon_id, emboss=True, depress=False)

        op = layout.operator('rhino.add_object_empt', text='Import4Rhino(empt)', icon_value=_icons['SmallTile.png'].icon_id, emboss=True, depress=False)
        if addon_prefs.sna_show_export2rhino:
            op = layout.operator('mesh.add_objectexport', text='Export2Rhino', icon_value=_icons['MediumTile.png'].icon_id, emboss=True, depress=False)

class OBJECT_OT_add_objectexport(Operator, AddObjectHelper):
    """导出到Rhino Mesh对象"""
    bl_idname = "mesh.add_objectexport"
    bl_label = "Export Mesh Obj"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        wm = context.window_manager
        addon_prefs = context.preferences.addons[__name__].preferences
        if addon_prefs.show_export_plane:
            return wm.invoke_props_dialog(self, width=220)
        else:
            return self.execute(context)

    def draw(self, context):
        layout = self.layout
        addon_prefs = context.preferences.addons[__name__].preferences
        row = layout.row()
        box1 = row.box()
        box1.prop(addon_prefs, "export_selected_objects")
        box1.prop(addon_prefs, "global_scale")
        box1.prop(addon_prefs, "forward_axis")
        box1.prop(addon_prefs, "up_axis")
        box1.prop(addon_prefs, "apply_modifiers")
        box1.prop(addon_prefs, "export_eval_mode")

        box = box1.row(align=True)
        box = box.box()
        box.prop(addon_prefs, "export_uv")
        box.prop(addon_prefs, "export_normals")
        box.prop(addon_prefs, "export_colors")
        box.prop(addon_prefs, "export_triangulated_mesh")
        box.prop(addon_prefs, "export_curves_as_nurbs")

        box = box1.row(align=True)
        box = box.box()
        box.prop(addon_prefs, "export_materials")
        box.prop(addon_prefs, "export_pbr_extensions")

        box = box1.row(align=True)
        box = box.box()
        box.prop(addon_prefs, "export_object_groups")
        box.prop(addon_prefs, "export_material_groups")
        box.prop(addon_prefs, "export_vertex_groups")
        box.prop(addon_prefs, "export_smooth_groups")
        if addon_prefs.export_smooth_groups:
            box.prop(addon_prefs, "smooth_group_bitflags")

        layout.prop(addon_prefs, "show_export_plane",text='Show panel before export(Turn on again in preferences)', emboss=True)
        layout.separator()

    def execute(self, context): 
        addon_prefs = context.preferences.addons[__name__].preferences      
        print("Exporting...")
        bpy.ops.wm.obj_export(
            filepath=os.path.join(os.path.dirname(__file__), 'assets', 'Blender to Rhino-mesh.obj'),
            export_selected_objects=addon_prefs.export_selected_objects,
            global_scale=addon_prefs.global_scale,
            forward_axis=addon_prefs.forward_axis,
            up_axis=addon_prefs.up_axis,
            apply_modifiers=addon_prefs.apply_modifiers,
            export_eval_mode=addon_prefs.export_eval_mode,
            export_uv=addon_prefs.export_uv,
            export_normals=addon_prefs.export_normals,
            export_colors=addon_prefs.export_colors,
            export_triangulated_mesh=addon_prefs.export_triangulated_mesh,
            export_curves_as_nurbs=addon_prefs.export_curves_as_nurbs,
            export_materials=addon_prefs.export_materials,
            export_pbr_extensions=addon_prefs.export_pbr_extensions,
            path_mode=addon_prefs.path_mode,
            export_object_groups=addon_prefs.export_object_groups,
            export_material_groups=addon_prefs.export_material_groups,
            export_vertex_groups=addon_prefs.export_vertex_groups,
            export_smooth_groups=addon_prefs.export_smooth_groups,
            smooth_group_bitflags=addon_prefs.smooth_group_bitflags,
        )
        return {'FINISHED'}

import textwrap
class RHINO_OT_CopyExportMacro(Operator):
    bl_idname = "rhino.copy_export_macro"
    bl_label = "Copy Rhino Export Macro Command"
    bl_description = "Paste the command directly into Rhino after copied"

    def execute(self, context):
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        assets_folder_path = os.path.join(addon_dir, 'assets')
        command = textwrap.dedent(f"""\
            -_rename_objrhino
            NoEcho
            -_Export _GeometryOnly=_Yes _SaveTextures=_No _SaveNotes=_No _SaveSmall=_Yes
            "{assets_folder_path}\\Rhino to Blender-mesh.obj"
            _VertexWelding=_Welded  _YUp=_Yes _Geometry=_Mesh _UseRenderMeshes=_Yes _NgonMode=_Preserve
            _ExportRhinoObjectNames=_ExportObjectsAsOBJObjects 
            _ExportRhinoGroupOrLayerNames=_ExportLayersAsOBJGroups
            _MergeNestedLayerGroupNames=_No  
            _SortByOBJGroups=_Yes  _ExportMaterialDefinitions=_Yes  _ChangeWhitespaceToUnderscores=_No  
            _UseDisplayColorForMaterial=_Yes  _WrapLongLines=_No  _WritePrecision=17  
            _ExportMeshTextureCoordinates=_Yes  _ExportMeshVertexNormals=_Yes  
            _ExportMeshVertexColors=_No  _ExportOpenMeshes=_Yes  _ExportMeshAsTriangles=_No  
            _SubDMeshing=_FromSurface  _SubDLevel=1
            enter
        """)
        bpy.context.window_manager.clipboard = command.strip()
        self.report({'INFO'}, f"Rhino macro command copied to clipboard！")
        return {'FINISHED'}

class RHINO_OT_CopyImportMacro(Operator):
    bl_idname = "rhino.copy_import_macro"
    bl_label = "Copy Rhino Import Macro Command"
    bl_description = "Paste the command directly into Rhino after copied"

    def execute(self, context):
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        assets_folder_path = os.path.join(addon_dir, 'assets')
        command = textwrap.dedent(f"""\
            !NoEcho -_Import
            "{assets_folder_path}\\Blender to Rhino-mesh.obj"
            _MapYtoZ=_Yes
            enter
        """)
        bpy.context.window_manager.clipboard = command.strip()
        self.report({'INFO'}, f"Rhino macro command copied to clipboard！")
        return {'FINISHED'}

import subprocess
class RHINO_OT_OpenAssetsExplorer(Operator):
    bl_idname = "rhino.open_assets_explorer"
    bl_label = "Open assets explorer"
    bl_description = ""

    def execute(self, context):
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        assets_folder_path = os.path.join(addon_dir, 'assets')
        if os.name == 'nt':  
            subprocess.Popen(['explorer', assets_folder_path.replace('/', '\\')])
        elif os.name == 'posix':  
            subprocess.Popen(['xdg-open', assets_folder_path])

        return {'FINISHED'}

class SNA_AddonPreferences_9F6AA(bpy.types.AddonPreferences):
    bl_idname = __name__
    show_import_plane: bpy.props.BoolProperty(
        name='Show options plane before import',
        description='Always show options panel before import',
        default=True
    )
    show_export_plane: bpy.props.BoolProperty(
        name='Show options plane before export',
        description='Always Show options panel before export',
        default=True
    )
    sna_show_export2rhino: bpy.props.BoolProperty(
        name='Show Export2Rhino',
        description='Whether to display the export button in the right-click menu',
        default=False
    )
    sna_use_rhinobackup: bpy.props.BoolProperty(
        name='Move replaced objs to \'Rhino_backup\' coll after updating.',
        description='',
        default=True
    )
    sna_autohide_render: bpy.props.BoolProperty(
        name='Auto hide \'Rhino_backup\' coll before render.',
        description='',
        default=True
    )
    scale_option: bpy.props.EnumProperty(
        items=[
        ("1", "1.0(mm ⇉ m)", "Scale by 1.0"),
        ("0.1", "0.1(mm ⇉ cm)", "Scale by 0.1"),
        ("0.01", "0.01(mm ⇉ mm)", "Scale by 0.01"),
        ("0.001", "0.001", "Scale by 0.001"),
        ],
        name="Scale",
        description="Select the scaling factor",
        default="0.01"  
    )
    apply_transform: bpy.props.BoolProperty(
        name="Apply Scale",
        description="Apply transform after scaling",
        default=True
    )

    sna_import_curves: bpy.props.BoolProperty(
        name='Import Curves.',
        description='',
        default=False
    )
    export_selected_objects: BoolProperty(
        name="Export Selected Only", 
        description="Export only selected objects instead of all supported objects", 
        default=True
    )
    global_scale: FloatProperty(
        name="Scale", 
        description="Value by which to enlarge or shrink the objects with respect to the world’s origin", 
        default=100.0,
        min=0.0001,
        max=10000
    )
    forward_axis: EnumProperty(
        name="Forward Axis", 
        description="Forward Axis", 
        items=(
            ('X', "X", "Positive X axis."),
            ('Y', "Y", "Positive Y axis."),
            ('Z', "Z", "Positive Z axis."),
            ('NEGATIVE_X', "-X", "Negative X axis."),
            ('NEGATIVE_Y', "-Y", "Negative Y axis."),
            ('NEGATIVE_Z', "-Z", "Negative Z axis.")
        ),
        default='NEGATIVE_Z'
    )
    up_axis: EnumProperty(
        name="Up Axis", 
        description="Up Axis", 
        items=(
            ('X', "X", "Positive X axis."),
            ('Y', "Y", "Positive Y axis."),
            ('Z', "Z", "Positive Z axis."),
            ('NEGATIVE_X', "-X", "Negative X axis."),
            ('NEGATIVE_Y', "-Y", "Negative Y axis."),
            ('NEGATIVE_Z', "-Z", "Negative Z axis.")
        ),
        default='Y'
    )

    apply_modifiers: BoolProperty(
        name="Apply Modifiers", 
        description="Apply modifiers to exported meshes", 
        default=True
    )
    export_eval_mode: EnumProperty(
        name="Object Properties", 
        description="Determines properties like object visibility, modifiers etc., where they differ for Render and Viewport", 
        items=(
            ('DAG_EVAL_RENDER', "Render", "Export objects as they appear in render."), 
            ('DAG_EVAL_VIEWPORT', "Viewport", "Export objects as they appear in the viewport.") 
        ),
        default='DAG_EVAL_RENDER'
    )

    export_uv: BoolProperty(
        name="Export UVs", 
        description="Export UVs", 
        default=True
    )
    export_normals: BoolProperty(
        name="Export Normals", 
        description="Export per-face normals if the face is flat-shaded, per-face-per-loop normals if smooth-shaded", 
        default=True
    )
    export_colors: BoolProperty(
        name="Export Colors", 
        description="Export per-vertex colors", 
        default=True
    )
    export_triangulated_mesh: BoolProperty(
        name="Export Triangulated Mesh", 
        description="All ngons with four or more vertices will be triangulated. Meshes in the scene will not be affected.", 
        default=False
    )
    export_curves_as_nurbs: BoolProperty(
        name="Export Curves as NURBS", 
        description="Export curves in parametric form instead of exporting as mesh", 
        default=False
    )

    export_materials: BoolProperty(
        name="Export Materials", 
        description="Export MTL library. There must be a Principled-BSDF node for image textures to be exported to the MTL file", 
        default=True
    )
    export_pbr_extensions: BoolProperty(
        name="Export Materials with PBR Extensions", 
        description="Export MTL library using PBR extensions (roughness, metallic, sheen, coat, anisotropy, transmission)", 
        default=False
    )
    path_mode: EnumProperty(
        name="Path Mode", 
        description="Method used to reference paths", 
        items=(
            ('AUTO', "Auto", "Use relative paths with subdirectories only."), 
            ('ABSOLUTE', "Absolute", "Always write absolute paths."), 
            ('RELATIVE', "Relative", "Write relative paths where possible."), 
            ('MATCH', "Match", "Match absolute/relative setting with input path."), 
            ('STRIP', "Strip", "Write filename only."), 
            ('COPY', "Copy", "Copy the file to the destination path.") 
        ),
        default='AUTO'
    )

    export_object_groups: BoolProperty(
        name="Export Object Groups", 
        description="Append mesh name to object name, separated by a ‘_’", 
        default=False
    )
    export_material_groups: BoolProperty(
        name="Export Material Groups", 
        description="Generate an OBJ group for each part of a geometry using a different material", 
        default=False
    )
    export_vertex_groups: BoolProperty(
        name="Export Vertex Groups", 
        description="Export the name of the vertex group of a face. It is approximated by choosing the vertex group with the most members among the vertices of a face", 
        default=False
    )
    export_smooth_groups: BoolProperty(
        name="Export Smooth Groups", 
        description="Every smooth-shaded face is assigned group “1” and every flat-shaded face “off”", 
        default=False
    )
    smooth_group_bitflags: BoolProperty(
        name="Generate Bitflags for Smooth Groups", 
        description="Generate Bitflags for Smooth Groups", 
        default=False
    )
    def draw(self, context):
        layout = self.layout
        box_000 = layout.box()
        row_707B7 = box_000.split(factor=0.5, align=True)
        box_750F6 = row_707B7.box()

        box_750F6.label(text='Rhino', icon_value=_icons['SmallTile.png'].icon_id)
        box_750F6.label(text='Don`t manually change object name,Use Command:rename_selected_obj_for_blender', icon_value=17)
        box_750F6.label(text='After modifying the object·s layer, the previous import will not be automatically replaced', icon_value=17)
        box_750F6.label(text='After modifying the layer name, it will be re-imported and the previous import will not be automatically recognized', icon_value=17)
        box_750F6.label(text='Don`t include the marks [/: *.] in the object name,they will be automatically replaced', icon_value=17)

        row = box_750F6.row(heading='123', align=False)
        row.operator('rhino.copy_export_macro', icon="MOUSE_LMB", emboss=True, depress=False)
        row.operator('rhino.copy_import_macro', icon="MOUSE_RMB", emboss=True, depress=False)
        row.operator('rhino.open_assets_explorer', icon="FILEBROWSER", emboss=True, depress=False)

        box_80C44 = row_707B7.box()
        box_80C44.label(text='Blender', icon_value=15)
        box_80C44.label(text="Don\'t use shade smooth on the mesh, as its display is determined by the rendered mesh in Rhino!", icon_value=17)
        box_80C44.label(text="You can change the object name, but don\'t change the object\'s grid name! Otherwise the update will fail!", icon_value=17)
        box_80C44.label(text='If you want to re-import and keep the imported, change the RhinoName in the name of the empty or collection called "RhinoName+[Scene]"!', icon_value=17)       
        box_80C44.label(text="By empty parent,Adjust only the root parent and don\'t apply all three transformations. Only then will the update be automatically aligned", icon_value=17)
        box_80C44.label(text='If import as collection, Do`t apply scale/location/rotation, so that the updated imported objects will automatically align with the replaced objects.', icon_value=17)

        box_000.prop(self, 'show_import_plane')
        box_000.prop(self, 'show_export_plane')
        box_000.prop(self, 'sna_import_curves')
        box_000.prop(self, 'sna_use_rhinobackup')
        box_000.prop(self, 'sna_autohide_render')
        box_000.prop(self, 'sna_show_export2rhino')
        if self.sna_show_export2rhino:
            row = box_000.row()
            box1 = row.box()
            box1.prop(self, "export_selected_objects")
            box1.prop(self, "global_scale")
            box1.prop(self, "forward_axis")
            box1.prop(self, "up_axis")
            box1.prop(self, "apply_modifiers")
            box1.prop(self, "export_eval_mode")

            box = box1.row(align=True)
            box = box.box()
            box.prop(self, "export_uv")
            box.prop(self, "export_normals")
            box.prop(self, "export_colors")
            box.prop(self, "export_triangulated_mesh")
            box.prop(self, "export_curves_as_nurbs")

            box = box1.row(align=True)
            box = box.box()
            box.prop(self, "export_materials")
            box.prop(self, "export_pbr_extensions")

            box = box1.row(align=True)
            box = box.box()
            box.prop(self, "export_object_groups")
            box.prop(self, "export_material_groups")
            box.prop(self, "export_vertex_groups")
            box.prop(self, "export_smooth_groups")
            if self.export_smooth_groups:
                box.prop(self, "smooth_group_bitflags")

        layout = self.layout 
        box_0CD4E = layout.box()
        box_0CD4E.scale_y = 0.7
        box_0CD4E.label(text='More', icon_value=206)
        box_0CD4E.label(text='A plug-in that can be converted between the collection and the empty object hierarchy!', icon_value=227)
        box_0CD4E.label(text='Move the empty at the center of the sub-level objects instead of the center of the world coordinates!', icon_value=227)

        row_D6666 = box_0CD4E.row(heading='', align=True)
        row_D6666.scale_y = 1.5
        op = row_D6666.operator('wm.url_open', text='Empty & Collection Switcher', icon="SCRIPTPLUGINS", emboss=True, depress=False)
        op.url = 'https://blendermarket.com/products/empty--collection-switcher'
        box_0CD4E.separator(factor=1.0)
        row_C73A8 = box_0CD4E.row(heading='', align=True)
        row_C73A8.scale_y = 1.5
        op = row_C73A8.operator('wm.url_open', text='Rhino to Blender', icon_value=_icons['SmallTile.png'].icon_id, emboss=True, depress=False)
        op.url = 'https://blenderartists.org/t/free-addon-rhino-to-blender-quickly-export-rhino-models-to-blender/1489621'

        op = row_C73A8.operator('wm.url_open', text='Blender Market', icon_value=_icons['blenderartists.png'].icon_id, emboss=True, depress=False)
        op.url = 'https://blendermarket.com/creators/cp-design'
        op = row_C73A8.operator('wm.url_open', text='Github', icon_value=_icons['icons8-github-100.png'].icon_id, emboss=True, depress=False)
        op.url = 'https://github.com/chenpaner'
        op = row_C73A8.operator('wm.url_open', text='BiLiBiLi', icon_value=_icons['bilibili.png'].icon_id, emboss=True, depress=False)
        op.url = 'https://space.bilibili.com/2711518?spm_id_from=333.1007.0.0'
        op = row_C73A8.operator('wm.url_open', text='Youtube', icon_value=_icons['youtube.png'].icon_id, emboss=True, depress=False)
        op.url = 'https://www.youtube.com/channel/UCb4bdeOqaXHLnSr9HGu63Ew'

langs = {
    'zh_HANS': {
        ('*', 'Only if the M3 plugin is installed will the root parent empty object be converted to an M3 empty object!'): '装了M3插件才会自动将空物体转为M3类型的父级空物体!',
        ('*', 'Imported {} meshs and {} curves from {}.3dm,took {} s'): '导入 {} 个网格 {} 条曲线 从{}.3dm里,用时{}秒。',
        ('*', 'No mesh or curves in Rhino to Blender-mesh.obj！'): 'Rhino to Blender-mesh.obj里没有网格或者线条！',
        ('*', 'Fichier {} does not exist. Please export it from Rhino first.'): '文件{}不存在，请先从 Rhino 中导出。',
        ('*', 'Don`t include the marks [/: *.] in the object name,they will be automatically replaced'): '物体名里不要出现[/ : * .]这四个标点符号,它会被自动替换',

        ('*', 'Don`t manually change object name,Use Command:rename_selected_obj_for_blender'): 
        '不要手动修改物体名字,用rename_selected_obj_for_blender命令修改',
        ('*', 'After modifying the object·s layer, the previous import will not be automatically replaced'): 
        '修改物体图层后不会自动替换之前的导入',
        ('*', 'After modifying the layer name, it will be re-imported and the previous import will not be automatically recognized'): 
        '修改图层名字后会重新导入不会自动识别之前的导入',

        ('*', 'If you want to re-import and keep the imported, change the RhinoName in the name of the empty or collection called "RhinoName+[Scene]"!'): 
        '如果要重新导入并且保留导入过的,就将叫“RhinoName+[Scene]”的空物体或集合名字里RhinoName完全修改！',

        ('*', 'You can change the object name, but don\'t change the object\'s grid name! Otherwise the update will fail!'): 
        '你可以修改物体名字，但不要修改物体的网格名!不然更新会失败！',
        ('*', 'Don\'t use shade smooth on the mesh, as its display is determined by the rendered mesh in Rhino!'): 
        '不要对网格用平滑着色,显示效果由Rhino里的渲染网格决定',

        ('*', 'By empty parent,Adjust only the root parent and don\'t apply all three transformations. Only then will the update be automatically aligned'): 
        '以空物体为父级的方式尽量只调整根父级,且不用应用三个变换,只有这样更新导入才会自动对齐',

        ('*', 'If import as collection, Do`t apply scale/location/rotation, so that the updated imported objects will automatically align with the replaced objects.'): 
        '以集合方式导入的,修改每个物体的位置缩放旋转后尽量别应用这3个变换,这样更新导入后的物体才会自动对齐替换的物体',

        ('*', 'A plug-in that can be converted between the collection and the empty object hierarchy!'): 
        '可以在集合与空物体层级之间相互转换的插件',

        ('*', 'Move the empty at the center of the sub-level objects instead of the center of the world coordinates!'): 
        '可以让空物体位于子级物体的中心，而不是世界坐标的中心!',

        ('*', 'Show Export2Rhino'): '在右键菜单里显示导出到Rhino',
        ('*', 'Import Curves.'): '导入曲线',

        ('*', 'Move replaced objs to \'Rhino_backup\' coll after updating.'): 
        '更新后将被替换的物体移动到\'Rhino_backup\'集合',

        ('*', 'Auto hide \'Rhino_backup\' coll before render.'): 
        '渲染前自动隐藏\'Rhino_backup\'集合',

        ('Operator', 'Import4Rhino(coll)'): 'Rhino导入(集合)',
        ('Operator', 'Import4Rhino(empt)'): 'Rhino导入(空物体)',

        ('Operator', 'Import obj from Rhino by collection!'): 'Rhino导入(图层转集合)',
        ('Operator', 'Import obj from Rhino by emptys!'): 'Rhino导入(图层转空物体父级)',

        ('*', 'Show panel before import(Turn on again in preferences)'): '导入前显示该面板(插件首选项里可再次打开)',
        ('*', 'Show panel before export(Turn on again in preferences)'): '导出前显示该面板(插件首选项里可再次打开)',
        ('*', 'Show options plane before import'): '每次导入前显示导入选项面板',
        ('*', 'Show options plane before export'): '每次导出前显示导出选项面板',

        ('Operator', 'Copy Rhino Export Macro Command'): '复制Rhino里导出的巨集命令',
        ('Operator', 'Copy Rhino Import Macro Command'): '复制Rhino里导入的巨集命令',
        ('*', 'Paste the command directly into Rhino after copied'): '复制后直接去Rhino里去粘贴命令吧',
        ('Operator', 'Open assets explorer'): '打开Assets文件夹',

        ('*', 'The name length exceeds the maximum length allowed by blender, you can shorten the Rhino filename or layer name! (%s)'):
         '名称长度超过Blender允许的最大长度，请缩短Rhino文件名或图层名！让这个长度不超过64字符(中文算3个字符) (%s)',
    }, 
    'zh_CN': {
        ('*', 'Only if the M3 plugin is installed will the root parent empty object be converted to an M3 empty object!'): '装了M3插件才会自动将空物体转为M3类型的父级空物体!',
        ('*', 'Imported {} meshs and {} curves from {}.3dm,took {} s'): '导入 {} 个网格 {} 条曲线 从{}.3dm里,用时{}秒。',
        ('*', 'No mesh or curves in Rhino to Blender-mesh.obj！'): 'Rhino to Blender-mesh.obj里没有网格或者线条！',
        ('*', 'Fichier {} does not exist. Please export it from Rhino first.'): '文件{}不存在，请先从 Rhino 中导出。',
        ('*', 'Don`t include the marks [/: *.] in the object name,they will be automatically replaced'): '物体名里不要出现[/ : * .]这四个标点符号,它会被自动替换',

        ('*', 'Don`t manually change object name,Use Command:rename_selected_obj_for_blender'): 
        '不要手动修改物体名字,用rename_selected_obj_for_blender命令修改',
        ('*', 'After modifying the object·s layer, the previous import will not be automatically replaced'): 
        '修改物体图层后不会自动替换之前的导入',
        ('*', 'After modifying the layer name, it will be re-imported and the previous import will not be automatically recognized'): 
        '修改图层名字后会重新导入不会自动识别之前的导入',

        ('*', 'If you want to re-import and keep the imported, change the RhinoName in the name of the empty or collection called "RhinoName+[Scene]"!'): 
        '如果要重新导入并且保留导入过的,就将叫“RhinoName+[Scene]”的空物体或集合名字里RhinoName完全修改！',

        ('*', 'You can change the object name, but don\'t change the object\'s grid name! Otherwise the update will fail!'): 
        '你可以修改物体名字，但不要修改物体的网格名!不然更新会失败！',
        ('*', 'Don\'t use shade smooth on the mesh, as its display is determined by the rendered mesh in Rhino!'): 
        '不要对网格用平滑着色,显示效果由Rhino里的渲染网格决定',

        ('*', 'By empty parent,Adjust only the root parent and don\'t apply all three transformations. Only then will the update be automatically aligned'): 
        '以空物体为父级的方式尽量只调整根父级,且不用应用三个变换,只有这样更新导入才会自动对齐',

        ('*', 'If import as collection, Do`t apply scale/location/rotation, so that the updated imported objects will automatically align with the replaced objects.'): 
        '以集合方式导入的,修改每个物体的位置缩放旋转后尽量别应用这3个变换,这样更新导入后的物体才会自动对齐替换的物体',

        ('*', 'A plug-in that can be converted between the collection and the empty object hierarchy!'): 
        '可以在集合与空物体层级之间相互转换的插件',

        ('*', 'Move the empty at the center of the sub-level objects instead of the center of the world coordinates!'): 
        '可以让空物体位于子级物体的中心，而不是世界坐标的中心!',

        ('*', 'Show Export2Rhino'): '在右键菜单里显示导出到Rhino',
        ('*', 'Import Curves.'): '导入曲线',

        ('*', 'Move replaced objs to \'Rhino_backup\' coll after updating.'): 
        '更新后将被替换的物体移动到\'Rhino_backup\'集合',

        ('*', 'Auto hide \'Rhino_backup\' coll before render.'): 
        '渲染前自动隐藏\'Rhino_backup\'集合',

        ('Operator', 'Import4Rhino(coll)'): 'Rhino导入(集合)',
        ('Operator', 'Import4Rhino(empt)'): 'Rhino导入(空物体)',

        ('Operator', 'Import obj from Rhino by collection!'): 'Rhino导入(图层转集合)',
        ('Operator', 'Import obj from Rhino by emptys!'): 'Rhino导入(图层转空物体父级)',

        ('*', 'Show panel before import(Turn on again in preferences)'): '导入前显示该面板(插件首选项里可再次打开)',
        ('*', 'Show panel before export(Turn on again in preferences)'): '导出前显示该面板(插件首选项里可再次打开)',
        ('*', 'Show options plane before import'): '每次导入前显示导入选项面板',
        ('*', 'Show options plane before export'): '每次导出前显示导出选项面板',

        ('Operator', 'Copy Rhino Export Macro Command'): '复制Rhino里导出的巨集命令',
        ('Operator', 'Copy Rhino Import Macro Command'): '复制Rhino里导入的巨集命令',
        ('*', 'Paste the command directly into Rhino after copied'): '复制后直接去Rhino里去粘贴命令吧',
        ('Operator', 'Open assets explorer'): '打开Assets文件夹',

        ('*', 'The name length exceeds the maximum length allowed by blender, you can shorten the Rhino filename or layer name! (%s)'):
         '名称长度超过Blender允许的最大长度，请缩短Rhino文件名或图层名！让这个长度不超过64字符(中文算3个字符) (%s)',
       },    
}

classList = [
    RHINO_OT_add_object_coll,
    RHINO_OT_add_object_empt,
    OBJECT_OT_add_objectexport,

    RHINO_OT_CopyExportMacro,
    RHINO_OT_CopyImportMacro,
    RHINO_OT_OpenAssetsExplorer,

    SNA_AddonPreferences_9F6AA,
]

def register():
    import bpy.utils.previews
    global _icons
    _icons = bpy.utils.previews.new()

    for c in classList:
        bpy.utils.register_class(c)

    if not 'SmallTile.png' in _icons: _icons.load('SmallTile.png', os.path.join(os.path.dirname(__file__), 'icons', 'SmallTile.png'), "IMAGE")
    if not 'MediumTile.png' in _icons: _icons.load('MediumTile.png', os.path.join(os.path.dirname(__file__), 'icons', 'MediumTile.png'), "IMAGE")   

    if not 'blenderartists.png' in _icons: _icons.load('blenderartists.png', os.path.join(os.path.dirname(__file__), 'icons', 'blenderartists.png'), "IMAGE")
    if not 'icons8-github-100.png' in _icons: _icons.load('icons8-github-100.png', os.path.join(os.path.dirname(__file__), 'icons', 'icons8-github-100.png'), "IMAGE")
    if not 'bilibili.png' in _icons: _icons.load('bilibili.png', os.path.join(os.path.dirname(__file__), 'icons', 'bilibili.png'), "IMAGE")
    if not 'youtube.png' in _icons: _icons.load('youtube.png', os.path.join(os.path.dirname(__file__), 'icons', 'youtube.png'), "IMAGE")
    bpy.types.VIEW3D_MT_add.append(sna_add_to_view3d_mt_add_7D1A0)

    bpy.app.translations.register(__name__, langs)
    bpy.app.handlers.render_pre.append(disable_collection_for_render)

def unregister():
    for c in classList:
        bpy.utils.unregister_class(c)

    global _icons
    bpy.utils.previews.remove(_icons)

    bpy.types.VIEW3D_MT_add.remove(sna_add_to_view3d_mt_add_7D1A0)

    bpy.app.translations.unregister(__name__)
    bpy.app.handlers.render_pre.remove(disable_collection_for_render)

if __name__ == "__main__":
    register()
