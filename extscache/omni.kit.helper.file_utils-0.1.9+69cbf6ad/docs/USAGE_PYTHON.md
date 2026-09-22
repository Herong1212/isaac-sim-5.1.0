# Usage Examples


## Get All File Extensions Of Given Asset Type.
```python
from omni.kit.helper.file_utils import asset_types

exts = asset_types.asset_type_exts("anim_usd")
print(f"The exts of anim_usd is {exts}.")
# Expected: [".anim.usd", ".anim.usda", ".anim.usdc", ".anim.usdz"]
```

## Determine File Asset Type

```python
from omni.kit.helper.file_utils import asset_types

# Determine the asset type of an image file
image_filename = "example.jpg"
image_asset_type = asset_types.get_asset_type(image_filename)
print(f"The asset type of {image_filename} is {image_asset_type}.")
# Expected: asset_types.ASSET_TYPE_IMAGE

# Determine the asset type of a sound file
sound_filename = "soundtrack.wav"
sound_asset_type = asset_types.get_asset_type(sound_filename)
print(f"The asset type of {sound_filename} is {sound_asset_type}.")
# Expected: asset_types.ASSET_TYPE_SOUND
```

## Retrieve Icon for Asset Type

```python
from omni.kit.helper.file_utils import asset_types

# Get the icon for a material asset
material_filename = "material.mtlx"
material_icon = asset_types.get_icon(material_filename)
print(f"The icon for {material_filename} is located at {material_icon}.")
```

## Retrieve Thumbnail for Asset Type

```python
from omni.kit.helper.file_utils import asset_types

# Get the thumbnail for an FBX file
fbx_filename = "model.fbx"
fbx_thumbnail = asset_types.get_thumbnail(fbx_filename)
print(f"The thumbnail for {fbx_filename} is located at {fbx_thumbnail}.")
```

## Check if File is a Specific Asset Type

```python
from omni.kit.helper.file_utils import asset_types

# Check if the file is a Python script
filename = "script.py"
if asset_types.is_asset_type(filename, asset_types.ASSET_TYPE_SCRIPT):
    print(f"{filename} is a script file.")
else:
    print(f"{filename} is not a script file.")
```

## Register Custom File Extensions

```python
from omni.kit.helper.file_utils import asset_types

# Register a new asset type with custom file extensions
asset_types.register_file_extensions("custom_type", [".custom", ".ct"])

# Verify if the file is recognized as the newly registered type
filename = "example.custom"
if asset_types.is_asset_type(filename, "custom_type"):
    print(f"{filename} is recognized as a custom type.")
else:
    print(f"{filename} is not recognized as a custom type.")
```

## Emit a file event to the event stream

```python
from omni.kit.helper.file_utils import FileEventModel

FILE_SAVED_GLOBAL_EVENT: str = "omni.kit.helper.file_utils.FILE_SAVED"
filename = "saved file"
# Emit a file saved event to the event stream
omni.kit.app.queue_event(FILE_SAVED_GLOBAL_EVENT, FileEventModel(url=filename).dict())
```

## Get Last Opened URL of a Specific Asset Type

```python
from omni.kit.helper.file_utils import get_last_url_opened, asset_types

# Retrieve the last opened URL of an image file
last_image_url = get_last_url_opened(asset_type=asset_types.ASSET_TYPE_IMAGE)
print(f"The last opened image file was at {last_image_url}.")
```

## Get Last Saved URL of a Specific Asset Type

```python
from omni.kit.helper.file_utils import get_last_url_saved, asset_types

# Retrieve the last saved URL of a sound file
last_sound_url = get_last_url_saved(asset_type=asset_types.ASSET_TYPE_SOUND)
print(f"The last saved sound file was at {last_sound_url}.")
```

## Clear File Event Queue

```python
from omni.kit.helper.file_utils import reset_file_event_queue

# Clear the file event queue
reset_file_event_queue()
print("File event queue has been cleared.")
```