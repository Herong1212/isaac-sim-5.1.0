USDRT Python API Reference
==========================

Note: We are currently migrating documentation from a previous location `here <https://docs.omniverse.nvidia.com/kit/docs/usdrt/latest/index.html>`_. Some python and C++ API reference may be missing.

Note that modules show up here in their private namespace,
but they are usable from the public namespace, reflecting USD's API. 
For example, the documentation here reports the class::

    usdrt.Gf._Gf.Vec3d

But it can be used in Python code like:

.. code:: python

    from usdrt import Gf

    vec_up = Gf.Vec3d(0, 1, 0)


Someday I'll figure out how to fix this with Sphinx or in the build,
but today is not that day.


.. toctree::
   :maxdepth: 1

..
    TODO Revisit Gf Vt and Sdf
    usdrt.Gf module
    ---------------
    .. automodule:: usdrt.Gf._Gf
        :platform: Windows-x86_64, Linux-x86_64
        :members:
        :undoc-members:

    usdrt.Vt module
    ---------------
    .. automodule:: usdrt.Vt._Vt
        :platform: Windows-x86_64, Linux-x86_64
        :members:
        :undoc-members:

    usdrt.Sdf module
    ----------------
    .. automodule:: usdrt.Sdf._Sdf
        :platform: Windows-x86_64, Linux-x86_64
        :members:
        :undoc-members:


usdrt.Usd module
----------------
.. automodule:: usdrt.Usd._Usd
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdGeom module
--------------------
.. automodule:: usdrt.UsdGeom._UsdGeom
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.Rt module
---------------
.. automodule:: usdrt.Rt._Rt
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdLux module
-------------------
.. automodule:: usdrt.UsdLux._UsdLux
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdMedia module
---------------------
.. automodule:: usdrt.UsdMedia._UsdMedia
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdRender module
----------------------
.. automodule:: usdrt.UsdRender._UsdRender
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdShade module
---------------------
.. automodule:: usdrt.UsdShade._UsdShade
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdSkel module
--------------------
.. automodule:: usdrt.UsdSkel._UsdSkel
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdUI module
------------------
.. automodule:: usdrt.UsdUI._UsdUI
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdVol module
-------------------
.. automodule:: usdrt.UsdVol._UsdVol
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.UsdPhysics module
-----------------------
.. automodule:: usdrt.UsdPhysics._UsdPhysics
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.PhysxSchema module
-------------------------
.. automodule:: usdrt.PhysxSchema._PhysxSchema
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.ForceFieldSchema module
-----------------------------
.. automodule:: usdrt.ForceFieldSchema._ForceFieldSchema
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens

usdrt.Semantics module
-----------------------------
.. automodule:: usdrt.Semantics._Semantics
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :exclude-members: Tokens
