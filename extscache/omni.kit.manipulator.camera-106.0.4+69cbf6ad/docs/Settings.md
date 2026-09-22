```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Normal settings
### "/exts/omni.kit.manipulator.camera/clampUpdates"
- default is 0.15
- clamp the max delta-time to a value when camera's velocity

### "/exts/omni.kit.manipulator.camera/flightMode/keyModifierAmount"
- default is 2
- Speed modifier amount in fly mode

### "/exts/omni.kit.manipulator.camera/forceStageUp"
- default is false
- Whether to simply use the stage-up axis instead or transform it via the camera's parent

### "/exts/omni.kit.manipulator.camera/objectCentric/type"
- default is 0
- Enable object-centric manipulation 0=off, 1=model-position, 2=pick-position

### "/exts/omni.kit.manipulator.camera/inertiaDecay"
- default is 1
- Inertial decay, 1=linear, 2=quadratic, 3=cubic

### "/exts/omni.kit.manipulator.camera/flyAcceleration"
- default is 1000
- Acceleration for inertia applied only during flight-mode

### "/exts/omni.kit.manipulator.camera/flyDampening"
- default is 10
- Dampening for inertia applied only during flight-mode

### "/exts/omni.kit.manipulator.camera/lookAcceleration"
- default is 2000
- Acceleration for inertia applied only with look

### "/exts/omni.kit.manipulator.camera/lookDampening"
- default is 20
- Dampening for inertia applied only with look


### "/persistent/exts/omni.kit.manipulator.camera/lookSpeed/0"
- default is 180.0
- lookSpeed 0 of camera

### "/persistent/exts/omni.kit.manipulator.camera/lookSpeed/1"
- default is 90.0
- lookSpeed 1 of camera

### "/persistent/exts/omni.kit.manipulator.camera/tumbleSpeed"
- default is 360.0
- tumbleSpeed of camera

### "/persistent/exts/omni.kit.manipulator.camera/moveSpeed/0"
- default is 1.0
- moveSpeed 0 of camera

### "/persistent/exts/omni.kit.manipulator.camera/moveSpeed/1"
- default is 1.0
- moveSpeed 1 of camera

### "/persistent/exts/omni.kit.manipulator.camera/moveSpeed/2"
- default is 1.0
- moveSpeed 2 of camera

### "/persistent/exts/omni.kit.manipulator.camera/flyViewLock"
- default is false
- Whether forward/backward and up/down movements ignore camera-view direction (similar to left/right strafe)

## GamePad settings
### "/exts/omni.kit.manipulator.camera/gamePad/enabled"
- default is true
- whether enable gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/trigger/action"
- default is "fly.y"
- Action of gamePad's trigger

### "/exts/omni.kit.manipulator.camera/gamePad/leftStick/action"
- default is "fly"
- Action of gamePad's leftStick action

### "/exts/omni.kit.manipulator.camera/gamePad/rightStick/action"
- default is "look"
- Action of gamePad's rightStick action

### "/exts/omni.kit.manipulator.camera/gamePad/shoulder/action"
- default is "fly.x"
- Action of gamePad's shoulder action

### "/exts/omni.kit.manipulator.camera/gamePad/dPad/action"
- default is "fly"
- Action of gamePad's dPad

### "/exts/omni.kit.manipulator.camera/gamePad/fly/scale"
- default is 1.0
- Fly scale of gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/fly/deadZone"
- default is 0.2
- Fly scale of gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/look/scale"
- default is 0.75
- Look scale of gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/look/deadZone"
- default is 0.1
- Look deadZone of gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/speed/scale"
- default is 0.5
- Speed scale of gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/button/a/action"
- default is "speed.y"
- Button A's action of gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/button/b/action"
- default is "speed.y"
- Button B's action of gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/button/a/scale"
- default is 1.0
- Button A's scale of gamePad

### "/exts/omni.kit.manipulator.camera/gamePad/button/b/scale"
- default is -1.0
- Button B's scale of gamePad
