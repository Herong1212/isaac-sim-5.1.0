
Here's an example of sending a kit application message bus event:

.. code-block:: python

    import carb.events
    import omni.kit.app

    msg = carb.events.type_from_string("my_event_name")
    omni.kit.app.get_app().get_message_bus_event_stream().push(msg, payload={ "arg1": 42 })

The event payload data will be copied in to matching dynamic output attributes if they exist.
In the previous example, 42 would be copied to outputs:arg1 if possible. :ref:`SendMessageBusEvent<omni_graph_action_SendMessageBusEvent>` is related.
