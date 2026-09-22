from typing import AsyncIterator, Dict, List, Optional

from idl.connection.transport import Client
from idl.types import Literal, Record

from .data import *

{% for interface in interfaces.values() %}
class {{ interface.name }}:
    {%- for field in interface.fields %}
    {% if not field.is_const %}{{ field.name }}: {{ field|py.type }}{% endif %}
    {%- endfor %}
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> '{{ interface.name }}':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    {% for function in interface.functions %}
    async def {{ function.name|underscore }}(self, {{ function.params|py.arguments(default="None", interface=interface) }}) -> {% if function.returns.is_many %}AsyncIterator[{{ function.returns.type|py.type_name }}]{% else %}{{ function.returns.type|py.type_name }}{% endif %}:
        """
        {{ function.comment|format_doc(indent=8) }}
        """
        {{ function.params|py.request_data(variable="_request", interface=interface, default="None") }}
        {%- if function.returns.is_many %}
        agen = self.transport.call_many("{{ interface.name }}", "{{ function.name }}", _request, request_type={{ function.name|py.request_record_name(interface.name) }}, return_type={{ function.returns.type|py.type_name }})
        try:
            async for _response in agen:
                yield _response
        finally:
            await agen.aclose()
        {%- else %}
        _response = await self.transport.call("{{ interface.name }}", "{{ function.name }}", _request, request_type={{ function.name|py.request_record_name(interface.name) }}, return_type={{ function.returns.type|py.type_name }})
        return _response
        {%- endif %}
    {% endfor %}
    __interface_name__ = "{{ interface.name }}"
    __interface_origin__ = "{{ spec.origin }}"
    {%- set capabilities = interface.name|capabilities.find(side="client") -%}
    {% if capabilities %}
    __interface_capabilities__ = {{ capabilities.name }}
    {%- endif %}
{%- if not loop.last %}
    {% raw %}


    {%- endraw %}
{% endif %}
{%- endfor %}

{% for interface in interfaces.values() %}
{%- for function in interface.functions %}
{%- set definition = function|py.request_record(interface) %}
{% include "struct.pyi" %}
{%- endfor %}
{%- endfor %}
