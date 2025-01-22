from django import template

register = template.Library()

# Example custom filter
@register.filter(name='my_custom_filter')
def my_custom_filter(value):
    return value.upper()  # Example: converts text to uppercase
