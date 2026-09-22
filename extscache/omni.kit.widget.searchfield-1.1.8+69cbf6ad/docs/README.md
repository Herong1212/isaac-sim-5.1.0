# Search field widget

To use:

```
from omni.kit.widget.searchfield import SearchField

def on_search(search_words: optional[List[str]]):
    if search_words is None:
        print("Nothing to search")
    else:
        print(f"search by words: {search_words}")

search_field = SearchField(on_search_fn=on_search)
```

Cleanup:

```
search_field.destroy()
```