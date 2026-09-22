{%- set generation = namespace(last={"type": "struct"}) -%}
{%- for definition in types -%}
{%- if definition.type == "enum" %}
{%- if generation.last.type not in ["struct", "enum"] or (generation.last.type == "struct" and generation.last.mapping) -%}
{%- raw %}

{% endraw -%}
{%- endif %}
class {{ definition.name }}(metaclass=Enum):
    {%- for member in definition.members %}
    {{ member.name }} = {{ member.value }}
    {%- endfor %}

{% elif definition.type == "const" %}
{{ definition.name }} = {{ definition.value }}
{%- elif definition.type == "alias" %}
{{ definition.name }} = {{ definition.value|py.type_name }}
{%- elif definition.type == "union" %}
{{ definition.name }} = Union[{{ ", ".join(definition['members']|map('py.type_name')) }}]
{%- elif definition.type == "struct" -%}
{%- if generation.last.type not in ["struct", "enum"] or (generation.last.type == "struct" and generation.last.mapping) -%}
{%- raw %}

{% endraw -%}
{%- endif %}
{% include "struct.pyi" %}
{%- elif definition.type == "custom" %}
{% include "custom/" + definition.schema + ".txt" %}
{%- endif -%}
{%- set generation.last = definition -%}
{%- endfor %}