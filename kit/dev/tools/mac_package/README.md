Omniverse Kit CLI Prototype for Mac OS
======================================

Omniverse Kit CLI is now building and working for Mac OS!  There is *minimal* functionality available in this
build.

*DO NOT DISTRIBUTE THESE BUILDS OUTSIDE OF NVIDIA*

The expectation is that these builds can:

* Complete the basic startup tasks including reading the various config files.
* Load and initialize python 3.10.
* Load the main app plugin (`kernel/plugins/omni.kit.app.plugin`) and its python bindings.
* Load the extension manager plugin (`kernel/plugins/omni.ext.plugin`) and its python bindings.
* Load basic C++ and python extensions using the `--ext-folder` and `--enable` command line options.
* Do some basic command line interaction through `stdin`, `stdout`, and `stderr`.
* Load and execute most `omni.ui` extensions, but only those without `USD` requirements

These builds are *not* expected to:

* Load other generic plugins or extensions that do not explicitly ship with these bundles.
* Do anything when double clicking `Kit.app` from Finder.


Installation and Running
========================

* Unzip the `Omniverse Kit.zip` file to the directory of choice.
* Choose either the debug or release build of `Kit.app` by changing into the appropriate directory.
* Run Kit with command lines such as the following:
  * `Kit.app/Contents/MacOS/kit`: launch the main app and have it output its command line usage info.
  * `Kit.app/Contents/MacOS/kit --list-exts`: list the available extensions.  This can be combined with
    the `--ext-folder` to add external extension folders as well.
  * `Kit.app/Contents/MacOS/kit -vv`: enable verbose logging.
  * `Kit.app/Contents/MacOS/kit --ext-folder <path_to_exts>`: add another external extension folder to
    be searched when scanning for extensions.  This path may contain one or more extensions.  Multiple
    extension folders may be specified by using the `--ext-folder` multiple times on the same command line.
  * `Kit.app/Contents/MacOS/kit --enable <extension_id>`: run the startup and shutdown of an extension.
    This can include an extension that is added to the scan using the `--ext-folder` option on the same
    command line.
  * `Kit.app/Contents/MacOS/kit --/app/printConfig=true`: print the entire settings tree once Kit has
    completed its initial startup.
  * `Kit.app/Contents/MacOS/kit --</path/to/setting>=<value>`: sets the value for a setting key for the
    given run.  Only settings under the `/persistent/` branch will be saved out to the user config file.


Example Extension
=================

Jordan Hubbard has graciously provided an example python extension called `Hello Kit-ty`.  It can be
found on `github.com` at https://github.com/jordanhubbard/hello-kitty and can be cloned from there with:

* `git clone https://github.com/jordanhubbard/hello-kitty`

Once cloned locally, the extension can be loaded in Kit using the `--ext-folder` and `--enable` command
line options:

* `Kit.app/Contents/MacOS/kit --ext-folder <path_to_hello_kitty_repo>/exts --enable omni.hello.kitty`

On startup, the extension should print an ASCII picture of Hello Kitty.  On shutdown, another ASCII
image of Hello Kitty should be printed.


How to Build This On Mac
========================

1. Setup a Mac OS build machine:
  1. Setup a Mac OS machine with Mac OS 11.0 or higher and XCode 12.3 or higher.
  1. Install Homebrew.
  1. Install `bash` from Homebrew and set it as the active shell in `Terminal.app`.
1. Clone the Kit repo locally.
  1. `git clone https://gitlab-master.nvidia.com/omniverse/kit`
  1. Change to the `kit/` directory: `cd kit/kit`.
1. Build Kit for Mac OS with the temporary build script for Mac OS: `./mac_build.sh`.  This script
   also has a `--help` option that displays the usage information and exits.
1. To package a Mac .app for Kit, run `mac_build.sh` with the `--package` option.  This will create
   debug and release .app packages in the `_builtpackages/debug/` and `_builtpackages/release/`
   folders.
1. Run `mac_build.sh` with the `--installer` option to build a .zip archive containing the .app
   packages.  For the moment, building a .pkg installer is not working.
1. Enjoy!
