# Usage Examples

## Create a Basic Search Field

```python
import omni.ui as ui
from omni.kit.widget.search_delegate import SearchField

# Callback function to process search results
def on_search_results(results_model):
    if results_model:
        # Get search result items
        items = results_model.get_item_children(None)
        print(f"Found {len(items)} search results")
        for item in items:
            print(f"- {item.path}")
    else:
        print("No search results found")

# Create a window for the search field
window = ui.Window("Search Example", width=400, height=100)
with window.frame:
    # Create the search field with our callback
    search_field = SearchField(on_search_results)
    
    # Build the UI components
    search_field.build_ui()
    
    # Set the search directory
    search_field.search_dir = "/path/to/search"
```

---

## Implement a Custom Search Delegate

```python
import omni.ui as ui
from omni.kit.widget.search_delegate import SearchDelegate

class CustomSearchDelegate(SearchDelegate):
    def __init__(self):
        super().__init__()
        self._container = None
        self._search_field = None
        self._is_visible = True
        self._is_enabled = True
        self._search_directory = "/default/path"
    
    @property
    def visible(self):
        return self._is_visible
    
    @property
    def enabled(self):
        return self._is_enabled
    
    @property
    def search_dir(self):
        return self._search_directory
    
    @search_dir.setter
    def search_dir(self, search_dir):
        self._search_directory = search_dir
        print(f"Search directory set to: {search_dir}")
    
    def build_ui(self):
        # Create UI components for the search delegate
        self._container = ui.VStack(height=0)
        with self._container:
            with ui.HStack(height=0):
                # Create the search input field
                self._search_field = ui.StringField()
                
                # Add a search button
                ui.Button(
                    "Search",
                    clicked_fn=lambda: print(f"Searching in: {self._search_directory}")
                )
    
    def destroy(self):
        # Clean up resources
        self._container = None
        self._search_field = None

# Create a window with our custom search delegate
window = ui.Window("Custom Search", width=400, height=100)
with window.frame:
    custom_search = CustomSearchDelegate()
    custom_search.build_ui()
    custom_search.search_dir = "/my/search/directory"
```

---

## Complete Search Implementation

```python
import omni.ui as ui
from omni.kit.widget.search_delegate import SearchField, SearchResultsModel
from omni.kit.search_core import SearchEngineRegistry, AbstractSearchModel, AbstractSearchItem
from datetime import datetime
from typing import List

# Create a mock search engine for demonstration
class MockSearchItem(AbstractSearchItem):
    def __init__(self, name, path, is_folder=False):
        self.name = name
        self.path = path
        self.is_folder = is_folder
        self.date = datetime.now()
        self.size = 1024  # Mock file size in bytes

class MockSearchModel(AbstractSearchModel):
    def __init__(self, search_text="", current_dir=""):
        self._items = []
        
        # Create mock search results based on search text
        if search_text:
            for word in search_text.split():
                self._items.append(
                    MockSearchItem(word, f"{current_dir}/{word}.usd")
                )
    
    @property
    def items(self) -> List[AbstractSearchItem]:
        return self._items

# Create the main window
window = ui.Window("Search Integration Example", width=600, height=400)

# Variables to store UI elements
tree_view = None
result_label = None

# Callback to handle search results
def on_search_results(results_model):
    global tree_view, result_label
    
    if results_model:
        items = results_model.get_item_children(None)
        result_label.text = f"Found {len(items)} results"
        
        # Update the tree view with new results
        tree_view.model = results_model
    else:
        result_label.text = "No results found"
        tree_view.model = None

# Register our mock search engine
search_registry = SearchEngineRegistry()
subscription = search_registry.register_search_model("MOCK_SEARCH", MockSearchModel)

# Create the UI layout
with window.frame:
    with ui.VStack():
        # Create a search field at the top
        search_field = SearchField(on_search_results)
        search_field.build_ui()
        search_field.search_dir = "/example/search/directory"
        
        # Label to show number of results
        result_label = ui.Label("Enter search terms above")
        
        # Tree view to display search results
        tree_view = ui.TreeView(None, root_visible=False)

# Note: Remember to call these when you're done with the search functionality:
# search_field.destroy()
# subscription = None
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.search_delegate/data/docs_images/complete_search_implementation.png
---
align: center
---
```

---

## Work with SearchResultsModel and Items

```python
import omni.ui as ui
from omni.kit.widget.search_delegate import SearchResultsModel, SearchResultsItem
from omni.kit.search_core import AbstractSearchModel, AbstractSearchItem
from omni.kit.widget.filebrowser import FileBrowserItemFields
from datetime import datetime
from typing import List

# Create a simple event subscription class
class EventSubscription:
    def __init__(self, signal, callback):
        self.signal = signal
        self.callback = callback
        self.active = True
    
    def unsubscribe(self):
        if self.active:
            self.active = False
            if self.signal and hasattr(self.signal, "subscribers"):
                if self.callback in self.signal.subscribers:
                    self.signal.subscribers.remove(self.callback)

# Create a simple search item implementation
class SimpleSearchItem(AbstractSearchItem):
    def __init__(self, name, path, is_folder=False):
        super().__init__()
        # Store values in protected attributes and use property getters
        self._name = name
        self._path = path
        self._is_folder = is_folder
        self._date = datetime.now()
        self._size = 1024  # Mock file size in bytes
    
    # Override the properties to provide getters
    @property
    def name(self):
        return self._name
    
    @property
    def path(self):
        return self._path
    
    @property
    def is_folder(self):
        return self._is_folder
    
    @property
    def date(self):
        return self._date
    
    @property
    def size(self):
        return self._size

# Create a simple search model implementation
class SimpleSearchModel(AbstractSearchModel):
    def __init__(self, search_text="", current_dir=""):
        self._items = []
        # Add a signal for item changed events with subscribers list
        self.__on_item_changed = type("Signal", (), {"subscribers": []})()
        
        # Create some mock search results based on search text
        if search_text:
            for word in search_text.split():
                self._items.append(
                    SimpleSearchItem(f"{word}_file", f"{current_dir}/{word}.usd")
                )
    
    @property
    def items(self) -> List[AbstractSearchItem]:
        return self._items
    
    # Implement the subscribe_item_changed method
    def subscribe_item_changed(self, fn):
        if not hasattr(self.__on_item_changed, "subscribers"):
            self.__on_item_changed.subscribers = []
        self.__on_item_changed.subscribers.append(fn)
        return EventSubscription(self.__on_item_changed, fn)

# Use a simplified example that doesn't require the TreeView
window = ui.Window("Search Results Example", width=500, height=300)
with window.frame:
    with ui.VStack():
        # Create a search model with mock data
        search_model = SimpleSearchModel("material texture lighting", "/path/to/search")
        
        # Display search terms directly instead of using SearchResultsModel
        ui.Label("Search terms: material, texture, lighting")
        
        # Display the items directly from the search model
        for item in search_model.items:
            ui.Label(f"Result: {item.name} - {item.path}")
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.search_delegate/data/docs_images/work_with_searchresultsmodel_and_items.png
---
align: center
---
```

