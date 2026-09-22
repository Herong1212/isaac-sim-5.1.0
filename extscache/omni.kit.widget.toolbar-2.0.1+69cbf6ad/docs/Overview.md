```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

`omni.kit.widget.toolbar` provides a toolbar-like widget that can host sub-widget such as ToolButton within itself. While the toolbar widget can be placed inside any UI frame, in a common Kit app setting, it is organized within `omni.kit.window.toolbar` to create the Main Toolbar in Kit. There can be only one instance of such toolbar widget globally.

The structure of a horizontal Toolbar looks like this:

```{mermaid}
graph TD
  subgraph toolbar_window["Toolbar Window (omni.kit.window.toolbar)"]
    subgraph toolbar_widget["Toolbar Widget (omni.kit.widget.toolbar)"]
      direction TB
      subgraph widget_group1[WidgetGroup 1]
          omni_ui_widget1(omni.ui.Widget 1)
      end
      subgraph widget_group2[WidgetGroup 2]
          direction TB
          omni_ui_widget2(omni.ui.Widget 2)
          omni_ui_widget3(omni.ui.Widget 3)
      end
      subgraph widget_group3[WidgetGroup 3]
          direction TB
          omni_ui_widget4(omni.ui.Widget 4)
          omni_ui_widget5(omni.ui.Widget 5)
      end
    end
  end
```

## Toolbar Widget

[Toolbar](omni.kit.widget.toolbar/omni.kit.widget.toolbar.Toolbar) class is both the registry and ui frame to host [WidgetGroup](omni.kit.widget.toolbar/omni.kit.widget.toolbar.WidgetGroup).

For examples of how to put [WidgetGroup](omni.kit.widget.toolbar/omni.kit.widget.toolbar.WidgetGroup) on a [Toolbar](omni.kit.widget.toolbar/omni.kit.widget.toolbar.Toolbar), please check [](USAGE_TOOLBAR).

## WidgetGroup

A widget group is a collection of one or more `omni.ui` widgets to be placed as associated entries on the toolbar. You can inherit this class and override various of its methods to create your custom widget group.

For example of how to create a [WidgetGroup](omni.kit.widget.toolbar/omni.kit.widget.toolbar.WidgetGroup), please check [](USAGE_WIDGET_GROUP).

## SimpleToolButton

[SimpleToolButton](omni.kit.widget.toolbar/omni.kit.widget.toolbar.SimpleToolButton) servers both as an example as well as a util class to demonstrate how a [WidgetGroup](omni.kit.widget.toolbar/omni.kit.widget.toolbar.WidgetGroup) with one `omni.ui.ToolButton` can be created. Check its documentation and source code for details.

## User Guide

- [](USAGE_TOOLBAR)
- [](USAGE_WIDGET_GROUP)
- [](CHANGELOG)
