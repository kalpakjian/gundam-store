from django import template

register = template.Library()


@register.filter
def sum_items_price(items):
    """計算購物車所有項目的總金額，考慮折扣價"""
    return sum(item.get_subtotal() for item in items)


@register.filter
def currency(value):
    """統一價格格式：HK$1,234.00"""
    if value is None:
        return ''
    try:
        return f"HK${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)