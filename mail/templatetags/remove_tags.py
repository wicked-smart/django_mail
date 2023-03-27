from django import template
import re

register = template.Library()

@register.filter
def remove_tags(value):
    ''' remove html tags of the text '''
    return re.sub("<[^<]+?>",'',value[:350])