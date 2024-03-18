import unreal

@unreal.uclass()
class ScriptObject(unreal.ToolMenuEntryScript):
    
    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext) -> None:
        unreal.log_warning("Not yet implemented!")

    def create_bp():
        ...
        
    def find_model_parts():
        ...
        
    def assemble_model():
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