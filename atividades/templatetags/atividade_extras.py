from django import template

register = template.Library()

@register.filter
def categoria_horas(atividades, categoria):
    horas = sum(a.horas_aprovadas or 0 for a in atividades if a.categoria == categoria)
    return f"{horas}h"
