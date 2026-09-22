.. _OmniPvd:

==================================================================================
OmniPVD - PhysX Visual Debugger
==================================================================================

Omniverse PhysX Visual Debugger (OmniPVD) allows the recording of data of a PhysX simulation for later visual and quantitative inspection. For example, you can record a rigid body box falling onto a ground plane, then replay the recording and inspect the motion of the box frame-by-frame to spot simulation issues. Besides the body transforms, the recording contains further simulation data, such as the values of the linear and angular velocity of the box at each frame.

OmniPVD consist of a shared dynamic library and the :ref:`Omni PhysX Visual Debugger` extension. The shared dynamic library is used both by the PhysX SDK simulation engine for the recording and writing of OmniPVD binary files (OVD) and by the OmniPVD extension to read and parse OVD files.

The OmniPVD extension makes it possible to import or load a PhysX recording in OVD format, transforming it seamlessly into a cached USDA format. After the OVD file is imported you can time scrub and analyze it as a USD Stage, which is good for debugging, inspecting, and visualizing a recorded PhysX scene, but it stays a pure animation. The OmniPVD gizmos can then be applied to the imported OVD file, for the sake of different visualizations such as collision contacts, bounding box representations, velocities as well as seeing mass, and transform reference frames.

It has a dedicated timeline that is geared towards replaying simulation steps and inspecting them more precisely. Use the OVD timeline instead of the alternatives because it allows for inspection of pre- and post-simulation frames.

Loading the OmniPVD Extension
----------------------------------------------------------------------------------

The :ref:`Omni PhysX Visual Debugger` extension can be found in the extension browser by searching for "pvd". Make sure to click on the slider **ENABLED**, to move it into its rightmost position shown as green, to have it be activated and visible.

    .. image:: images/load_extension_from_browser.png
        :align: center
        :alt: Show OmniPhysics Debug Window

Recording a PhysX Simulation from the OmniPhysics Debug Window
----------------------------------------------------------------------------------

To record a PhysX scene in the OVD format:

1. Make sure that the **OmniPhysics Debug** window is enabled and visible or that the OmniPVD extension window is visible, as will be discussed below. This can be done by going into the menu **Window > Physics > Debug** window and making sure it is marked checked.

    .. image:: images/physics_debug_window_show.png
        :align: center
        :alt: Show Physics Debug Window

2. Then in the **Physics Debug** window in the OmniPVD section, check **Recording Enabled**.

    .. image:: images/omniphysics_record_enabled_full_bbox.png
        :align: center
        :alt: OmniPVD Enabled

3. Just underneath is a button called **Set Recording Directory**, which allows you to navigate to the desired OVD recording directory where time stamped OVD recordings will be saved. 

    .. image:: images/omniphysics_select_directory_colored_bbox.png
        :align: center
        :alt: OmniPVD Recording Directory

4. By opening the directory of choice and by pressing **Select Current**, the OVD output directory is updated and set. Each time the Physics simulation is started and stopped, a new OVD recording is saved and time stamped into this directory as an ``.ovd`` recording.
5. If the checkbox **Recording Enabled** is checked and enabled (not grayed out), as soon as the **Play** button is pressed, PhysX is now recording OmniPVD time stamped files into the OVD recording directory.

    If the USD Stage is an OmniPVD Stage (it has OmniPVD prims) the checkbox "Recording Enabled" is grayed out, as it's not possible to record any simulation data from an OmniPVD Prim, because it remains an animation.

    .. image:: images/omniphysics_record_enabled_grayed_bbox.png
        :align: center
        :alt: Recording Grayed out

Recording a Physics Simulation from the OmniPVD Window
----------------------------------------------------------------------------------

As was shown above you can record a physics scene from the **Physics Debug** window, but it's also possible to do it from the OmniPVD extension:

1. Select "**Recording Enabled**. For example:

    .. image:: images/ovd_recording_menu_enabled.png
        :align: center
        :alt: Enable Recording

2. Select the recording directory using **Set Recording Directory**. 

    .. image:: images/ovd_recording_menu_setting_directory.png
        :align: center
        :alt: Set Recording Directory

Enabling OmniPVD Recordings from the Command Line for a Headless Session
----------------------------------------------------------------------------------

If you need to record a PhysX simulation into OVD from a headless session:

1. You can enable OmniPVD recording from the command line using the following settings:

    .. code-block::

        /persistent/physics/omniPvdOvdRecordingDirectory
        /physics/omniPvdOutputEnabled

   An example console command line, from Linux and not complete because the Stage is not defined:

    .. code-block::    

        bash kit/omni.app.dev.sh --no-window --/windowless=True --/persistent/physics/omniPvdOvdRecordingDirectory=/tmp/ --/physics/omniPvdOutputEnabled=true 

   The order of the settings is important:   
    1. Set the output directory.
    2. Enable the OVD output. If this order is not followed, the OVD recording will try to be written into a predefined directory, which might not exist. The writing operation will not crash but it will produce an error.


2. It is not required to load the OmniPVD extension to do recordings, but make sure to have the :ref:`ext_omni_physx` extension loaded and do the recording from there. The OmniPVD extension is only necessary to import the produced OVD file.

Enabling OmniPVD Recordings from the Command Line for a Headless RL Session in IsaacLab
----------------------------------------------------------------------------------

IsaacLab users can record into OVD files with a special command line argument : --kit_args

    .. code-block::

        ./isaaclab.sh -p scripts/demos/bipeds.py --kit_args "--/persistent/physics/omniPvdOvdRecordingDirectory=/tmp/ --/physics/omniPvdOutputEnabled=true" --headless

Please also see
    https://isaac-sim.github.io/IsaacLab/main/source/refs/troubleshooting.html#debugging-physics-simulation-stability-issues

Enabling OmniPVD Recordings via Python
----------------------------------------------------------------------------------

You can enable recording in a Python script. This might look like::

    settings_ = carb.settings.get_settings()
    settings_.set("/persistent/physics/omniPvdOvdRecordingDirectory", "/tmp/pvdout2/")
    settings_.set("/physics/omniPvdOutputEnabled", True)

The order that you apply the settings is important. The same order as the console command, above, applies. The recording directory must be set first and then you can enable the output. You do not have to import the OmniPVD extension in the script to do OVD recordings. However, you must make sure to have the :ref:`ext_omni_physx` extension imported.
    
OVD Recording File Name Structure
----------------------------------------------------------------------------------

In the OmniPVD recording settings, the OVD file names will be based on a time stamp and end in a file type of ``ovd``. 

The timestamp in the file name ensures that newer recordings do not overwrite older recordings.

If a duplicated timestamp does occur, there is a safety mechanism to ensure file names stay unique.

Loading an OVD File from the OmniPVD Window
----------------------------------------------------------------------------------

After a PhysX simulation is recorded into a time stamped OVD file, you can import or load it. 

The loading operation automatically looks for a cached version of a corresponding USD Stage (in the Cache directory) and loads that if it exists. 

You can now explore the USD Stage of the imported OVD file, inspecting the recorded motion and data: 

* To import the latest OVD file in the import directory, press the **Load Latest** button in the file browser.
* To load a specific file, see the next section on loading a file using the file import menu.

    .. image:: images/ovd_load_menu_latest.png
        :align: center
        :alt: OVD Load Latest

* To change the directory from where to load the latest OVD file from, click **Set Import Directory**.

    .. image:: images/ovd_load_menu_set_import.png
        :align: center
        :alt: OVD Set Import Directory

* To override the up axis for the USD Stage that is automatically derived from the PhysX gravity vector, use the drop down menu for the Y or Z axis.

    .. image:: images/ovd_load_menu_set_axis.png
        :align: center
        :alt: OVD Import OVD Up Axis

* To set the cache directory where the USD Stages are stored, which are created on loading an OVD file, click **Set Cache Directory**. The next time the same OVD file is loaded, the USD Stage is directly loaded from there.

    .. image:: images/ovd_load_menu_set_cache.png
        :align: center
        :alt: OVD Set Cache Directory

Loading an OVD File from the File Import Menu
----------------------------------------------------------------------------------

To load or import an OVD file from the menu:

1. Navigate to **File > Import**, which opens up a file explorer dialog window. 
2. Navigate to a specific file.

    .. image:: images/file_import_menu.png
        :align: center
        :alt: File Import Menu

3. Double click or press the **Import** button in the explorer window to import the OVD file.

    .. image:: images/file_import_select.png
        :align: center
        :alt: File Import Selection

Dedicated Timeline
----------------------------------------------------------------------------------

A recent addition to OmniPVD is the dedicated timeline, while similar to other USD animation timelines, it works specifically on PhysX simulation steps in OVD files. The PhysX simulation steps can be divided into two frames, namely pre-simulation and post-simulation. 

* The **pre-simulation** frame covers PhysX user calls, such as adding a PxActor to a PxScene, various set operations, and collisions. 
* The **post-simulation** frame covers transforms, velocities, and any other parameters that were updated on PhysX objects. 
 
Being able to inspect the simulation steps into two distinct and precise frames is valuable. For example in root cause analysis, knowing if user data was somehow out of bounds or ill defined can help you fix the issue.

The timeline allows you to inspect the simulation in three modes, which are **post-sim**, **pre-sim**, and **pre-sim + post-sim**. The different modes allows you to inspect a specific type of frame or a mixed frame. They are listed in this order because post-sim is the default. Post-sim allows you to inspect all operations that happened up to and including the post-simulation step, therefore having the view of all operations that happened in a simulation step.

    .. image:: images/timeline_drop_down.png
        :align: center
        :alt: Drop down simulation replay mode

At any time you can determine the type of simulation frame you are in by inspecting the **Pre** or **Post** button. The button functions both as an indicator and as a switch from one mode to the other. 

.. _pre_sim_frame_type_ref:
.. Note:: Contact gizmos are only visualized for **pre-sim** frames. Make sure to be either in **pre-sim** or **pre-sim + post-sim** frame mode. You can also temporarily flip the frame mode to the **Pre** mode, by clicking on frame type button which shows as **Pre** or **Post** as below.

Independent of the simulation replay mode that you have selected, you can at any time use the **Pre** or **Post** button to switch back and forth between the frame types in a simulation step. For example, if you are in the pre-sim mode but momentarily want to inspect the post-simulation frame of the simulation step.  

    .. image:: images/timeline_pre_post.png
        :align: center
        :alt: Pre post simulation switch/indicator

The **timeline scrubber** field allows you to drag the mouse to change the simulation step or frame. If the mode is pre or post, the scrubber moves in increments of a full simulation step. If it's in pre+post mode, then the scrubbing can be adjusted to any pre- and post-simulation frame. The **timeline scrubber** field is highlighted below:

    .. image:: images/timeline_scrubber.png
        :align: center
        :alt: The timeline scrubber

A timeline must also be able to playback an OVD recording. To playback the OVD recording there is the
**play** button. The **play** button becomes a pause button as soon as the OVD recording is being played back. During play mode, the timeline shows each simulation frame. If the play mode is engaged, after the OVD recording reaches the end, pressing the play button again, moves the frame to the first one. See the play button placement below:

    .. image:: images/timeline_play.png
        :align: center
        :alt: The play button

The **wait time** indicator/input button, is used to set the milliseconds to wait in between simulation steps or frames during the play mode. For example, if you input 50, then the timeline will wait 50 milliseconds before advancing to the next frame. It will not skip frames if the frame takes longer to load and display. The frame will take as long as it needs to load and display, then the timeline will wait the indicated amount of milliseconds, before proceeding to the next frame. No frames are skipped, however, if the mode is pre or post, only pre or post simulation frames will be played back.

    .. image:: images/timeline_replay_speed.png
        :align: center
        :alt: The replay speed
    
There is also the option to advance precisely one simulation step or frame (if the replay mode is **pre+post**), in the backwards direction or the forward direction by using the **previous frame** or **next frame** buttons. This is good for when you want to know exactly when a parameter changed. For example, inspecting a simulation frame by frame.

    .. image:: images/timeline_prev_next.png
        :align: center
        :alt: The next/prev buttons

To indicate the simulation step you are in, as well as to give the option to jump to a specific frame, there is a step indicator/input button. You can input the step value with an integer (using the keyboard). The value also changes depending on the scrubbed value or if the play state is initiated. 

It will not show an increase or decrease if you change the Pre/Post frame because the simulation step stays the same.

    .. image:: images/timeline_sim_step.png
        :align: center
        :alt: The sim step button
    
If you ARE interested in going to the start or the end of the OVD recording you can use the **first** or **last** buttons.

    .. image:: images/timeline_first_last.png
        :align: center
        :alt: The first/last buttons

Object Tree and Property Widget
----------------------------------------------------------------------------------

The **Object Tree** features include:

Objects can have names derived from the OmniPVD object name (a string set at the object creation call), a PhysX actor name, or a combination of the OmniPVD class name and a unique identifier. 
The names do not have to be displayed with the USD Prim names (which have to follow strict SDF path rules).

Objects have the OmniPVD class displayed in the class column, not the USD Prim type.

The **Object Tree search** bar differs from the USD Stage search bar in the following ways:

- The search bar expands the matching objects (based on their OVDTree name and UID) and allows for iterating through the results using the **Prev/Next** buttons. Results are not displayed in a flat list.
- It's possible to collapse the view and only display the root objects in the tree. 
  
Every search result expands the existing expansion of the OVD Tree elements. For example, if you found something with a certain search string and then you found something else, both these searches (and any upcoming ones) are added to the expansions.

When an OVD file is imported, a cached Stage file is created. The USD hierarchy in the resulting file starts of with a scene, then lists the different object classes that have populated each scene. For example object classes include dynamic rigid bodies, static rigid bodies, and articulations. 
 
For each body, there is an actor or articulation link with accompanying shapes and geometries. Each USD Prim has a set of custom USD attributes, which can be explored in detail and if they change over time, can be scrubbed through the animation to see how they are updated.

    .. image:: images/stage.png
        :align: center
        :alt: OmniPVD USD Stage

Another view of the Stage is in the OmniPVD Object Tree.

A Unique Identifier (UID) is prepended to all the objects, which is connected to the moment an object was created. It follows the creation/removal of objects, so only the objects that are active in the PhysX engine at that specific frame (defined by the timeline interface scrubber) are displayed in the tree. This is to have a more precise visualization of what was actually simulated in the frame.

Selection in the viewport selects the Prim geometries, but makes sure that the selection affects the owning PhysX classes that are above the geometries in the OVD Tree. This is to make sure that selection is a smooth and intuitive operation and does not break the existing interaction paradigm of the USD Stage.

    .. image:: images/ovd_tree_hierarchy.png
        :align: center
        :alt: OmniPVD OVD Tree Hierarchy

You can also search in the names of the OmniPVD objects or the UID and you get the resulting searches expanded and colored, with the possibility to walk through the results using the **Next** and **Prev** buttons. If you have done many searches, each search continues to expand the nodes, which can result in the expansion of all nodes. The **Collapse All** button collapses all expanded nodes of the tree.

.. Note:: The search bar in the USD Stage only allows for search in the Prim path and Prim name.

    .. image:: images/ovd_tree_search.png
        :align: center
        :alt: OmniPVD OVD Tree Search

Below the **Object Tree**, is the **Property** window and inside the Physics widget lives the **OmniPVD Property widget**, which displays the OmniPVD attributes in a pretty printed form. The attributes in the widget get updated with the timeline changes in the USD Stage.

    .. image:: images/ovd_properties.png
        :align: center
        :alt: OmniPVD OVD Properties

Object Hierarchies, Attributes and Units in OmniPVD are Based on PhysX
----------------------------------------------------------------------------------

In the above section on the **Object Tree** you can see how OmniPVD displays object hierarchies, attributes, names and units which are a reflection of the recorded underlying PhysX simulation stream.

There might be objects that are only present in the OVD recorded PhysX stream, that have no direct mapping to for example the OmniPhysics USD Schema classes and structures.

Visualization Gizmos
----------------------------------------------------------------------------------

The gizmos sub-window is located below the OmniPVD recording sub-window in the OmniPVD tab.

There are several ways to augment the imported OVD file with OmniPVD gizmos. The gizmos are typically set to **None**, **All**, or **Selected** from the menu below. The drop down menus with the scaling values attached, allows you to scale each type of gizmo either independently and as a group. In the following, the velocity gizmos are set to **Selected** and their individual scale to 0.2 while the grouped scale is 3.8, leading to a combined scaled of 3.8 x 0.2 for the velocities.

    .. image:: images/gizmos_menu.png
        :align: center
        :alt: OmniPVD Gizmos Menu

Selection is multi-directional between the viewport, the Stage, and the OmniPVD Object Tree. Selection can be done from the viewport, which also ends up selecting them in the Stage and OmniPVD Object Tree windows. 

It's for example possible to see bounding boxes, which are the same axis aligned bounding boxes, that PhysX uses internally to delineate the actors.

    .. image:: images/gizmos_selection.png
        :align: center
        :alt: OmniPVD Gizmos Selection

The contacts with the reference frame along with the mass reference frame are shown for the selected actors below. 

    .. Note:: If the contacts don't show up you might not be in the correct simulation frame mode, see :ref:`Pre-Simulation Frame Type <pre_sim_frame_type_ref>`

    .. image:: images/gizmos_contacts.png
        :align: center
        :alt: OmniPVD Gizmos Contacts

You can also view joints (such as D6, distance, gear, prismatic, rack and pinion). For example, this rope made out of D6 joints:

    .. image:: images/gizmos_joints_d6_ropes.png
        :align: center
        :alt: OmniPVD Gizmos D6 rope

Or this distance joint:

    .. image:: images/gizmos_joints_distance.png
        :align: center
        :alt: OmniPVD Gizmos Distance Joint

Or this gear joint:

    .. image:: images/gizmos_joints_gear.png
        :align: center
        :alt: OmniPVD Gizmos Gear Joint

Or this spherical joint:

    .. image:: images/gizmos_joints_spherical.PNG
        :align: center
        :alt: OmniPVD Gizmos Spherical Joint

Using these gizmos you increase the ability to drill down into debug data.

Overlaying an OmniPVD OVD File onto a USD Stage - Physics Baking
----------------------------------------------------------------------------------

This feature is deprecated although still functional.

    .. image:: images/ovd_physx_baking.png
        :align: center
        :alt: OmniPVD PhysX Baking

OVD Messages
----------------------------------------------------------------------------------

The OmniPVD API allows users to send messages inside of the object and attribute stream. These messages can contain arbitrary information strings, file name, line number and type. They are displayed in the "OVD Messages" tab and using the "Frame" button you can move the timeline to the frame where the error occurred.

    .. image:: images/ovd_messages.png
        :align: center
        :alt: OVD Messages tab

OmniPVD Known Limitations
----------------------------------------------------------------------------------

At the moment, recording of simulation runs starts as soon as the simulation starts, meaning there is no way to delay, pause, or start the recording from a specific frame or simulation time. The recording starts when the simulation starts and stops when the simulation stops.

The recording system is constrained to write OVD files to disk, which must then be imported by the Omniverse OmniPVD extension for visualization. There is currently no live streaming of the OVD data as it's being produced.

Data that is set via the Direct GPU API is recorded. Simulation results, when running with Direct GPU API enabled, are recorded also. Note that this comes with a performance penalty.

PhysX tendons and deformables are currently not supported.

Regarding collision visualization, the contact forces are not displayed with gizmos.