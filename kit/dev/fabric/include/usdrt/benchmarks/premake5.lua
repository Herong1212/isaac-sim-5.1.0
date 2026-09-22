project "usdrt.benchmarks.interface"
    location (workspaceDir.."/%{prj.name}")
    kind "StaticLib"
    targetdir(targetPluginsDir.."/usdrt")
    use_usdrt_settings()
    use_carb()
    use_gsl()
    dependson { "omni.core.interfaces" }
    omnibind {
        { file="IBenchmarks.h", api="IBenchmarks.gen.h", py=repo_build.root.."/../runtime/source/bindings/python/usdrt/benchmarks/PyIBenchmarks.gen.h" },
    }
