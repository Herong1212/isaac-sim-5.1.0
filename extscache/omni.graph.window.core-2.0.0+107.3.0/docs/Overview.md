```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`,{ref}`changelog_omni_graph_window_core`
```

(ext_omni_graph_window_core)=

# Overview

This extension contains the base functionality that is shared by editors of OmniGraph.
It is based `omni.kit.graph.editor.core` and provides base implementations which are intended to be specialized by
editor windows for particular graph types.

## Coordinate Systems

There are three coordinate systems used in the graph editor code: screen, view and mouse.

Screen coordinates are the pixel coordinates of the display device, with (0, 0) in the upper left corner of
the display.

View coordinates are the coordinates within the `GraphView` widget.
Internally `GraphView` uses an `omni.ui.CanvasFrame` to display the nodes and connections. `CanvasFrame` allows its
contents to be zoomed and panned, meaning that view coordinates are not simply an offset from screen coordinates.
(If you see references to canvas coordinates those are the same as view coordinates.)
To convert screen coordinates to view coordinates call `GraphView.screen_to_view()`. There is currently no method
available for converting from view coordinates back to screen.

Mouse coordinates are the coordinates supplied by mouse events which occur over the `GraphView`. Normally these are
the same as screen coordinates but may differ depending upon certain settings. `GraphView.mouse_to_screen()` and
`GraphView.mouse_to_view()` can be used to convert mouse coordinates in a consistent manner, regardless of settings.
