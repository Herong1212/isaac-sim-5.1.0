# Usage Examples

## Register a New Stage Template
```python
import omni.kit.stage_template.core as stage_template_core

# Define a function to populate the new stage after creation
def create_custom_stage(rootname, usd_context_name):
    # Create basic DistantLight
    usd_context = omni.usd.get_context(usd_context_name)
    stage = usd_context.get_stage()
    with Usd.EditContext(stage, stage.GetRootLayer()):
        # create Environment
        omni.kit.commands.execute(
            "CreatePrim",
            prim_path="/Environment",
            prim_type="Xform",
            select_new_prim=False,
            create_default_xform=True,
            context_name=usd_context_name
        )

        omni.kit.commands.execute(
            "CreatePrim",
            prim_path="/Environment/defaultLight",
            prim_type="DistantLight",
            select_new_prim=False,
            # https://github.com/PixarAnimationStudios/USD/commit/b5d3809c943950cd3ff6be0467858a3297df0bb7
            attributes={UsdLux.Tokens.inputsAngle: 1.0, UsdLux.Tokens.inputsIntensity: 3000} if hasattr(UsdLux.Tokens, 'inputsIntensity') else \
                {UsdLux.Tokens.angle: 1.0, UsdLux.Tokens.intensity: 3000},
            create_default_xform=True,
            context_name=usd_context_name
        )

# Register the new stage template
stage_template_core.register_template("CustomStage", create_custom_stage, group=0)
```

## Create a New Stage Asynchronously with a Template
```python
import asyncio
import omni.kit.stage_template.core as stage_template_core

# Asynchronously create a new stage using the registered template
async def create_stage_async():
    result, error_message = await stage_template_core.new_stage_async(template="CustomStage")
    if result:
        print("Stage created successfully")
    else:
        print(f"Failed to create stage: {error_message}")

# Ensure the coroutine is executed
asyncio.ensure_future(create_stage_async())
```

## Create a New Stage With a Callback Function
```python
import omni.kit.stage_template.core as stage_template_core

# Define a callback function to be called after the new stage is created
def on_new_stage(created, error_message):
    if created:
        print("Stage created successfully.")
    else:
        print(f"Stage creation failed with error: {error_message}")

# Create a new stage with a callback using the 'empty' template
stage_template_core.new_stage_with_callback(on_new_stage, template="empty")
```

## Unregister a Stage Template
```python
import omni.kit.stage_template.core as stage_template_core

# Unregister a previously registered stage template
stage_template_core.unregister_template("CustomStage")
```
