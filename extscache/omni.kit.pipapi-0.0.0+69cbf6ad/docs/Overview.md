```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

Module to enable usage of ``pip install`` in Omniverse Kit environment. It wraps ``pip install`` calls and reroutes package installation into
user specified environment folder.

It also extends Kit Extension System by enabling extensions to depend on python packages and providing pip archive folders for offline pip install (prebundling).

# Important Notes

**This extension is not recommended for production. Installing packages at runtime relies on network availability, slow and security risk. Use this extension for prototyping and local development only.**

More information on pip packages in Kit can be found in [Using Python pip Packages](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/using_pip_packages.html).


# Usage

Simples example is to just call `omni.kit.pipapi.install()` before importing a package:

```py
import omni.kit.pipapi

omni.kit.pipapi.install("semver==2.13.0")

# use
import semver
ver = semver.VersionInfo.parse('1.2.3-pre.2+build.4')
print(ver)

```

It can also be used to call pip with custom arguments, e.g.:

```py
omni.kit.pipapi.call_pip(["--help"])
```

## Extension Config

All extensions that loaded after **omni.kit.pipapi** can specify those additional configuration settings in their extension.toml file:

### extension.toml

```toml
[python.pipapi]
# List of additional directories with pip achives to be passed into pip using ``--find-links`` arg.
# Relative paths are relative to extension root. Tokens can be used.
archiveDirs = ["path/to/pip_archive"]

# Commands passed to pip install before extension gets enabled. Can also contain flags, like `--upgrade`, `--no--index`, etc.
# Refer to: https://pip.pypa.io/en/stable/reference/requirements-file-format/
requirements = [
    "simplejson==6.1",
    "numpy"
]

# Optional list of modules to import before (check) and after pip install if different from packages in requirements.
modules = [
    "simplejson",
    "numpy"
]

# Allow going to online index. Required to be set to true for pip install call.
use_online_index = true

# Ignore import check for modules.
ignore_import_check = false

# Use this to specify a list of additional repositories if your pip package is hosted somewhere other
# than the default repo(s) configured in pip. Will pass these to pip with "--extra-index-url" argument
repositories = ["https://my.additional.pip_repo.com/"]

# Other arguments to pass to pip install. For example, to disable caching:
extra_args = ["--no-cache-dir"]
```

This is equivalent to just calling `omni.kit.pipapi.install()` in your extension's startup.
