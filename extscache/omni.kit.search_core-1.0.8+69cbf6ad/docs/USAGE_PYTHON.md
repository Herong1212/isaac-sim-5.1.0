# Usage Examples

## Register Search Models and Monitor Registry Changes

```python
import omni.kit.search_core as search_core
from omni.kit.search_core import AbstractSearchModel

# Create a simple search model class
class SimpleSearchModel(AbstractSearchModel):
    @property
    def items(self):
        # Return search results here
        return []

# Get the search engine registry
registry = search_core.SearchEngineRegistry()

# Define a callback for when engines change
def on_engines_changed():
    print(f"Available search engines: {registry.get_search_names()}")

# Subscribe to changes in the registry
subscription = registry.subscribe_engines_changed(on_engines_changed)

# Register our search model (this will trigger the callback)
model_subscription = registry.register_search_model("SimpleSearch", SimpleSearchModel)

# Get available search engines
all_engines = registry.get_search_names()
print(f"Available search engines: {all_engines}")

# Get available search engines for a specific server
server_engines = registry.get_available_search_names("MyServer")
print(f"Search engines for 'MyServer': {server_engines}")

# Get a specific search model class
search_model_class = registry.get_search_model("SimpleSearch")

# Unregister (this will also trigger the callback)
model_subscription = None  # This will deregister the model automatically
```
---

## Create Custom Search Model with Items

```python
import asyncio
import omni.kit.search_core as search_core
from omni.kit.search_core import AbstractSearchModel, AbstractSearchItem

# Create a custom search item
class MySearchItem(AbstractSearchItem):
    def __init__(self, name, path, is_folder=False, size=0):
        self._name = name
        self._path = path
        self._is_folder = is_folder
        self._size = size
        self._date = None
        
    @property
    def path(self):
        return self._path
        
    @property
    def name(self):
        return self._name
        
    @property
    def date(self):
        return self._date
        
    @property
    def size(self):
        return self._size
        
    @property
    def icon(self):
        return None
        
    @property
    def is_folder(self):
        return self._is_folder
        
    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return None

# Create a custom search model
class MySearchModel(AbstractSearchModel):
    def __init__(self, search_text="", current_dir="", search_lifetime=None):
        super().__init__()
        self._search_text = search_text
        self._current_dir = current_dir
        self._search_lifetime = search_lifetime
        self._search_items = []
        
        # Start asynchronous search
        asyncio.ensure_future(self._perform_search())
        
    @property
    def items(self):
        return self._search_items
        
    async def _perform_search(self):
        # Simulate search delay
        await asyncio.sleep(1)
        
        # Add some search results
        self._search_items = [
            MySearchItem("Item 1", "/path/to/item1", False, 1024),
            MySearchItem("Item 2", "/path/to/item2", True, 0),
            MySearchItem("Item 3", "/path/to/item3", False, 2048)
        ]
        
        # When search results are updated, subscribers will be notified
        # No need to manually call protected methods
```
---

## Use SearchLifetimeObject for Callbacks

```python
import omni.kit.search_core as search_core

def search_completed_callback():
    print("Search operation completed!")

# Create a SearchLifetimeObject to manage the callback
search_lifetime = search_core.SearchLifetimeObject(search_completed_callback)

# Later when search is finished
search_lifetime.destroy()  # This calls the callback and cleans up
```
