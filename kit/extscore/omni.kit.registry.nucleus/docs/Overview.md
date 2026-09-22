# Overview

Nucleus registry implementation for extension system.

It is important for such extension to be enabled as soon as possible so that other extensions can use it as a bootstrap to be downloaded. Once enabled it registers itself in the extension manager as extension registry provider.


## Settings


Refer to `extension.toml` file for settings.


## Basic Principle

In the provided nucleus URL it stores all extensions as zip archives and special `index.zip` file (zipped json) which contains information about each extension stored.



## Setting Extension Registries

To change the list of extension registries to sync to you can use those settings:

```toml
[settings.exts."omni.kit.registry.nucleus"]
# URL where to store archives and index of extensions (can be local filesystem too). They are being pulled in order,
# so if multiple registries have a package with the same name the one that is specified first is prioritized.
# Both Carbonite and custom tokens (defined below under "tokens" key) are supported in URLs. That allows to reuse same
# URL parts for multiple registries.
# `optional` flag if set is used to ignore registry if it's unreachable, otherwise it will be treated as an error.
registries = [
    #{ name = "kit/default", url = "${main_registry_url}/kit/default", optional = false },
]
```

A name is used for UI, debug purposes and to specify which registry to publish to when there are multiple.

By default, **Kit** has some default registry set in core config (`kit-core.json`) with setting above.

An example of overriding a registry with CLI:

```bash
kit --/exts/omni.kit.registry.nucleus/registries/0/url="C:/temp"
```


## Supported Registries Backends

Omniverse Client library is used under the hood so anything that it supports can be used as storage. If registry doesn't exist it will be created automatically when the first extension is published.

* nucleus server, e.g. `omniverse://kit-extensions.ov.nvidia.com/exts`
* local filesystem, e.g. `C:/my_registry`
* http/https, e.g. `https://my_registry.com/exts` (read only)

Http registry is read-only, so it can't be used to publish extensions. However, a common pattern is to publish extensions to a local filesystem or nulceus server and then sync them to http registry for distribution.


## Nucleus Accounts

To read and write to nucleus server you need a nucleus account. Use this setting to specify it:

```toml
[settings.exts."omni.kit.registry.nucleus"]
accounts = [
    { url = "omniverse://kit-extensions.ov.nvidia.com", read = "[user]:[pass]", write = "[user]:[pass]" }
]
```

User and password is separated by `:`. A separate account can be set for read and write operations.

Different accounts per different hosts can be set. Otherwise an empty `url` matches all hosts.


## Setting Up Your Own Registry

You can setup your own registry Kit can publish to on nucleus server or filesystem (can be a shared network drive). A read-only http registry can also be used, which can be a copy (or mirror) of the registry you publishing in.

No initial setup is required for a new registry, if path is empty it will be created automatically when the first extension is published.

For nucleus server you need to provide an account with write permissions for publishing. Use settings from above if you directly call `kit --publish` or (preferred) use repo publishing tool.


## Repo Publish Tool

Kit comes with a repo tool for publishing extensions. It can be called as:

```bash
./repo.sh publish_exts
```

Here are some useful settings for own nucleus registry in `repo.toml`:

```toml
[repo_publish_exts]

signing.enabled = false # disable signing
use_packman_to_upload_archive = false # disable packman upload
write_auth = "admin:admin" # auth for write, can use `${env:VAR}` syntax to get from environment

# add your own nucleus registry
registries = [
    { name = "my_registry", url = "omniverse://localhost/exts" }
]

# extensions to publish, wildcard can be used:
exts.include = [
    "sample.extension",
]
```

Refer to `repo_tools.toml` file in Kit (tool definition config) for all the default settings of `repo_publish_exts` tool.
