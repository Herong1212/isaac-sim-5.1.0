```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Report all the stats

```python
import omni.stats

stats = omni.stats.get_stats_interface()
scopes = stats.get_scopes()

for scope in scopes:
    stat_nodes = stats.get_stats(scope["scopeId"])
    print(scope["name"])
    for node in stat_nodes:
        print("Name: " + node["name"], " | Value: " + str(node["value"]) + " | Description: " + node["description"])

```
