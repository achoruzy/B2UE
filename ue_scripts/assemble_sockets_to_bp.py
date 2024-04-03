# Copyright (C) 2024 Arkadiusz Choruży
# github.com/achoruzy

import unreal
from pathlib import Path

class ScriptUtils():
    @staticmethod
    def get_base_mesh_from_selected() -> unreal.StaticMesh:
        editorUtility = GetEditorUtility()
        selection = editorUtility.get_selected_assets()
        for asset in selection:
            asset: unreal.StaticMesh
            if asset.get_full_name().endswith('_base'):
                return asset
        return None
    
    @staticmethod
    def create_BP_Actor(name: str, path: str) -> unreal.Actor:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        factory = unreal.BlueprintFactory()
        factory.set_editor_property('ParentClass', unreal.Actor)
        
        bp_actor = asset_tools.create_asset(name, path, None, factory)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_actor)
        return bp_actor
    
    @staticmethod
    def add_BP_component(bp: unreal.Blueprint, comp_name: str, comp_type: unreal.SceneComponent, 
                         parent_to: unreal.SubobjectDataHandle = None) -> tuple[unreal.SubobjectDataHandle, unreal.SceneComponent]:
        # handlers
        SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        SDBPFL = unreal.SubobjectDataBlueprintFunctionLibrary
        
        if not parent_to:
            parent_to = SDS.k2_gather_subobject_data_for_blueprint(bp)[0]
            
        subobject_handle, _fail_reason = SDS.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle = parent_to,
                new_class = comp_type,
                blueprint_context = bp
            )
        )        
        subobject = SDBPFL.get_object(SDBPFL.get_data(subobject_handle))
        SDS.rename_subobject(subobject_handle, comp_name)
        
        return subobject_handle, subobject
    
    @staticmethod
    def get_static_mesh_sockets(static_mesh: unreal.StaticMeshComponent) -> list[unreal.StaticMeshSocket]:
        sockets = static_mesh.get_sockets_by_tag('')
        return sockets

@unreal.uclass()
class GetEditorUtility(unreal.GlobalEditorUtilityBase):
    pass

@unreal.uclass()
class SocketAssemblerScript(unreal.ToolMenuEntryScript):
    
    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext) -> None:
        base_mesh = ScriptUtils.get_base_mesh_from_selected()
        if not base_mesh: return
        
        bp_name = f"BP_{base_mesh.get_name().removeprefix('SM_').removesuffix('_base')}"
        bp_path = Path(base_mesh.get_path_name()).parent.as_posix()

        actor = ScriptUtils.create_BP_Actor(bp_name, bp_path)
                    
        basepart_handle, basepart = ScriptUtils.add_BP_component(
            bp=actor,
            comp_name=base_mesh.get_name(),
            comp_type=unreal.StaticMeshComponent,
        )
        basepart.set_static_mesh(base_mesh)        
        basepart_sockets = ScriptUtils.get_static_mesh_sockets(base_mesh)
        
        #### Refactored till here
        
        SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        SDBPFL = unreal.SubobjectDataBlueprintFunctionLibrary
        EAL = unreal.EditorAssetLibrary
        PT = unreal.PackageTools
        
        assets_in_dir = EAL.list_assets(directory_path=bp_path, recursive=False)
        assets_in_dir = [PT.filename_to_package_name(a.removesuffix(a[a.rfind('.'):])) for a in assets_in_dir]
        
        if basepart_sockets:
            for socket in basepart_sockets:
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
                            parent_handle = basepart_handle,
                            new_class = unreal.StaticMeshComponent,
                            blueprint_context = actor
                            )
                        )
                    
                    
                    # unreal.BlueprintEditorLibrary.refresh_open_editors_for_blueprint(actor)
                    
                    SDS.rename_subobject(submesh_handle, mesh_to_assemble.get_name())
                    submesh: unreal.StaticMeshComponent = SDBPFL.get_object(SDBPFL.get_data(submesh_handle))
                    
                    submesh.call_method("K2_AttachToComponent", (
                        basepart, 
                        socket.socket_name, 
                        unreal.AttachmentRule.SNAP_TO_TARGET,
                        unreal.AttachmentRule.SNAP_TO_TARGET,
                        unreal.AttachmentRule.SNAP_TO_TARGET,
                        False
                        ))
                    # submesh.attach_to_component( # seems to work but submesh has no given socket to use and is not properly located
                    #     parent=subobject, #unreal.SceneComponent.cast(subobject),
                    #     socket_name=socket.socket_name,
                    #     location_rule=unreal.AttachmentRule.SNAP_TO_TARGET,
                    #     rotation_rule=unreal.AttachmentRule.SNAP_TO_TARGET,
                    #     scale_rule=unreal.AttachmentRule.SNAP_TO_TARGET
                    # )
                    
                    submesh.set_static_mesh(mesh_to_assemble)
                                       
                    # submesh.set_editor_property("AttachSocketName", socket_name)
                    # world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
                    # submesh.call_method("SetAttachSocketName", (socket.socket_name, world,))
                    
                    # unreal.BlueprintEditorLibrary.compile_blueprint(actor)
                    # SDS.attach_subobject(
                    #     owner_handle=subobject_handle,
                    #     child_to_add_handle=submesh_handle
                    # )
                    
                    # help = submesh.k2_attach_to(
                    #     parent=unreal.SceneComponent.cast(subobject),
                    #     socket_name=socket.socket_name,
                    #     attach_type=unreal.AttachLocation.SNAP_TO_TARGET,
                    #     weld_simulated_bodies=False
                    # )
                    # CHECK
                    print('>>> Is socket exist> >>>', unreal.SceneComponent.cast(basepart).does_socket_exist(socket.socket_name), help)
                    
                    print('>>> attached socket name >>>', submesh.get_attach_socket_name())
                    
                    # submesh.set_relative_transform(
                    #     new_transform=unreal.Transform(),
                    #     sweep=False,
                    #     teleport=False
                    #     )
                                    
        # 4. repeat for each subcomponent
    

def register_menu_position():
    menus = unreal.ToolMenus().get()
    mesh_context_menu = menus.find_menu("ContentBrowser.AssetContextMenu.StaticMesh")
    
    script = SocketAssemblerScript()
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