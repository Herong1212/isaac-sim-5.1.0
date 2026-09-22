omni.client
###########

Omniverse Client Library



Python Module
***************

Introduction
==============

Most functions come in 3 flavors:

    * (**preferred**) asynchronous using async/await syntax, e.g. :func:`omni.client.list_async`
    * asynchronous with callback (**Callback is called from other thread**), e.g. :func:`omni.client.list_with_callback`
    * synchronous/blocking, e.g. :func:`omni.client.list`

Example:

.. code:: python

    import omni.client
    import asyncio

    async def task():
        (result, entries) = await omni.client.list_async("omniverse://ov-sandbox/Users")
        print(result) # omni.client.Result.OK)
        for entry in entries:
            print(entry) # __str__ is supported

    asyncio.ensure_future(task())

.. toctree::
   :maxdepth: 1

   CHANGELOG

For more example look into `omni.client` tests (:mod:`omni.client.tests`).

API Reference
==============

.. automodule:: omni.client
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :imported-members:
    :show-inheritance:
    :exclude-members: Tuple, Callable
