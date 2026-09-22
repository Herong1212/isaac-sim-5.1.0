.. _omni.usd module:

omni.usd module
############################

Introduction
************

Extension **omni.usd** serves to load and initialize Pixar USD library. It also provides managed UsdContext for easy USD Stage access, and state mangement, which provides both synchronous/asynchronous interfaces in C++ and Python to open/close/attach/save stage, and do state query. It also provides common utilities and undoable commands for wrapped USD operations. **omni.usd** is the foundation component for all other extentions that need to access USD.

API Changes
***********

Since Kit 106.0, old layer interface accessed through **omni.usd.UsdContext.get_layers** is removed which was deprecated since Kit 104.0. In order to
access corresponding APIs, you'd have to refer {py:mod}`omni.kit.usd.layers` for more details.

omni.usd module reference
==========================

.. automodule:: omni.usd
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :imported-members:
    :exclude-members: partial


omni.usd.audio module reference
==================================

.. automodule:: omni.usd.audio
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :imported-members:

.. toctree::
   :maxdepth: 1

   CHANGELOG
