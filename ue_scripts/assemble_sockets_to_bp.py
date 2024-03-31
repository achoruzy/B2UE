# Copyright (C) 2024 Arkadiusz Choruży
# github.com/achoruzy

import unreal
from pathlib import Path
from time import sleep

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
        
        SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        root_handle = SDS.k2_gather_subobject_data_for_blueprint(actor)[0]
        subobject_handle, fail_reason = SDS.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle = root_handle,
                new_class = unreal.StaticMeshComponent,
                blueprint_context = actor
                )
            )
        print(fail_reason)
        
        SDS.rename_subobject(subobject_handle, base_mesh.get_name())
        
        SDBPFL = unreal.SubobjectDataBlueprintFunctionLibrary
        subobject: unreal.StaticMeshComponent = SDBPFL.get_object(SDBPFL.get_data(subobject_handle)) # this is the component finally
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
                if mesh_to_assemble:
                    submesh_handle, mesh_fail_reason = SDS.add_new_subobject(
                        unreal.AddNewSubobjectParams(
                            parent_handle = subobject_handle,
                            new_class = unreal.StaticMeshComponent,
                            blueprint_context = actor
                            )
                        )
                    
                    # unreal.BlueprintEditorLibrary.refresh_open_editors_for_blueprint(actor)
                    
                    SDS.rename_subobject(submesh_handle, mesh_to_assemble.get_name())
                    submesh: unreal.StaticMeshComponent = SDBPFL.get_object(SDBPFL.get_data(submesh_handle))
                    submesh.set_static_mesh(mesh_to_assemble)
                                       
                    unreal.BlueprintEditorLibrary.compile_blueprint(actor)
                    # SDS.attach_subobject(
                    #     owner_handle=subobject_handle,
                    #     child_to_add_handle=submesh_handle
                    # )
                    
                    help = submesh.k2_attach_to(
                        parent=unreal.SceneComponent.cast(subobject),
                        socket_name=socket.socket_name,
                        attach_type=unreal.AttachLocation.SNAP_TO_TARGET,
                        weld_simulated_bodies=False
                    )
                    # CHECK
                    print('>>> Is socket exist> >>>', unreal.SceneComponent.cast(subobject).does_socket_exist(socket.socket_name), help)
                    
                    # submesh.attach_to_component( # seems to work but submesh has no given socket to use and is not properly located
                    #     parent=subobject, #unreal.SceneComponent.cast(subobject),
                    #     socket_name=socket.socket_name,
                    #     location_rule=unreal.AttachmentRule.SNAP_TO_TARGET,
                    #     rotation_rule=unreal.AttachmentRule.SNAP_TO_TARGET,
                    #     scale_rule=unreal.AttachmentRule.SNAP_TO_TARGET
                    # )
                    
                    print('>>> attached socket name >>>', submesh.get_attach_socket_name())
                    
                    # submesh.set_relative_transform(
                    #     new_transform=unreal.Transform(),
                    #     sweep=False,
                    #     teleport=False
                    #     )
                    
                    
                
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