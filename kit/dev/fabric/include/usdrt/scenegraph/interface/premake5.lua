project "usdrt.scenegraph.interface"
    location (repo_build.workspace_dir().."/%{prj.name}")
    kind "StaticLib"
    use_usdrt_settings()
    targetdir(targetPluginsDir.."/scenegraph")
    use_carb()
    use_gsl()
    dependson { "omni.core.interfaces" }
    omnibind {
        { file="IRtStage.h", api="IRtStage.gen.h"},
        { file="IRtStage104QuerySupport.h", api="IRtStage104QuerySupport.gen.h"},
        { file="IRtStage105.h", api="IRtStage105.gen.h"},
        { file="IRtStage106.h", api="IRtStage106.gen.h"},
        { file="IRtStage106_4.h", api="IRtStage106_4.gen.h"},
        { file="IRtStage107.h", api="IRtStage107.gen.h"},
        { file="IRtPrim.h", api="IRtPrim.gen.h"},
        { file="IRtPrim105.h", api="IRtPrim105.gen.h"},
        { file="IRtPrim107.h", api="IRtPrim107.gen.h"},
        { file="IRtAttribute.h", api="IRtAttribute.gen.h"},
        { file="IRtAttribute105.h", api="IRtAttribute105.gen.h"},
        { file="IRtObject.h", api="IRtObject.gen.h"},
        { file="IRtProperty.h", api="IRtProperty.gen.h"},
        { file="IRtPrimRange.h", api="IRtPrimRange.gen.h"},
        { file="IRtRelationship.h", api="IRtRelationship.gen.h"},
        { file="IRtXformable.h", api="IRtXformable.gen.h"},
        { file="IRtCollection.h", api="IRtCollection.gen.h"},
        { file="IRtBoundable.h", api="IRtBoundable.gen.h"},
        { file="IRtAssetPath.h", api="IRtAssetPath.gen.h"},
        { file="IRtSchemaRegistry.h", api="IRtSchemaRegistry.gen.h"},
        { file="IRtPrimSelection.h", api="IRtPrimSelection.gen.h"},
        { file="IRtPrimSelection106_4.h", api="IRtPrimSelection106_4.gen.h"},
        { file="IRtPath.h", api="IRtPath.gen.h"},
        { file="IRtPath107.h", api="IRtPath107.gen.h"},
        -- add one more line for each other interface header in the project.
    }
