# Registry 2.0 Architecture

## File Layout

```
registry.gz
summaries.gz
packages/
	omni.foo.gz
	omni.bar.gz
archives/
	omni.foo/
		omni.foo-1.0.0+wx64.r.json
		omni.foo-1.0.0+lx64.r.json
		omni.foo-1.2.0+wx64.r.json
	omni.bar/
		...
```

- **registry.gz** - is a main file to store registry information. Client will always fetch it first. It contains:
    * files - a map of all files required for dependency resolution and their hashes (archives subfolder is not in it).

    *Format: gzip json*

    More fields are likely to be added in the future to store registry wide information. Example of that file:

    ```json
    {
        "files": {
            "summaries.gz": "3fdb1367",
            "packages/omni.foo.zip": "d8501f51",
            "...": "..."
        }
    }
    ```

    To sync with remote registry client looks in `files` field and can compare with the current files. Thus downloading only changed files.

- **summaries.gz** - a map of the extension name to the dictionary with all the data required to list extensions. It is not used for dependency resolutio, but can be used to list extensions in UI, search, find the latest version etc:

    ```
    {
        "omni.foo": { "package": { "title": "Foo Extension", ... }
        "omni.bar": { "package": { "title": "Bar Extension", ... }
        ...
    }
    ```

    *Format: gzip json*

- **packages/[ext].gz** - file with all packages/versions for each extension.

    Each line has a package id, one space, json with all package data

    ```
        1.0.0+wx64.r {"dependencies": {...}, "targets": {...} }
        1.0.1+lx64.r {"dependencies": {...}, "targets": {...} }
        1.1.0+wx64.r {"dependencies": {...}, "targets": {...} }
    ```

    When the solver encounters a dependency of a such name it can load this file and get all versions. Actual json objects can be parsed on demand during the search.

    *Format: gzip txt file*


- **archives/** - Stores per package full metadata. Also store archives unless using other storage (like packman).


## Operations

### Sync

Index sync is like a git pull. We maintain a local copy of the whole registry required to solve dependencies. That includes `registry.gz`, `summaries.gz` and `packages/[ext].gz`.

 To sync:

1. Download `registry.gz` and read `files` field.
2. Compare with local `registry.json` and download changed files. All files are stored in decompressed form (`.gz` -> `.json`).
3. Load `summaries.json` and return it to the extension manager. Thus it has one latest version per extension available immediately.
4. Path to the local registry is written in a `#meta/local_cache_path` of the returned dictionary.
5. Extension manager uses that path to load per extension versions files (**packages/[ext].gz**) when needed.

### Publish

1. Push package to the remote storage (like packman) and get a URL.
2. Write `package/archivePath` to the extension dictionary (config).
3. Extension dictionary (config) is uploaded to:
    - to `archives/[ext_name]/[package-id].json` (full metadata in json form)
    - to `summaries.gz` if version is the latest (shorter form, only title, description, icon, etc)
    - to `packages/[ext].gz`(shortest form, only version and dependencies)
4. Re-hash and push all changed registry files to the remote (like git push).
