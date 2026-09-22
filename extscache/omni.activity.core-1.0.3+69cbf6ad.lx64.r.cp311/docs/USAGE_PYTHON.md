# Python Usage Examples

## work with activity core

Here is an example showing using omni.activity.core APIs to pump began and ended typed activity events, and also how to subscribe callbacks when activity event dispatching on the stream.

```python
import omni.activity.core as act

def callback(node: act.INode):
    child = node.get_child(0)

    began = child.get_event(0)
    ended = child.get_event(1)

    # the begin progress as 0.0
    print(f"{began.payload["progress"]}")
    # the end progress as 1.0
    print(f"{ended.payload["progress"]}")

# create callback when activity event dispatching on the stream
id = act.get_instance().create_callback_to_pop(callback)

# enable activity core
act.enable()
# activity "Test" with child "SubTest" starts with payload of progress as 0.0
act.began("Test|SubTest", progress=0.0)
# activity "Test" with child "SubTest" ends with payload of progress as 1.0
act.ended("Test|SubTest", progress=1.0)
# disable activity core
act.disable()

# process the activity callback
act.get_instance().pump()

# remove created callback
act.get_instance().remove_callback(id)

```
