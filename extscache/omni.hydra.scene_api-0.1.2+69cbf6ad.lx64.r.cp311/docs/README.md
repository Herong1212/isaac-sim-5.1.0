
## A background scene delegate and python api

This extension provides a scene delegate that can load in the background,
and also python api for adding and removing those scene delegates.

Usage is like

> from omni.hydra.scene_api import add_background_loading_hydra_scene_delegate, remove_hydra_scene_delegate
   
> add_background_loading_hydra_scene_delegate('myuniquename', '/path/to/file.usd')
    ... Do stuff
> remove_hydra_scene_delegate('myuniquename')

Note that name needs to follow usd identifier rules, like a prim name.

