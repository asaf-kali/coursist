from django import template
from django.conf import settings
from django.template.loader import get_template
from django.utils.safestring import mark_safe

register = template.Library()


class AssignNode(template.Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, context):
        context[self.name] = getattr(settings, self.value.resolve(context, True), "")
        return ""


@register.tag("get_settings_value")
def do_assign(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(f"'{bits[0]}' tag takes two arguments")
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)


@register.simple_tag
def raw_include(name: str):
    try:
        path = get_template(name).template.origin.name
    except Exception as e:
        return ""
    with open(path) as file:
        output = file.read()
    return mark_safe(output)
