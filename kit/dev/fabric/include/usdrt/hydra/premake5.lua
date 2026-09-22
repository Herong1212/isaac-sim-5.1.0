project "usdrt.scenedelegate.interface"
    location (workspaceDir.."/%{prj.name}")
    kind "StaticLib"
    use_usdrt_settings()
    targetdir(targetPluginsDir.."/usdrt")
    use_carb()
    use_gsl()
    dependson { "omni.core.interfaces" }
    omnibind {
        { file="ISceneDelegate.h",
          api="ISceneDelegate.gen.h",
          -- py=repo_build.root.."/source/bindings/python/usdrt/scenedelegate/PyISceneDelegate.gen.h"
        }
    }
