from django import template

register = template.Library()


@register.filter
def display_username(value):
    # Здесь можно добавить логику для отображения имени с пробелами
    # return value.replace('', ' ')
    return ' '.join(value.split('_'))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_most_voted(choices_with_colors, percentages):
    max_percentage = max(percentages.values())
    for choice, color in choices_with_colors:
        if percentages[choice] == max_percentage:
            return choice


@register.filter
def percentage(value, total):
    if total == 0:
        return 0
    return round((value / total) * 100)


@register.filter
def split(value, delimiter=';'):
    """
    Разделяет строку по указанному разделителю.
    По умолчанию разделитель — точка с запятой.
    """
    return value.split(delimiter)
