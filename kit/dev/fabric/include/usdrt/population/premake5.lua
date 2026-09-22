project "usdrt.population.interface"
    location (workspaceDir.."/%{prj.name}")
    kind "StaticLib"
    use_usdrt_settings()
    targetdir(targetPluginsDir.."/usdrt")
    use_gsl()
    use_carb()
    
    -- Begin OpenUSD
    add_usd()
    -- End OpenUSD

    dependson { "omni.core.interfaces" }
    omnibind {
        {
            file = "IUtils.h",
            api  = "IUtils.gen.h",
            py   = repo_build.root.."/../runtime/source/bindings/python/usdrt/population/PyIUtils.gen.h"
        },
    }
