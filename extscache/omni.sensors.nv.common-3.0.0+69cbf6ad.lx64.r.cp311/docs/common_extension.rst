.. _ext_omni_sensors_nv_common:

Omniverse Common Extension
==========================

Introduction
------------

The Common extension is the one extension that every sensor extension depends on. It provides a set of common functionalities/headers that are used by other extensions.



Plugins
-------


.. _DWPodIO:


IDWPodIO
^^^^^^^^

The ``IDWPodIO`` class is an interface for DW POD file format I/O operations. It writes and reads lidar bin files using the DW POD format.

Methods
"""""""

- ``void init(const DWPodIOConfig& cfg)``
    - Initializes the ``IDWPodIO`` interface with the given configuration.

- ``void dumpPacket(void* packet, const uint64_t packetSize, void* packetHeader, const uint64_t packetHeaderSize, const uint64_t packetTimestampNs)``
    - Writes the given packet to the file.

- ``TimedDataBuffer readNextPacket()``
    - Reads the next DWPod packet with a timestamp.

- ``const DWPodIOConfig& getCfg()``
    - Returns the configuration of the ``IDWPodIO`` interface.

Initialization
""""""""""""""

To get an object of the ``IDWPodIO`` interface, you need to call the ``carb::getFramework()->acquireInterface<omni::sensors::IDWPodIOFactory>()->createInstance()`` function.
To initialize the ``IDWPodIO`` interface, you need to create a ``DWPodIOConfig`` structure and call the ``init`` method.

.. code-block:: python

    import omni.sensors.nv.common._common as common

    pod_cfg = common.DWPodIOConfig()
    pod_cfg.accessType = common.DWPodAccessType.READ
    pod_cfg.fileName = cfg.cfg.fileName
    factory = common.acquire_dwpod_io_interface()
    dwpod_io = factory.createInstance()

    dwpod_io.init(pod_cfg)


DWPodIOConfig
"""""""""""""

The ``DWPodIOConfig`` structure is used to configure the ``IDWPodIO`` interface.


- ``DWPodAccessType accessType``
    - The access type for the ``IDWPodIO`` interface. Default is ``DWPodAccessType::WRITE``.

- ``TimedDataBuffer trackHeaderDataBuffer``
    - The track data header for the file.

- ``omni::string fileName``
    - The name of the file. Default is an empty string.

- ``int desiredTrackId``
    - Specifies which track to read from the file. Default is ``1``.


DWPodAccessType
"""""""""""""""

The ``DWPodAccessType`` enumeration specifies whether the ``DWPodIOConfig`` is reading or writing to a file.


- ``READ``
    - The access type for the ``DWPodIOConfig`` for file reading.

- ``WRITE``
    - The access type for the ``DWPodIOConfig`` for file writing.


TimedDataBuffer
"""""""""""""""

The ``TimedDataBuffer`` contains the raw data and the timestamp of the buffer.


- ``int64_t timestampNs``
    - The timestamp of the data buffer in nanoseconds.

- ``omni::vector<uint8_t> dataBuffer``
    - The raw data buffer.


.. _ProfileReader:

IProfileReader
^^^^^^^^^^^^^^

The IProfileReader reads the parameter of the modality specific profile from a JSON file.
The code below details how to instantiate the IProfileReader interface

.. code-block:: python

    import omni.sensors.nv.common._common as common

    profilefactory = common.acquire_profile_reader_interface()

Users can create objects that implement this interface by acquiring the ``IProfileReader`` carbonite interface and using the ``acquire_profile_reader_interface()`` method.

Instantiation
"""""""""""""

To instantiate the IProfileReader the user needs to acquire the carbonite IProfileReaderFactory interface through the python bindings interface::

  profilefactory = common.acquire_profile_reader_interface()

Initialization
""""""""""""""

The user has to initialize the profile reader with the JSON string

.. code-block:: python

    import omni.sensors.nv.common._common as common

    profilefactory = common.acquire_profile_reader_interface()
    reader = profilefactory.createInstance()
    reader.init(data, common.ProfileType.LIDAR)

The supprted profile types are: LIDAR, RADAR, USS, IDS (and variants)

Filling a Profile object
""""""""""""""""""""""""

The user can get the data size object of the profile (for data dependent sizes, e.g, for LIDAR) and has to allocate the memory for the profile objectId
before the profile reader can fill the profile object

.. code-block:: python

    import omni.sensors.nv.common._common as common

    profilefactory = common.acquire_profile_reader_interface()

    with open(profilfilename, "r") as file:
        data = file.read()
        reader = profilefactory.createInstance()
        reader.init(data, common.ProfileType.LIDAR)
        data_size = reader.dataSizeProfile()
        byte_array = bytearray(data_size)
        reader.update(byte_array)
        profile = lidar.getLidarProfileFromBuffer(byte_array)


Python Bindings
---------------

The common extension provides a multitude of python bindings, e.g., for the ``IProfileReader`` and ``IDWPodIO`` interfaces.
