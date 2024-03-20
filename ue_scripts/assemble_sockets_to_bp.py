import unreal

@unreal.uclass()
class GetEditorUtility(unreal.GlobalEditorUtilityBase):
    pass

@unreal.uclass()
class ScriptObject(unreal.ToolMenuEntryScript):
    
    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext) -> None:
        unreal.log_warning("Not yet implemented!!!")
        # mesh: unreal.StaticMesh = context.find_by_class(unreal.StaticMesh)
        # unreal.log(unreal.ContentBrowserAssetContextMenuContext().selected_assets)
        
        editorUtility = GetEditorUtility()
        unreal.log(editorUtility.get_selected_assets())
        self.create_bp()
        

    def create_bp(self):
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("Actor", unreal.Actor)
        
        bp_actor = asset_tools.create_asset_with_dialog("BP_", "./", None, factory)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_actor)
        
        
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