project "usdrt.hierarchy.interface"
    location (workspaceDir.."/%{prj.name}")
    kind "StaticLib"
    use_usdrt_settings()
    targetdir(targetPluginsDir.."/usdrt")
    use_carb()
    use_gsl()
    dependson { "omni.core.interfaces" }
    omnibind {
        { file="IFabricHierarchy.h", api="IFabricHierarchy.gen.h", py=repo_build.root.."/../runtime/source/bindings/python/usdrt/hierarchy/PyIFabricHierarchy.gen.h" },
    }
