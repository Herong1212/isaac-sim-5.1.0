.. _omni_anim_Timeline_2:

.. _omni_anim_Timeline:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Timeline
    :keywords: lang-en omnigraph node animation anim timeline


Timeline
========

.. <description>

Timeline Node is a node that lets you create animation curve(s), plays back and samples the value(s) along its time to output values.

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.timeline<ext_omni_anim_timeline>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Framerate (*inputs:framerate*)", "``double``", "Playback frame rate", "24.0"
    "Length (*inputs:length*)", "``double``", "Duration of the Timeline node in seconds", "10.0"
    "Loop (*inputs:loop*)", "``bool``", "Whether animation should loop when reaches the end (or beginning if playing backwards)", "False"
    "New Time (*inputs:newTime*)", "``double``", "New time to set then ""Set New Time"" is triggered", "0.0"
    "Play (*inputs:play*)", "``execution``", "Play the timeline from current time", "None"
    "Play from Start (*inputs:playFromStart*)", "``execution``", "Play the timeline from start", "None"
    "Reverse (*inputs:reverse*)", "``execution``", "Play the timeline backwards from current time", "None"
    "Reverse from End (*inputs:reverseFromEnd*)", "``execution``", "Play the timeline backwards from end", "None"
    "Set New Time (*inputs:setNewTime*)", "``execution``", "Set timeline to new time defined in ""New Time"" input", "None"
    "Stop (*inputs:stop*)", "``execution``", "Stop playback at current time", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Finished (*outputs:finished*)", "``execution``", "The Timeline node has finished the playback", "None"
    "Updated (*outputs:updated*)", "``execution``", "The Timeline node is ticked and output value(s) resampled and updated", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.Timeline"
    "Version", "2"
    "Extension", "omni.anim.timeline"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Timeline"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "OgnTimelineDatabase"
    "Python Module", "omni.anim.timeline"

