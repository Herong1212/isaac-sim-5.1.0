# Usage Examples

An intuitive collection dialog will appear when call following api function, allowing you to customize the collection by selecting the appropriate configuration options.

These options include:
`USD Only`: Only collect USD files and other other dependencies are ignored (like material files and textures.) if it enabled.

`Material Only`: If this options is enabled, it will only collect all material related dependencies including textures, and USD files will be ignored.

`Flat Collection`: By default, it will collect USD project by keeping the directory structure. If this option is enabled, the directory structure will not be kept and all dependencies will be put into specified folders.

`Flat Collection Texture Options`: When collecting in Flat mode, users can specify the grouping for texture files via this option; Currently there are 3 available options:
| Options | Description |
| ------- | ----------- |
| Group by MDL | Textures will be grouped by their parent MDL file name. |
| Group by USD | Textures will be grouped by their parent USD file name. |
| Flat | All textures will be collected under the same hierarchy under "textures" folder. Note that there might be potential danger of textures overwriting each other, if they have the same names but belong to different assets/mdls. |

## Collect signle USD file
```python
from omni.kit.tool.collect import get_instance

# Initialize Collect Extension
collect_extension = get_instance()
collect_extension.collect("your_usd_path.usd")
```

## Collect Multiple USD Files
```python
from omni.kit.tool.collect import get_instance

# Initialize Collect Extension
collect_extension = get_instance()
collect_extension.collect_multiple(["path_to_first_usd.usd", "path_to_second_usd.usd"], "your_folder_name")
```

## Collect USD files in Folder
```python
from omni.kit.tool.collect import get_instance

# Initialize Collect Extension and Collect USD files in Folder
collect_extension = get_instance()
collect_extension.collect_multiple_in_folder("your_folder_path")
```
