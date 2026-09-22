{%- if definition.mapping -%}
{{ definition.name }} = Dict[{{ definition.mapping.key|py.type_name }}, {{ definition.mapping.value|py.type }}]

{%- else -%}
class {{ definition.name }}{% if definition.extends %}({{ definition.extends }}){% else %}(Record){% endif %}:
    {%- for field in definition.fields %}
    {{ field.name }}: {{ field|py.type }}{% if field.is_const %} = {{ spec.resolve_name(field.type) }}{% endif %}
    {%- else %}
    pass
    {%- endfor %}

{% endif -%}