# Usage Examples

## Export USD to USDZ Format

```python
import asyncio
import omni.kit.usdz_export

# Path to the source USD file
source_usd_path = "/path/to/source/file.usd"

# Path where the USDZ file will be saved
output_usdz_path = "/path/to/output/file.usdz"

# Export the USD file to USDZ format
async def export_to_usdz():
    await omni.kit.usdz_export.usdz_export(source_usd_path, output_usdz_path)
    print(f"Successfully exported USDZ to {output_usdz_path}")

# Run the export asynchronously
asyncio.ensure_future(export_to_usdz())
```

---

## Export Current Stage to USDZ

```python
import asyncio
import omni.usd
import omni.kit.usdz_export

# Get the current stage
stage = omni.usd.get_context().get_stage()
if stage:
    # Get the layer identifier of the current stage
    stage_identifier = stage.GetRootLayer().identifier

    # Define output path for the USDZ file
    output_path = "/path/to/output/exported_stage.usdz"

    # Export the current stage to USDZ format
    async def export_current_stage():
        await omni.kit.usdz_export.usdz_export(stage_identifier, output_path)
        print(f"Current stage exported to {output_path}")

    # Run the export asynchronously
    asyncio.ensure_future(export_current_stage())
else:
    print("No stage is currently loaded")
```
---

## Export with File Exporter Dialog

```python
import asyncio
from functools import partial
import omni.kit.usdz_export
from omni.kit.window.file_exporter import get_file_exporter

def show_usdz_export_dialog(layer_identifier):
    # Prepare handler for the export operation
    def on_export(callback, flatten, filename, dirname, extension="", selections=None):
        # Construct full path for the output file
        path = f"{dirname}{filename}{extension}"

        # Launch the export process
        asyncio.ensure_future(omni.kit.usdz_export.usdz_export(layer_identifier, path))

    # Show file exporter dialog
    file_picker = get_file_exporter()
    file_picker.show_window(
        title="Export To USDZ",
        export_button_label="Export",
        export_handler=partial(on_export, None, False),
        file_extension_types=[(".usdz", "Zipped package")],
    )

# Usage example - pass an identifier for the USD layer you want to export
show_usdz_export_dialog("/path/to/source/layer.usd")
```