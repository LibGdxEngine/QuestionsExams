from django import template
from urllib.parse import urlencode

register = template.Library()


@register.filter
def urlencode_except(query_dict, exclude_param):
    """
    Returns URL parameters encoded as a string, excluding the specified parameter.
    """
    mutable_get = query_dict.copy()
    if exclude_param in mutable_get:
        mutable_get.pop(exclude_param)
    return "&" + urlencode(mutable_get) if mutable_get else ""
