```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Text Editor extension provides a widget-based text editor by binding to ImGuiColorTextEdit. It enables text editing with built-in support for syntax highlighting and error markers. The extension serves as a lightweight tool for integrating editable text areas into Omniverse Kit applications, making it easy to work with code or structured content.

```{image} ../../../../source/extensions/omni.kit.widget.text_editor/data/preview.png
---
align: center
---
```


## Concepts

- This extension is built on top of Omni UI and leverages ImGuiColorTextEdit for rendering its interface.
- The core element is the [TextEditor](omni.kit.widget.text_editor/omni.kit.widget.text_editor.TextEditor) widget, which supports common editing functions like copy, cut, paste, undo, redo, and selection.
- It includes support for syntax highlighting with predefined styles (e.g., Python, C++, HLSL) and allows choosing between different color themes (Dark, Light, RetroBlue).

## Functionality

- The [TextEditor](omni.kit.widget.text_editor/omni.kit.widget.text_editor.TextEditor) widget offers a range of editing capabilities including managing text, selection, and error marking.
- It provides properties to switch between read-only and editable modes, as well as to customize the text content via simple APIs.
- Developers can configure syntax rules and palettes for tailored visual feedback, enhancing clarity when editing source code or structured text.

## Relationships

- The extension declares a dependency on Omni UI, ensuring integration with the broader UI system in Omniverse Kit.
- It is designed to work seamlessly within applications that require embedded text editing features without the need for additional third-party tools.

