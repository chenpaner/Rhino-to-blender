## Please go to the blender plug-in website to download the new version.[链接](https://extensions.blender.org/approval-queue/rhino-to-blender/)

## And download rename_obj_bylayer.rhp in there！


# Link To Rhino（~~Rhino-to-blender~~)

Quickly export Rhino models to Blender and retain the layer structure in Rhino. The layers in Rhino will automatically be converted into collections or parent empty objects in Blender!

Change the plugin name to Link To Rhino ,for comply with blender's Terms of Service.

![Snipaste_2023-10-27_01-59-00](https://github.com/chenpaner/Rhino-to-blender/assets/107256886/ff41772d-5633-4963-aa2d-79d18d7a957f)

![1980](https://github.com/chenpaner/Rhino-to-blender/assets/107256886/aa539b8c-1acc-42a1-be21-fa241a8c642f)


# Installation

- **中文：[Video](https://www.bilibili.com/video/BV1cH4y1A7Fc/?vd_source=aabd4ea827264740eabbeec9857d3286)
- **En：[Video](https://blenderartists.org/t/free-addon-rhino-to-blender-quickly-export-rhino-models-to-blender/1489621/3?u=chen-pan)

# Change Log

## *15/8/2024*

### ADDED
- Added a new command: rename_objrhino_by_id,If you are an architect with more than 10,000 objects in the scene, it will be faster than rename_objrhino. Be careful not to nest too many layers to avoid objects exceeding the blender's object name length limit.

### FIXED
- Fixed rename_objrhino command renaming object serial number bug, it will be faster!
- rename_objrhino command will now only rename objects in the displayed layer, hidden layers will be automatically ignored
