# Kit Services Core

The core of Kit's micro services framework.
Using endpoints and routers, functions can be registered to be used as microservices.

Combining the Core with the various transports (`omni.services.transport.server.*`) available services can be interacted with via the various protocols.

Using facilities (`omni.services.facilities.*`) additional, stateful, functionality can be added to the stateless services.

A reference implementation showing the combination of the core with transports, facilities and service extensions can be found in `omni.kit.controlport`.
