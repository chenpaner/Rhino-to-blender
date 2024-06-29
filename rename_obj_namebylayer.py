# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs

filename = rs.DocumentName()

if not filename:   
    filename = "NoSaveRhino"

if filename.endswith(".3dm"):
    filename = filename[:-4]

def clean_layer_name(name):
    return name.replace("/", "-").replace(":", ";").replace("*", "-").replace(".", "_")

def LayerNameToObject():
    layers = rs.LayerNames()
    if layers:
        for layer in layers: 
            layername=rs.LayerName(layer, fullpath=False)
            cleaned_layer_name = clean_layer_name(layername)
            if cleaned_layer_name != layername:
                rs.RenameLayer(layername, cleaned_layer_name)
    objects = rs.AllObjects()
    if objects:
        for obj in objects:
            obj_name = rs.ObjectName(obj)
            if obj_name:
                parts = obj_name.split("*")
                if len(parts) > 1:
                    cleaned_obj_name = parts[0] + "*" + clean_layer_name(parts[1])
                    if cleaned_obj_name != obj_name:
                        rs.ObjectName(obj, cleaned_obj_name)
    layers = rs.LayerNames()
    for layer in layers:
        objs = rs.ObjectsByLayer(layer)
        nmax_index = 0
        objs.reverse()
        for obj in objs:
            current_name = rs.ObjectName(obj)
            if current_name:
                if current_name.startswith("{}/{}*".format(filename, layer)):
                    index_str = current_name.split("*")[-1]                
                    try:
                        index = int(index_str)
                        if index > nmax_index:
                            nmax_index = index                        
                    except ValueError:
                        pass              
        index = nmax_index + 1     
        objs.reverse()
        for obj in objs:            
            index_str = "{:03d}".format(index)
            check_name = "{}/{}*".format(filename, layer)                  
            current_name = rs.ObjectName(obj) 
            if not current_name or not current_name.startswith(check_name) :                
                new_name = "{}/{}*{}".format(filename, layer, index_str)              
                rs.ObjectName(obj, new_name)
                index += 1 
            else:
                if sum(1 for o in objs if rs.ObjectName(o) == current_name) > 1:                  
                    index_new = 1
                    while True:
                        indexn = "{:03d}".format(index_new)
                        new_name = "{}_{}".format(current_name, indexn)
                        if not rs.ObjectsByName(new_name):
                            break
                        indexn += 1
                    rs.ObjectName(obj, new_name)
    print("All objects renamed!")
    selected_objects = rs.SelectedObjects()
    if selected_objects:
        print("Selected {} objs,and be exported!".format(len(selected_objects)))
    else:
        print("!!!!!No objects selected, no objects will be exported!!!!!")

LayerNameToObject()