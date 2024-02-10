# Rhino-to-blender

Quickly export Rhino models to Blender and retain the layer structure in Rhino. The layers in Rhino will automatically be converted into collections or parent empty objects in Blender!

![Snipaste_2023-10-27_01-59-00](https://github.com/chenpaner/Rhino-to-blender/assets/107256886/ff41772d-5633-4963-aa2d-79d18d7a957f)

# Installation

## 中文：[Video](https://www.bilibili.com/video/BV15G411C745/?vd_source=aabd4ea827264740eabbeec9857d3286)
1,先安装Blender端的插件，安装后复制插件里的assets文件夹路径！

2，安装rhino里的插件
      拖动rename_obj_bylayer.rhp到rhino里就行了

3，添加rhino里的按钮，修改巨集指令
    RHINO 里新建一个按钮，然后shift右键按钮打开编辑！
    
左键导出模型到Blender在左键里复制下面内容：（记得把文件路径改为第一步复制的路径，记得在路径最后以\Rhino to Blender-mesh.obj结尾）
```
!NoEcho
 -_rename_objrhino
 -_Export _GeometryOnly=_Yes _SaveTextures=_No _SaveNotes=_No _SaveSmall=_Yes
"C:\Users\CP\AppData\Roaming\Blender Foundation\Blender\Big addons\addons\Rhino to blender\assets\Rhino to Blender-mesh.obj"
Geometry=Mesh  EndOfLine=CRLF  ExportRhinoObjectNames=ExportObjectsAsOBJObjects  ExportRhinoGroupOrLayerNames=ExportLayersAsOBJGroups  MergeNestedLayerGroupNames=No  SortByOBJGroups=Yes  ExportMaterialDefinitions=Yes  ChangeWhitespaceToUnderscores=No  UseDisplayColorForMaterial=Yes  YUp=Yes  WrapLongLines=No  WritePrecision=17  ExportMeshTextureCoordinates=Yes  ExportMeshVertexNormals=Yes  ExportMeshVertexColors=No  ExportOpenMeshes=Yes  ExportMeshAsTriangles=No  UseRenderMeshes=Yes  VertexWelding=Welded  SubDMeshing=FromSurface  SubDLevel=1  NgonMode=None
enter
```

右键把模型从Blender里导入到Rhino
右边复制下面内容：（记得把文件路径改为第一步复制的路径，记得在路径最后以\Blender to Rhino-mesh.obj结尾）
2024.02.10 添加了熔并重复顶点的操作，导入完成后要手动框选导入的网格，或者运行选择最后生成的obj（'_SelLast）.
```
!NoEcho -_Import
"C:\Users\CP\AppData\Roaming\Blender Foundation\Blender\4.0\scripts\addons\Rhino to blender\assets\Blender to Rhino-mesh.obj"
MapYtoZ=Yes
enter
_WeldVertices
```

## English：[YouToBe](https://youtu.be/peUmoLbUnKY)
I made an English subtitle with Google Translate, remember to turn it on!

1/First, install the plugin in Blender, and after installation, copy the path of the "assets" folder from the plugin!

2/Install the plugin in Rhino
 Just drag and drop "rename_obj_bylayer.rhp" into Rhino.

3/Add a button in Rhino and modify the macro command
 Create a new button in Rhino, then right-click the button and select "Edit"!
 
Left-click to export the model to Blender
Copy the following content in the left-click action (make sure to change the file path to the one copied in the first step, and make sure it ends with "\Rhino to Blender-mesh.obj"):

```
!NoEcho
-_rename_objrhino
-_Export _GeometryOnly=_Yes _SaveTextures=_No _SaveNotes=_No _SaveSmall=_Yes
"C:\Users\CP\AppData\Roaming\Blender Foundation\Blender\Big addons\addons\Rhino to blender\assets\Rhino to Blender-mesh.obj"
Geometry=Mesh  EndOfLine=CRLF  ExportRhinoObjectNames=ExportObjectsAsOBJObjects  ExportRhinoGroupOrLayerNames=ExportLayersAsOBJGroups  MergeNestedLayerGroupNames=No  SortByOBJGroups=Yes  ExportMaterialDefinitions=Yes  ChangeWhitespaceToUnderscores=No  UseDisplayColorForMaterial=Yes  YUp=Yes  WrapLongLines=No  WritePrecision=17  ExportMeshTextureCoordinates=Yes  ExportMeshVertexNormals=Yes  ExportMeshVertexColors=No  ExportOpenMeshes=Yes  ExportMeshAsTriangles=No  UseRenderMeshes=Yes  VertexWelding=Welded  SubDMeshing=FromSurface  SubDLevel=1  NgonMode=None
enter
```

Right-click to import the model into Rhino，Copy the following content in the right-click action (make sure to change the file path to the one copied in the first step, and make sure it ends with "\Blender to Rhino-mesh.obj"):
```
!NoEcho -_Import
"C:\Users\CP\AppData\Roaming\Blender Foundation\Blender\Big addons\addons\Rhino to blender\assets\Blender to Rhino-mesh.obj"
MapYtoZ=Yes
enter
```
