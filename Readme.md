# <font color="darkorange">B</font>2<font color="cyan">UE</font>

## Toolset for Blender and Unreal Engine import/export operations

### Contains:

#### <font color="darkorange">Blender</font> scripts:

<font color="darkorange">**B2UE.py**</font> - generates properly models for export to UE with proper localization, rotation and sockets to use in UE.

Models needs to be parented and have applied rotation and scale. Base model need to be X-forward and applied transform. Models that need specific pivot location or specific directions has to have properly located origin.

To export from Blender select all the objects in EXPORT_OBJECTS collection (both models and empties) and nothing else. Exported FBX file on import to UE will automatically generate sockets having names consistent with parts to set into sockets.


#### <font color="cyan">Unreal</font> scripts:

<font color="cyan">**assemble_sockets_to_bp.py**</font> - Unreal Engine script that automates creating assembly blueprint of multi part models with use of given sockets.

The scripts searches for parts only in the same directory where the base part is. The base part should be named with suffix `_base` and names of sockets and subparts should be corelated (best to use B2UE.py script for Blender).

NOTE: Unfortunatelly, UE doesn't allow assigning parent sockets in components from python script!

To make it work execute the script in UE editor first, then `Create assembly blueprint` is given under StaticMesh asset context menu (RMB on asset in Context Browser). If conditions are fullfilled, there will be created a new BP in this directory.


---

Copyright (C) 2024 Arkadiusz Choruży
