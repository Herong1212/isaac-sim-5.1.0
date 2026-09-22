```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.window.console` extension provides a console window within the application, allowing users to interact with console output directly from the UI. It also allows users to execute commands in `Command Field`.

## Commands
There are two types of commands:
- Pre-defined commands: following commands are pre-defined and could be executed directly.
    - `CLEAR`: Clear console.
    - `HELP`: Show help information.
    - `HISTORY`: List command history.
    - `QUIT`: Quit kit immediately.
    - `OPEN`: Open a USD file. Followed by the path of the USD file.
    - `CLOSE`: Close current USD file.
- Scripts: Scripts (`.py` and `.lst`) in pre-defined folders could be executed too. The script folders are defined in `/app/python/scriptFolders` setting. Type file name to execute directly.

## User Guide
- [CHANGELOG](CHANGELOG)
- [SETTINGS](SETTINGS)
