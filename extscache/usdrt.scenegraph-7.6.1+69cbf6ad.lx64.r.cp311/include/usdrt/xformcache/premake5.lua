project "usdrt.xformcache.interface"
    location (workspaceDir.."/%{prj.name}")
    kind "StaticLib"
    use_usdrt_settings()
    targetdir(targetPluginsDir.."/scenegraph")
    use_carb()
    use_gsl()
    dependson { "omni.core.interfaces" }
    omnibind {
        { file="IXformCache.h", api="IXformCache.gen.h", py=repo_build.root.."/../runtime/source/bindings/python/usdrt/xformcache/IXformCache.gen.h" },
        { file="ISharedXformCache.h", api="ISharedXformCache.gen.h", py=repo_build.root.."/../runtime/source/bindings/python/usdrt/xformcache/ISharedXformCache.gen.h" },
    }
