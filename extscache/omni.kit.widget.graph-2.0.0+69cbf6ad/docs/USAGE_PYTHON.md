# Usage Examples
The following two sessions serve as one complete example of a simple graph, which uses the GraphNodeDelegate, GraphModel and GraphView. It allows users to move nodes and create/remove connections.

## Graph Model
In this example, we create a graph Model which inherits GraphModel. It has nodes, name, ports, inputs, outputs and position which are essential to support graph node connections and transformations.

```python
from omni.kit.widget.graph.graph_model import GraphModel

inputs = ["First.color1", "First.color2", "Third.size"]
outputs = ["First.result", "Second.out", "Third.outcome"]
connections = {"First.color1": ["Second.out"], "First.color2": ["Third.outcome"]}

class Model(GraphModel):
    def __init__(self):
        super().__init__()
        self.__positions = {}

    @property
    def nodes(self, item=None):
        if item:
            return

        return sorted(set([n.split(".")[0] for n in inputs + outputs]))

    @property
    def name(self, item=None):
        return item.split(".")[-1]

    @property
    def ports(self, item=None):
        if item in inputs:
            return

        if item in outputs:
            return

        return [n for n in inputs + outputs if n.startswith(item)]

    @property
    def inputs(self, item):
        if item in inputs:
            return connections.get(item, [])

    @inputs.setter
    def inputs(self, value, item=None):
        if item is None:
            return

        for v in value:
            if item:
                if item not in connections:
                    connections[item] = []

                if v not in connections:
                    connections[item].append(v)
                    if item in inputs and v in inputs: # same side connection
                        connections[v]= [item]
        if not value:
            connections.pop(item)

        self._item_changed(None)

    @property
    def outputs(self, item):
        if item in outputs:
            return []

    @property
    def position(self, item=None):
        """Returns the position of the node"""
        return self.__positions.get(item, None)

    @position.setter
    def position(self, value, item=None):
        """The node position setter"""
        self.__positions[item] = value
```

## Graph View
GraphView is the visualisation layer which behaves like a regular widget and displays nodes and their connections with delegate.

```python
import omni.ui as ui
from omni.kit.widget.graph.graph_node_delegate import GraphNodeDelegate
from omni.kit.widget.graph.graph_view import GraphView

# define the style
style = GraphNodeDelegate.get_style()
# Don't use the image because the image scaling looks different in editor and kit-mini
style["Graph.Node.Footer.Image"]["image_url"] = ""
style["Graph.Node.Header.Collapse"]["image_url"] = ""
style["Graph.Node.Header.Collapse::Minimized"]["image_url"] = ""
style["Graph.Node.Header.Collapse::Closed"]["image_url"] = ""

window = ui.Window("Graph", width=768, height=512)
with window.frame:
    delegate = GraphNodeDelegate()
    # Note the Model can use the Model() defined in the previous example, or a new customized model.
    model = Model()
    graph_view = GraphView(model=model, delegate=delegate, style=style, pan_x=600, pan_y=170)
```
