# Copyright (C) 2024 Arkadiusz Choruży
# github.com/achoruzy

import unreal
from pathlib import Path

@unreal.uclass()
class GetEditorUtility(unreal.GlobalEditorUtilityBase):
    pass

@unreal.uclass()
class ScriptObject(unreal.ToolMenuEntryScript):
    
    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext) -> None:      
        # 1. find base mesh, create bp and set mesh as component of actor
        base_mesh = self.find_base_mesh()
        if not base_mesh: return
        
        bp_name = f"BP_{base_mesh.get_name().removeprefix('SM_').removesuffix('_base')}"
        bp_path = Path(base_mesh.get_path_name()).parent.as_posix()

        actor = self.create_actor_bp(bp_name, bp_path)
        
        subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        root_sub_object = subsystem.k2_gather_subobject_data_for_blueprint(actor)[0]
        subobject_handle, fail_reason = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle = root_sub_object,
                new_class = unreal.StaticMeshComponent,
                blueprint_context = actor
                )
            )
        print(fail_reason)
        
        subsystem.rename_subobject(subobject_handle, base_mesh.get_name())
        
        bp_func_lib = unreal.SubobjectDataBlueprintFunctionLibrary
        subobject: unreal.StaticMeshComponent = bp_func_lib.get_object(bp_func_lib.get_data(subobject_handle)) # this is the component finally
        subobject.set_static_mesh(base_mesh)
        
        # 2. get sockets
        print('2. get sockets')
        sockets = base_mesh.get_sockets_by_tag('') # OK!
        # sockets = [s.socket_name.replace('.', '_') for s in sockets] # as asset names have auto replace in names
        
        # 3. check for meshes to put in sockets in same localization
        EAL = unreal.EditorAssetLibrary
        PT = unreal.PackageTools
        
        # LogPackageName: Warning: TryConvertFilenameToLongPackageName 
        # was passed an ObjectPath (/Game/GAME/Props/Guns/AK47/Meshes/SM_AK_SM_AK_base.SM_AK_SM_AK_base) 
        # rather than a PackageName or FilePath; it will be converted to the PackageName. 
        # Accepting ObjectPaths is deprecated behavior and will be removed in a future release; 
        # TryConvertFilenameToLongPackageName will fail on ObjectPaths.

        assets_in_dir = EAL.list_assets(directory_path=bp_path, recursive=False)
        assets_in_dir = [PT.filename_to_package_name(a.removesuffix(a[a.rfind('.'):])) for a in assets_in_dir] # to fix the warning given above
        for i in assets_in_dir:
            print("===========>>>>>>>>>", i)
        
        if sockets:
            for socket in sockets:
                socket: unreal.StaticMeshSocket
                socket_name = str(socket.socket_name).replace('.', '_')
                print('>>>>>> socket name', socket_name)
                
                mesh_to_assemble_path = [a for a in assets_in_dir if socket_name in a][0]
                mesh_to_assemble = EAL.load_asset(mesh_to_assemble_path)
                print("xxxxxxxxxxx>>>>", mesh_to_assemble.get_name())
                
                # attach new component here
                
        # 4. repeat for each subcomponent
        
    def find_base_mesh(self) -> unreal.StaticMesh:
        editorUtility = GetEditorUtility()
        selection = editorUtility.get_selected_assets()
        unreal.log(selection)
        for asset in selection:
            asset: unreal.StaticMesh
            if asset.get_full_name().endswith('_base'):
                return asset
        return None

    def create_actor_bp(self, name: str, path: str) -> unreal.Actor:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        factory = unreal.BlueprintFactory()
        factory.set_editor_property('ParentClass', unreal.Actor)
        
        bp_actor = asset_tools.create_asset(name, path, None, factory)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_actor)
        return bp_actor
    

def register_menu_position():
    menus = unreal.ToolMenus().get()
    mesh_context_menu = menus.find_menu("ContentBrowser.AssetContextMenu.StaticMesh")
    
    script = ScriptObject()
    script.init_entry(
        owner_name = mesh_context_menu.menu_name,
        menu = mesh_context_menu.menu_name,
        section = "GetAssetActions",
        name = "AC_CreateAssemblyBP",
        label = "Create assembly blueprint",
        tool_tip = "Creates new blueprint with this mesh and all found socket parts recursively."
    )
    script.register_menu_entry()

def run_script():
    register_menu_position()

if __name__ == "__main__":
    run_script()