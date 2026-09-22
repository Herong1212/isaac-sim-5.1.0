```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# USDRT Project Overview

USDRT is a package delivering a set of libraries and functionality that
accelerate runtime processing and workflows on top of a USD stage, without the limitations
imposed by the USD API.

## Fabric

A library that provides fast access, modification, topology editing and change notification for
a composed USD stage, gpu-cpu interoperability, and replication support for multi-node clients.
The keystone of USDRT. Fabric is developed in Kit but a synchronized build is provided here.

## USDRT Scenegraph API

A pin-compatible API to USD that extends the API to provide new efficient methods
for run-time introspection and authoring of data with Fabric. C++ and pybind bindings
are provided. This includes a no-dependency implementation of Gf, also with pybind bindings.

## Fabric Scene Delegate

Highly optimized Hydra scene delegate to provide data to renderers with minimal copying of data
across CPU and GPU, as well as data-streaming and  just-in-time scene optimizations.

## Test render delegate and hdTest binary

A render delegate that generates USD output for testing and validation
of scene delegate implementations. The hdTest binary loads a USD stage
and outputs the results of the Hydra pipeline as USD using the test render delegate.

## USD viewer

A standalone USD viewer using imgui. Super-lightweight and great for
testing and experimentation. 
