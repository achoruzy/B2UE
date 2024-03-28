import unreal

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
        print(f'bp_name: {bp_name}')
        actor = self.create_bp(bp_name, base_mesh.get_path_name().removesuffix(bp_name)) # TODO: path to rework
        
        so_subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem) # TODO: smtg wrong here
        root_sub_object = so_subsystem.k2_gather_subobject_data_for_instance(actor)[0]
        new_sub_object: unreal.StaticMesh = so_subsystem.add_new_subobject(unreal.AddNewSubobjectParams(
            parent_handle=root_sub_object,
            new_class=unreal.StaticMesh,
            ))
        
        # 2. get sockets
        print('2. get sockets')
        sockets = new_sub_object.get_sockets_by_tag('')
        
        # 3. check for meshes to put in sockets in same localization
        editorUtility = GetEditorUtility();
        
        for socket in sockets:
            socket: unreal.StaticMeshSocket
            socket_name = socket.socket_name
            print(socket_name)
            
            # editorUtility...
            
            
        
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

    def create_bp(self, name: str, path: str) -> unreal.Actor:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        factory = unreal.BlueprintFactory()
        factory.set_editor_property('ParentClass', unreal.Actor)
        
        bp_actor = asset_tools.create_asset(name, path, None, factory)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_actor)
        return bp_actor
    
        
    def find_model_parts(self):
        ...
        
    def assemble_model(self):
        ...

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