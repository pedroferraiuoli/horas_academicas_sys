from django import template

register = template.Library()

@register.filter
def categoria_horas(atividades, categoria):
    horas = sum(a.horas for a in atividades if a.categoria == categoria)
    return f"{horas}h"
