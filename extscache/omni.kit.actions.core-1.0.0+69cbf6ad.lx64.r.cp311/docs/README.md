# Omni Kit Actions Core Extension

A framework for creating, registering, and discovering actions.


## Actions

Actions are programmable objects that can encapsulate anything which occurs in a fire and forget manner.
- They can be created, registered, discovered, and executed from any extension in C++, Python, or a mix.
- They can be created with associated metadata to aid in their discoverability and/or display in a UI.
- They can be invoked/executed in a single call (although they can accept arbitrary parameters).
- They are not stateful (although their end result may not manifest immediately).
- They do not support undo/redo functionality.


## Action Registry

The Action Registry maintains a collection of all registered actions and allows any extension to:
- Register new actions.
- Deregister existing actions.
- Discover registered actions.
