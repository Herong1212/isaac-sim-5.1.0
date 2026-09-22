```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Commands Utils extension provides a dedicated viewer window for exploring and reviewing commands executed within the Omniverse Kit environment. It is designed to help users and developers quickly inspect command history and search through registered commands without requiring any direct code interaction. The extension offers a user-friendly interface for visualizing command parameters, execution history, and availability of undo functionality.

```{image} ../../../../source/extensions/omni.kit.window.commands/data/preview.png
---
align: center
---
```

## Functionality

- **Main UI Window:** A lightweight window that brings together **Command History Viewer** and **Command Search**. This window can be shown or hidden as needed via menu actions or user controls.
- **Command History Viewer:** Provides a detailed list of previously executed commands along with their parameters and undo details. This history panel lets users review command execution data in a structured tree view.
- **Command Search:** A window enables users to browse through the available commands registered in the system. The search panel formats the command items into a simple list, making it easier to locate specific commands by name or extension.

## Configuration

- **Window Behavior:** The extension includes a setting (windowOpenByDefault) that controls whether the commands viewer window opens automatically when the extension starts. This setting provides flexibility in how the viewer is accessed during an Omniverse Kit session.

## Integration

- **Interoperability:** The extension tightly integrates with other Omniverse Kit modules such as **omni.kit.commands** for command registration and **omni.kit.menu.utils** for menu integration. This helps maintain a cohesive user experience across the Omniverse Kit environment.
- **Data Presentation:** By leveraging Omni UI’s abstract models and delegates, the extension ensures that command data is consistently formatted and interactive within the designated viewer window.

## Relationships

- **Dependencies:** The extension relies on several other components including **omni.kit.clipboard**, **omni.kit.commands**, **omni.kit.pip_archive**, **omni.ui**, and **omni.kit.menu.utils.** These dependencies help provide a complete, robust environment for command viewing and interaction.

This extension is ready to use immediately once enabled, offering a streamlined interface for reviewing command activity within Omniverse Kit.