from django import template
from django.conf import settings
from django.template.loader import get_template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.template import loader


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


@register.simple_tag(takes_context=True)
def simple_rating(context, score):
    request = context.get("request")
    if request is None:
        raise Exception(
            'Make sure you have "django.core.context_processors.request" in your templates context processor list'
        )

    star_count = settings.STAR_RATINGS_RANGE
    stars = [i for i in range(1, star_count + 1)]
    template_name = "star_ratings/widget_for_comment.html"
    icon_height = settings.STAR_SIZE_FOR_COMMENT

    if isinstance(score, int) and 1 <= score <= star_count:
        percentage = score / star_count * 100
    else:
        percentage = 0

    return loader.get_template(template_name).render(
        {
            "request": request,
            "stars": stars,
            "star_count": star_count,
            "read_only": True,
            "editable": False,
            "icon_height": icon_height,
            "icon_width": icon_height,
            "sprite_width": icon_height * 3,
            "sprite_image": static("images/stars.png"),
            "percentage": percentage,
            "id": "dsr{}".format(0),
        },
        request=request,
    )
