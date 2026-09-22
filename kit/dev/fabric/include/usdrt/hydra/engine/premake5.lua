project "usdrt.hydra.engine.interface"
    location (workspaceDir.."/%{prj.name}")
    kind "StaticLib"
    use_usdrt_settings()
    targetdir(targetPluginsDir.."/usdrt")
    use_carb()
    
    -- Begin OpenUSD
    add_usd()
    enable_usd_pch()
    -- End OpenUSD

    use_gsl()
    omnibind {
        { file="ISimpleEngine.h", api="ISimpleEngine.gen.h", py=repo_build.root.."/../runtime/source/bindings/python/usdrt/engine/PyISimpleEngine.gen.h" },
    }
    dependson { "omni.core.interfaces" }
