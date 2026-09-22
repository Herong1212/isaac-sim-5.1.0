# Replicator YAML


## Getting started

Build replicator using the instructions in the Readme of the main repo.


## Create YAML file

Following the [Replicator Parameter List](https://docs.omniverse.nvidia.com/app_isaacsim/app_isaacsim/manual_replicator_composer_parameter_list.html#isaac-sim-app-manual-replicator-replicator_yaml-parameter-list) to create the YAML file.

## Generate the scene

```python
    from omni.replicator.replicator_yaml import parse
    import omni.replicator.core as rep

    parse(
        yaml_path="data/parameters/profiles/flying_things_3d.yaml",
        root_dir="/home/jf/Projects/omni.replicator/source/extensions/omni.replicator.replicator_yaml/python/scripts"
    )

    # Run the replicator
    rep.orchestrator.run()
```