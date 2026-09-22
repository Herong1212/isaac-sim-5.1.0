```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```
# Camera Manipulator

Mouse interaction with the Viewport is handled with classes from `omni.kit.manipulator.camera`, which is built on top of the `omni.ui.scene` framework.
We've created an `omni.ui.scene.SceneView` to host the manipulator, and by simply assigning the camera manipulators model
into the SceneView's model, all of the edits to the Camera's transform will be pushed through to the `SceneView`.


```
# And finally add the camera-manipulator into that view
with self.__scene_view.scene:
    self.__camera_manip = ViewportCameraManipulator(self.viewport_api)

    # Push the camera manipulator's model into the SceneView so it'lll auto-update
    self.__scene_view.model = self.__camera_manip.model
```

The `omni.ui.scene.SceneView` only understands two values: 'view' and 'projection'.  Our CameraManipulator's model will push
out those values as edits are made; however, it supports a larger set of values to control the manipulator itself.

## Operations and Values

The CameraManipulator model store's the amount of movement according to three modes, applied in this order:
1. Tumble
2. Look
3. Move (Pan)
4. Fly (FlightMode / WASD navigation)

### tumble
Tumble values are specified in degrees as the amount to rotate around the current up-axis.
These values should be pre-scaled with any speed before setting into the model.
This allows for different manipulators/gestures to interpret speed differently, rather than lock to a constant speed.
```python
# Tumble by 180 degrees around Y (as a movement across ui X would cause)
model.set_floats('tumble', [0, 180, 0])
```

### look
Look values are specified in degrees as the amount to rotate around the current up-axis.
These values should be pre-scaled with any speed before setting into the model.
This allows for different manipulators/gestures to interpret speed differently, rather than lock to a constant speed.
```python
# Look by 90 degrees around X (as a movement across ui Y would cause)
# i.e Look straight up
model.set_floats('look', [90, 0, 0])
```

### move
Move values are specified in world units and the amount to move the camera by.
Move is applied after rotation, so the X, Y, Z are essentially left, right, back.
These values should be pre-scaled with any speed before setting into the model.
This allows for different manipulators/gestures to interpret speed differently, rather than lock to a constant speed.
```python
# Move left by 30 units, up by 60 and back by 90
model.set_floats('move', [30, 60, 90])
```

### fly
Fly values are the direction of flight in X, Y, Z.
Fly is applied after rotation, so the X, Y, Z are essentially left, right, back.
These values will be scaled with `fly_speed` before aplication.
Because fly is a direction with `fly_speed` automatically applied, if a gesture/manipulator wants to fly slower
without changing `fly_speed` globally, it must apply whatever factor is required before setting.
```python
# Move left
model.set_floats('fly', [1, 0, 0])
# Move up
model.set_floats('fly', [0, 1, 0])
```


## Speed


By default the Camera manipulator will map a full mouse move across the viewport as follows:
- Pan: A full translation of the center-of-interest across the Viewport.
- Tumble: A 180 degree rotation across X or Y.
- Look: A 180 degree rotation across X and a 90 degree rotation across Y.

These speed can be adjusted by setting float values into the model.

### world_speed
The Pan and Zoom speed can be adjusted with three floats set into the model as 'world_speed'.
```python
# Half the movement speed for both Pan and Zoom
pan_speed_x = 0.5, pan_speed_y = 0.5, zoom_speed_z = 0.5
model.set_floats('world_speed', [pan_speed_x, pan_speed_y, zoom_speed_z])
```


### rotation_speed
The Tumble and Look speed can be adjusted with either a scalar value for all rotation axes or per component.
```python
# Half the rotation speed for both Tumble and Look
rot_speed_both = 0.5
model.set_floats('rotation_speed', [rot_speed_both])
# Half the rotation speed for both Tumble and Look in X and quarter if for Y
rot_speed_x = 0.5, rot_speed_y = 0.25
model.set_floats('rotation_speed', [rot_speed_x, rot_speed_y])
```

### tumble_speed
Tumble can be adjusted separately with either a scalar value for all rotation axes or per component.
The final speed of Tumble operation is `rotation_speed * tumble_speed`
```python
# Half the rotation speed for Tumble
rot_speed_both = 0.5
model.set_floats('tumble_speed', [rot_speed_both])
# Half the rotation speed for Tumble in X and quarter if for Y
rot_speed_x = 0.5, rot_speed_y = 0.25
model.set_floats('tumble_speed', [rot_speed_x, rot_speed_y])
```

### look_speed
Look can be adjusted separately with either a scalar value for all rotation axes or per component.
The final speed of a Look operation is `rotation_speed * tumble_speed`
```python
# Half the rotation speed for Look
rot_speed_both = 0.5
model.set_floats('look_speed', [rot_speed_both])
# Half the rotation speed for Tumble in X and quarter if for Y
rot_speed_x = 0.5, rot_speed_y = 0.25
model.set_floats('look_speed', [rot_speed_x, rot_speed_y])
```

### fly_speed
The speed at which FlightMode (WASD navigation) will fly through the scene.
FlightMode speed can be adjusted separately with either a scalar value for all axes or per component.
```python
# Half the speed in all directions
fly_speed = 0.5
model.set_floats('fly_speed', [fly_speed])
# Half the speed when moving in X or Y, but double it moving in Z
fly_speed_x_y = 0.5, fly_speed_z = 2
model.set_floats('fly_speed', [fly_speed_x_y, fly_speed_x_y, fly_speed_z])
```


## Undo


Because we're operating on a unique `omni.usd.UsdContext` we don't want movement in the preview-window to affect the undo-stack.
To accomplish that, we'll set the 'disable_undo' value to an array of 1 int; essentially saying `disable_undo=True`.
```python
# Let's disable any undo for these movements as we're a preview-window
model.set_ints('disable_undo', [1])
```


## Disabling operations


By default the manipulator will allow Pan, Zoom, Tumble, and Look operations on a perspective camera, but only allow
Pan and Zoom on an orthographic one.  If we want to explicitly disable any operations again we set int values as booleans
into the model.

### disable_tumble
```python
# Disable the Tumble manipulation
model.set_ints('disable_tumble', [1])
```

### disable_look
```python
# Disable the Look manipulation
model.set_ints('disable_look', [1])
```

### disable_pan
```python
# Disable the Pan manipulation.
model.set_ints('disable_pan', [1])
```

### disable_zoom
```python
# Disable the Zoom manipulation.
model.set_ints('disable_zoom', [1])
```
