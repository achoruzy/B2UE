# <font color="darkorange">B</font>2<font color="cyan">UE</font>

### Toolset for Blender and Unreal Engine import/export operations

#### Contains:

##### Blender scripts:

<font color="darkorange">**B2UE.py**</font> - generates properly models for export to UE with proper localization, rotation and sockets to use in UE.

Models needs to be parented and have applied rotation and scale. Base model need to be X-forwart and applied transform. Models that need specific pivot location or specific directions has to have properly located origin.

To export from Blender select all the objects in EXPORT_OBJECTS collection (both models and empties) and nothing else. Exported FBX file on import to UE will automatically generate sockets having names consistent with models to socket into.

---

Copyright (C) 2024 Arkadiusz Choruży
