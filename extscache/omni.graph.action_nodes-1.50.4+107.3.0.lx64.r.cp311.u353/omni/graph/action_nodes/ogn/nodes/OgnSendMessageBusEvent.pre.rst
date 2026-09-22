The event can be handled by any message bus listener, or with a corresponding :ref:`OnMessageBusEvent<omni_graph_action_OnMessageBusEvent>` node.

Data from dynamic input attributes will be copied into the event payload, with keys that match the attribute name. Here's an example of handling the event in Python. In this example the sending node has an input "inputs:arg1":

.. code-block:: python

    import carb.events
    import omni.kit.app

    def on_event(event: carb.events.IEvent):
        data = event.payload["arg1"]
        print(f"got data = {data}")

    msg = carb.events.type_from_string("my_event_name")
    message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
    sub = message_bus.create_subscription_to_pop_by_type(msg, on_event)
